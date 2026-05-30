from django.views.generic import FormView, TemplateView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from django.utils.timezone import make_aware, now

from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import EmailSource, RegexRule, Transaction, Tag

class InboxView(LoginRequiredMixin,TemplateView):
    template_name = "finanzas/inbox.html"
    login_url = '/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["email_sources"] = EmailSource.objects.filter(
            active=True,
            user=self.request.user
        ).order_by("name")


        context["transactions_need_review"] = Transaction.objects.filter(
            status="need_review",
            user=self.request.user
        ).order_by("-date")

        context["regex_rules"] = RegexRule.objects.filter(
            active=True,
            user=self.request.user
        ).order_by(
            "-priority",
            "name"
        )

        context["transactions"] = Transaction.objects.filter(
            status="pending",
            user=self.request.user
        ).select_related("matched_rule")

        context["tags"] = Tag.objects.filter(user=self.request.user).order_by("name")

        year = int(self.request.GET.get("year", now().year))
        month = int(self.request.GET.get("month", now().month))


        start_month = make_aware(datetime(year, month, 1))

        # next month (for range)
        if month == 12:
            end_month = make_aware(datetime(year + 1, 1, 1))
        else:
            end_month = make_aware(datetime(year, month + 1, 1))
        messages.info(self.request, f"Usuario: {self.request.user}")

        monthly_tx = Transaction.objects.filter(
            date__gte=start_month,
            date__lt=end_month,
            status="classified",
            user=self.request.user
        )

        context["transactions"] = Transaction.objects.filter(
            date__gte=start_month,
            date__lt=end_month,
            status="pending",
            user=self.request.user
        ).order_by("-date")

        # previous month
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1

        # next month
        next_month = month + 1
        next_year = year
        if next_month == 13:
            next_month = 1
            next_year += 1

        context.update({
            "year": year,
            "month": month,
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month,
        })


        # totals
        total_income = monthly_tx.filter(tags__positive=True).aggregate(total=Sum("amount"))["total"] or 0
        total_expenses = monthly_tx.filter(tags__positive=False).aggregate(total=Sum("amount"))["total"] or 0
        balance = total_income - total_expenses

        by_tag = (
            monthly_tx
            .values("tags__id", "tags__name", "tags__positive")
            .annotate(total=Sum("amount"))
            .order_by("total")
        )

        context["total_income"] = total_income
        context["total_expenses"] = total_expenses
        context["balance"] = balance
        context["by_tag"] = by_tag




        return context



class TagDetailView(LoginRequiredMixin, TemplateView):
    template_name = "finanzas/tag_detail.html"
    login_url = '/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tag = get_object_or_404(Tag, pk=self.kwargs["tag_id"])

        year = int(self.request.GET.get("year", now().year))
        month = int(self.request.GET.get("month", now().month))

        start_month = make_aware(datetime(year, month, 1))

        # next month (for range)
        if month == 12:
            end_month = make_aware(datetime(year + 1, 1, 1))
        else:
            end_month = make_aware(datetime(year, month + 1, 1))


        transactions = Transaction.objects.filter(
            tags=tag,
            date__gte=start_month,
            date__lt=end_month,
            status="classified",
            user=self.request.user
        ).order_by("-date")

        total = transactions.aggregate(total=Sum("amount"))["total"] or 0

        context["tag"] = tag
        context["transactions"] = transactions
        context["total"] = total
        context["tags"] = Tag.objects.filter(user=self.request.user).order_by("name")

        context.update({
            "year": year,
            "month": month,
        })
        return context

class CreateTagView(LoginRequiredMixin, View):
    login_url = '/login'

    def post(self, request):

        name = request.POST.get("name")
        positive = request.POST.get("positive") == "on"

        if name:
            Tag.objects.get_or_create(
                name=name.strip(),
                positive=positive,
                user=request.user
            )

        return redirect("finanzas:inbox")

class CreateTransactionManualView(LoginRequiredMixin, View):
    login_url = '/login'

    def post(self, request):

        description = request.POST.get("description")
        amount = request.POST.get("amount")
        merchant = request.POST.get("merchant")
        date = request.POST.get("date")
        tag_id = request.POST.get("tag_id")

        if not tag_id:
            messages.error(request, "Please select a tag for the transaction.")
            return redirect("finanzas:inbox")
        
        if not amount:
            messages.error(request, "Amount is required.")
            return redirect("finanzas:inbox")

        if description and amount and date:
            transaction = Transaction.objects.create(
                description=description.strip(),
                amount=float(amount),
                merchant=merchant.strip() if merchant else "",
                date=datetime.strptime(date, "%Y-%m-%d").date(),
                status="classified",
                user=self.request.user
            )
            transaction.tags.add(tag_id)
            transaction.save()

        return redirect("finanzas:inbox")

class ClassifyTransactionView(LoginRequiredMixin, View):
    login_url = '/login'

    def post(self, request, pk):

        transaction = get_object_or_404(
            Transaction,
            pk=pk
        )

        tag_id = request.POST.get("tag_id")
        description = request.POST.get("description")
        amount = request.POST.get("amount")

        if transaction.status == "need_review":
            if not description:
                messages.error(request, "Description is required for transactions that need review.")
                return redirect("finanzas:inbox")
            if not amount:
                messages.error(request, "Amount is required for transactions that need review.")
                return redirect("finanzas:inbox")

        # manual fixes
        if description:
            transaction.description = description.strip()

        if amount:
            try:
                transaction.amount = float(amount)
            except ValueError:
                pass  # you can add message here later
        

        if tag_id != "":
            transaction.tags.add(tag_id)
            transaction.status = "classified"
            transaction.raw_text = ""
            transaction.save()
            messages.success(request, "Transaction classified successfully.")
        else:
            messages.error(request, "Please select one tag.")

        return redirect("finanzas:inbox")

