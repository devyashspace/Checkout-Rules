from django.urls import path
from .views import install, callback, app_home, create_rule, upgrade, billing_callback, activate_rule

urlpatterns = [
    path("install/", install, name="shopify_install"),
    path("callback/", callback, name="shopify_callback"),
    path("app/", app_home, name="app_home"),
    path("rules/create/", create_rule, name="create_rule"),
    path("upgrade/", upgrade),
    path("billing/callback/", billing_callback),
    path("activate_rule/", activate_rule, name="activate_rule"),
    

]
