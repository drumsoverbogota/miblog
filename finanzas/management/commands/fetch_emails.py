from datetime import datetime
import sys
import bs4

from django.core.management.base import BaseCommand

import imaplib
import email
import re

from finanzas.models import RegexRule
from finanzas.models import Transaction
from finanzas.models import EmailSource

from blog.settings import GMAIL_USER
from blog.settings import GMAIL_PASSWORD



class Command(BaseCommand):

    help = "Fetch bank transactions from email"

    def handle(self, *args, **kwargs):

        mail = imaplib.IMAP4_SSL("imap.gmail.com")

        try:
            mail.login(
                GMAIL_USER,
                GMAIL_PASSWORD
            )
        except imaplib.IMAP4.error:
            self.stdout.write(
                self.style.ERROR("LOGIN FAILED!!! ")
            )

        mail.select("inbox")

        email_from = EmailSource.objects.filter(
            active=True
        )

        regex_rules = RegexRule.objects.filter(
            active=True,
            source__in=email_from
        )

        for source in email_from:

            status, messages = mail.search(
                None,
                f'(SINCE 01-Jan-2026 UNSEEN FROM "{source.sender_email}")'
            )

            email_ids = messages[0].split()

            for email_id in email_ids:

                processed = False

                status, msg_data = mail.fetch(
                    email_id,
                    "(RFC822)"
                )

                raw_email = msg_data[0][1]

                msg = email.message_from_bytes(raw_email)

                body = self.get_body(msg)

                for rule in regex_rules:

                    regex = rule.regex

                    parsed = self.parse_transaction(body, rule)

                    if parsed:
                        
                        user = source.user

                        Transaction.objects.create(
                            status="pending",
                            source=source,
                            raw_text=body,
                            amount=parsed["amount"],
                            merchant=parsed["merchant"],
                            account_from=parsed["account_from"],
                            account_to=parsed["account_to"],
                            matched_rule=rule,
                            date=parsed["date"],
                            user=user,
                        )

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Saved transaction: {parsed}"
                            )
                        )
                        processed = True
                        break
                
                if not processed:
                    Transaction.objects.create(
                        status="need_review",
                        source=source,
                        raw_text=body,
                        date=datetime.now(),
                        user=source.user,
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f"Email did not match any rule and was marked for review: {body[:50]}..."
                        )
                    )
                

    def get_body(self, msg):

        if msg.is_multipart():
            print("Email is multipart, iterating through parts...")

            for part in msg.walk():

                content_type = part.get_content_type()

                if content_type == "text/plain" or content_type == "text/html":
                    print(f"Found {content_type} part, decoding...")
                    body_decoded = part.get_payload(
                        decode=True
                    ).decode()
                    body_decoded = body_decoded.replace('\r\n', ' ')  # normalize newlines
                    body_decoded = body_decoded.replace('\n', ' ')
                    return body_decoded
                
                else:
                    body_decoded = part.get_payload(
                        decode=True
                    )
                    print(f"Found non-text part, decoded content: {body_decoded}")
        else:
            print("Email is not multipart, decoding payload directly...")
            body_decoded = msg.get_payload(
                decode=True
            ).decode(
                errors="ignore"
            )

            print(f"Decoded body: {body_decoded}")

            payload = msg.get_payload(decode=True)
            if payload is None:
                self.stdout.write(
                    self.style.WARNING(
                        "Payload is None, cannot decode."
                    )
                )
                return ""

            return body_decoded

    def parse_transaction(self, text, rule):

        if rule.remove_html_tags:
            text = bs4.BeautifulSoup(text, "html.parser").get_text(separator=" ")
            # Convert NBSP to normal spaces
            text = text.replace("\xa0", " ")

            # Collapse repeated whitespace
            text = re.sub(r"\s+", " ", text).strip()
            print(f"Removed HTML tags, new text:")
            print("-----------------------------")
            print(repr(text))
            print("-----------------------------")
            print(f"Applying regex: {rule.regex}")

        match = re.search(rule.regex, text)
        print(f"Regex search result for rule {rule.name}: {match}")


        if not match:
            print(f"No match found for rule {rule.name}")
            return None

        amount = match.group(rule.amount_group)

        amount = self.normalize_amount(amount)
        
        date = match.group(rule.date_group) if rule.date_group else None
        time = match.group(rule.time_group) if rule.time_group else None

        if date:
            if rule.date_format == "%d/%m/%Y":
                year = date.split("/")[-1]
                if len(year) == 2:
                    date = date[:-2] + "20" + year

        try:
            print(f"Parsing date and time with rule {rule.name}: date='{date}', time='{time}'")
            if date and time:
                date_time_str = f"{date} {time}"
                date_time_obj = datetime.strptime(date_time_str, rule.date_format + " " + rule.time_format)
            elif date:
                date_time_obj = datetime.strptime(date, rule.date_format)
            else:
                date_time_obj = datetime.now()
        except ValueError as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Date parsing error for rule {rule.name}: {e}"
                )
            )
            self.stdout.write(
                self.style.ERROR(
                    f"Offending text: {text}"
                )
            )
            sys.exit(1)

        transacttion = {
            "amount": amount,
            "merchant": match.group(rule.merchant_group) if rule.merchant_group else "",
            "account_from": match.group(rule.account_from_group) if rule.account_from_group else "",
            "account_to": match.group(rule.account_to_group) if rule.account_to_group else "",
            "date": date_time_obj,
        }

        self.stdout.write(
            self.style.SUCCESS(
                f"Parsed transaction for rule {rule.name}: {transacttion}"
            )
        )
        return transacttion
    
    def normalize_amount(self, value):
        print(f"Normalizing amount: {value}")
        if "." in value and "," in value:
            if value.rfind(".") > value.rfind(","):
                # 9,500.00
                value = value.replace(",", "")
            else:
                # 9.500,00
                value = value.replace(".", "").replace(",", ".")
        elif "," in value:
            # 1,000,000
            value = value.replace(",", "")
        return float(value)
