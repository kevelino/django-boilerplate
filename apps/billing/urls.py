from django.urls import include, path

from apps.billing import views

urlpatterns = [
    path("", views.subscription_status, name="billing_status"),
    path("pricing/", views.pricing, name="pricing"),
    path("checkout/", views.create_checkout_session, name="create_checkout_session"),
    path("success/", views.billing_success, name="billing_success"),
    path("cancel/", views.billing_cancel, name="billing_cancel"),
    path("portal/", views.billing_portal, name="billing_portal"),
]