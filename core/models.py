from django.db import models

class Shop(models.Model):
    shop_domain = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=255)
    delivery_customization_id = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    installed_at = models.DateTimeField(auto_now_add=True)

    PLAN_CHOICES = [
        ("free", "Free"),
        ("pro", "Pro"),
    ]

    plan = models.CharField(
        max_length=10,
        choices=PLAN_CHOICES,
        default="free"
    )

    def __str__(self):
        return self.shop_domain


class Rule(models.Model):
    RULE_TYPE_CHOICES = [
        ("disable_cod_min_cart", "Disable COD below cart value"),
        ("disable_cod_region", "Disable COD for region"),
        ("add_cod_fee", "Add COD fee"),
        ("hide_shipping", "Hide shipping method"),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="rules")
    name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES)

    # Generic fields to keep MVP simple
    min_cart_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    cod_fee_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cod_fee_is_percent = models.BooleanField(default=False)
    shipping_method_name = models.CharField(max_length=100, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.shop.shop_domain})"


