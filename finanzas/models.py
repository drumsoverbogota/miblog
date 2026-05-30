from django.db import models

# Create your models here.
class EmailSource(models.Model):

    name = models.CharField(max_length=100)

    sender_email = models.EmailField(
        unique=True
    )

    active = models.BooleanField(
        default=True
    )

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.sender_email})"

class RegexRule(models.Model):

    source = models.ForeignKey(
        EmailSource,
        on_delete=models.CASCADE,
        related_name="rules"
    )

    name = models.CharField(max_length=100)

    regex = models.TextField()

    remove_html_tags = models.BooleanField(
        default=False,
        help_text="If enabled, HTML tags will be removed from the email body before applying the regex."
    )

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Cantidad
    amount_group = models.IntegerField(
        default=1
    )

    # Lugar de compra o persona
    merchant_group = models.IntegerField(
        null=True,
        blank=True
    )

    account_from_group = models.IntegerField(
        null=True,
        blank=True
    )

    account_to_group = models.IntegerField(
        null=True,
        blank=True
    )

    date_group = models.IntegerField(
        null=True,
        blank=True
    )

    date_format = models.CharField(
        max_length=50,
        blank=True,
        help_text="Use Python date format, e.g. %d/%m/%Y",
        default="%d/%m/%Y"
    )

    time_format = models.CharField(
        max_length=50,
        blank=True,
        help_text="Use Python time format, e.g. %H:%M:%S",
        default="%H:%M"
    )

    time_group = models.IntegerField(
        null=True,
        blank=True
    )

    active = models.BooleanField(
        default=True
    )

    priority = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.name

class Transaction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("classified", "Classified"),
        ("ignored", "Ignored"),
        ("need_review", "Need Review"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    source = models.ForeignKey(
        EmailSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    matched_rule = models.ForeignKey(
        RegexRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )    

    reviewed = models.BooleanField(default=False)

    raw_text = models.TextField(blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    description = models.CharField(max_length=255, blank=True)
    merchant = models.CharField(max_length=255, blank=True)
    account_from = models.CharField(max_length=100, blank=True)
    account_to = models.CharField(max_length=100, blank=True)

    date = models.DateTimeField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    tags = models.ManyToManyField("Tag", blank=True)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=False)
    positive = models.BooleanField(default=False)


    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name
    