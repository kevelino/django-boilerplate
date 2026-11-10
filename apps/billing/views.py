import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from djstripe.models import Customer, Subscription


def _stripe_keys():
    return settings.STRIPE_TEST_SECRET_KEY if not settings.STRIPE_LIVE_MODE else settings.STRIPE_LIVE_SECRET_KEY


def pricing(request):
    try:
        import djstripe.models as djstripe_models

        products = djstripe_models.Product.objects.filter(active=True)
    except Exception:
        products = []
    return render(request, "billing/pricing.html", {"products": products, "publishable_key": settings.STRIPE_TEST_PUBLISHABLE_KEY if not settings.STRIPE_LIVE_MODE else settings.STRIPE_LIVE_PUBLISHABLE_KEY})


@login_required
@require_POST
def create_checkout_session(request):
    stripe.api_key = _stripe_keys()
    price_id = request.POST.get("price_id")
    if not price_id:
        messages.error(request, "No price selected.")
        return redirect("pricing")
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=request.build_absolute_uri("/billing/success/"),
        cancel_url=request.build_absolute_uri("/billing/cancel/"),
        client_reference_id=str(request.user.pk),
        customer_email=request.user.email,
    )
    return redirect(session.url, permanent=False)


@login_required
def billing_success(request):
    messages.success(request, "Subscription activated. Thank you!")
    return redirect("billing_portal")


@login_required
def billing_cancel(request):
    messages.info(request, "Checkout cancelled.")
    return redirect("pricing")


@login_required
def billing_portal(request):
    stripe.api_key = _stripe_keys()
    try:
        customer = Customer.objects.get(subscriber=request.user)
    except Customer.DoesNotExist:
        messages.info(request, "You don't have a subscription yet.")
        return redirect("pricing")
    session = stripe.billing_portal.Session.create(customer=customer.id, return_url=request.build_absolute_uri("/billing/"))
    return redirect(session.url, permanent=False)


@login_required
def subscription_status(request):
    sub = Subscription.objects.filter(customer__subscriber=request.user, status__in=["active", "trialing"]).first()
    return render(request, "billing/status.html", {"subscription": sub})