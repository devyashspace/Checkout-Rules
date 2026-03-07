from django.db import models

class Shop(models.Model):
    shop_domain = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=255)
    delivery_customization_id = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    installed_at = models.DateTimeField(auto_now_add=True)

    PLAN_CHOICES = [
        ("Free", "Free"),
        ("Pro", "Pro"),
    ]

    plan = models.CharField(
        max_length=10,
        choices=PLAN_CHOICES,
        default="Free"
    )

    def __str__(self):
        return self.shop_domain


class Rule(models.Model):
    RULE_TYPE_CHOICES = [
        ("hide_shipping", "Hide shipping method"),
        ("hide_payment", "Hide payment method"),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="rules")
    name = models.CharField(max_length=100)
    rule_id = models.CharField(max_length=100, null=True)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES)
    shopify_delivery_id = models.CharField(max_length=255, null=True, blank=True)
    shopify_payment_id = models.CharField(max_length=255, null=True, blank=True)

    # Generic fields to keep MVP simple
    min_cart_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    cod_fee_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cod_fee_is_percent = models.BooleanField(default=False)
    shipping_method_name = models.CharField(max_length=100, null=True, blank=True)
    payment_method_name = models.CharField(max_length=100, null=True, blank=True)
    summary = models.CharField(max_length=500, null=True, blank=True)

    CONDITION_TYPE_CHOICES = [
        ("and", "All conditions must match (AND)"),
        ("or", "Any condition can match (OR)"),
    ]

    condition_type = models.CharField(
        max_length=10,
        choices=CONDITION_TYPE_CHOICES,
        default="and"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.shop.shop_domain})"


