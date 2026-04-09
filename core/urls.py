from django.urls import path
from .views import install, callback, app_home, create_rule, upgrade, billing_callback, activate_rule, privacy_policy, data_deletion_policy, delete_rule, deactivate_rule, app_uninstalled

urlpatterns = [
    path("install/", install, name="shopify_install"),
    path("callback/", callback, name="shopify_callback"),
    path("app/", app_home, name="app_home"),
    path("rules/create/", create_rule, name="create_rule"),
    path('billing/upgrade/', upgrade, name='billing_upgrade'),
    path("billing/callback/", billing_callback),
    path("activate_rule/", activate_rule, name="activate_rule"),
    path("privacy_policy/", privacy_policy, name="privacy_policy"),
    path("data_deletion_policy/", data_deletion_policy, name="data_deletion_policy"),
    path("delete_rule/", delete_rule, name="delete_rule"),
    path("deactivate_rule/", deactivate_rule, name="deactivate_rule"),
    path("webhooks/app-uninstalled/", app_uninstalled),
    

]
