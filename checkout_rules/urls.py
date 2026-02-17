from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def root_redirect(request):
    shop = request.GET.get("shop")
    host = request.GET.get("host")
    return redirect(f"/shopify/app/?shop={shop}&host={host}")

urlpatterns = [
    path("", root_redirect),
    path("admin/", admin.site.urls),
    path("shopify/", include("core.urls")),
]