class DeleteTransactionView(LoginRequiredMixin, View):
    login_url = '/login'

    def post(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk)
        transaction.delete()
        messages.success(request, "Transaction deleted successfully.")
        return redirect("finanzas:inbox")


class IgnoreTransactionView(LoginRequiredMixin, View):
    login_url = '/login'

    def post(self, request, pk):

        transaction = get_object_or_404(
            Transaction,
            pk=pk
        )

        transaction.status = "ignored"

        transaction.save()

        return redirect("finanzas:inbox")


class UpdateTransactionView(LoginRequiredMixin, View):
    login_url = '/login'

    def post(self, request, pk):

        transaction = get_object_or_404(Transaction, pk=pk)

        description = request.POST.get("description", "").strip()
        amount = request.POST.get("amount", "").strip()
        merchant = request.POST.get("merchant", "").strip()
        tag_id = request.POST.get("tag_id")

        if description:
            transaction.description = description

        if amount:
            try:
                transaction.amount = float(amount)
            except ValueError:
                messages.error(request, "Invalid amount")
                return redirect(request.META.get("HTTP_REFERER", "finanzas:inbox"))
        
        if merchant:
            transaction.merchant = merchant

        if tag_id:
            transaction.tags.set([tag_id])

        transaction.save()

        messages.success(request, "Transaction updated")

        return redirect(request.META.get("HTTP_REFERER", "finanzas:inbox"))


class CreateEmailSourceView(View):

    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")

        if not name or not email:
            messages.error(request, "Both fields are required")
            return redirect("finanzas:inbox")

        EmailSource.objects.create(name=name, sender_email=email, user=request.user)

        messages.success(request, "Email source added")
        return redirect("finanzas:inbox")


class CreateRegexRuleView(View):

    def post(self, request):
        name = request.POST.get("name")
        regex = request.POST.get("regex")
        source_id = request.POST.get("source_id")
        amount_group = request.POST.get("amount_group")
        account_from_group = request.POST.get("account_from_group")
        account_to_group = request.POST.get("account_to_group")
        date_group = request.POST.get("date_group")
        time_group = request.POST.get("time_group")
        date_format = request.POST.get("date_format")
        time_format = request.POST.get("time_format")
        remove_html_tags = request.POST.get("remove_html_tags") == "on"

        if not name or not regex or not source_id:
            messages.error(request, "All fields are required")
            return redirect("finanzas:inbox")

        regex = {
            "name": name,
            "regex": regex,
            "source_id": source_id,
            "user": request.user
        }

        if amount_group:
            regex["amount_group"] = int(amount_group)
        if account_from_group:
            regex["account_from_group"] = int(account_from_group)
        if account_to_group:
            regex["account_to_group"] = int(account_to_group)
        if date_group:
            regex["date_group"] = int(date_group)
        if time_group:
            regex["time_group"] = int(time_group)
        if date_format:
            regex["date_format"] = date_format
        if time_format:
            regex["time_format"] = time_format
        if remove_html_tags:
            regex["remove_html_tags"] = True

        source = get_object_or_404(EmailSource, pk=source_id)

        RegexRule.objects.create(**regex)

        messages.success(request, "Regex rule added")
        return redirect(request.META.get("HTTP_REFERER", "finanzas:inbox"))

class RegexRuleListView(TemplateView):
    template_name = "finanzas/regex_rule_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = int(self.request.GET.get("year", now().year))
        month = int(self.request.GET.get("month", now().month))
        context["regex_rules"] = RegexRule.objects.filter(user=self.request.user).order_by("-priority", "name")
        context["email_sources"] = EmailSource.objects.filter(user=self.request.user).order_by("name")
        context.update({
            "year": year,
            "month": month,
        })

        return context

class UpdateRegexRuleView(View):

    def post(self, request, pk):
        rule = get_object_or_404(RegexRule, pk=pk)

        name = request.POST.get("name")
        regex = request.POST.get("regex")
        source_id = request.POST.get("source_id")
        amount_group = request.POST.get("amount_group")
        account_from_group = request.POST.get("account_from_group")
        account_to_group = request.POST.get("account_to_group")
        remove_html_tags = request.POST.get("remove_html_tags") == "on"
        active = request.POST.get("active") == "on"
        priority = request.POST.get("priority")
        date_group = request.POST.get("date_group")
        time_group = request.POST.get("time_group")
        date_format = request.POST.get("date_format")
        time_format = request.POST.get("time_format")

        if name:
            rule.name = name
        if regex:
            rule.regex = regex
        if source_id:
            rule.source_id = source_id
        if amount_group:
            rule.amount_group = int(amount_group)
        if account_from_group:
            rule.account_from_group = int(account_from_group)
        if account_to_group:
            rule.account_to_group = int(account_to_group)
        if date_group:
            rule.date_group = int(date_group)
        if time_group:
            rule.time_group = int(time_group)
        if date_format:
            rule.date_format = date_format
        if time_format:
            rule.time_format = time_format
        if remove_html_tags is not None:
            rule.remove_html_tags = remove_html_tags
        if priority:
            rule.priority = int(priority)
        if active is not None:
            rule.active = active
        rule.save()

        messages.success(request, "Regex rule updated")
        return redirect(request.META.get("HTTP_REFERER", "finanzas:inbox"))

class DeleteRegexRuleView(View):

    def post(self, request, pk):
        rule = get_object_or_404(RegexRule, pk=pk)
        rule.delete()
        messages.success(request, "Regex rule deleted")
        return redirect(request.META.get("HTTP_REFERER", "finanzas:inbox"))