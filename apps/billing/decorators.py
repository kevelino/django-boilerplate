from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from djstripe.models import Subscription


def subscription_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        active = Subscription.objects.filter(
            customer__subscriber=request.user, status__in=["active", "trialing"]
        ).exists()
        if not active:
            messages.warning(request, "This feature requires an active subscription.")
            return redirect("pricing")
        return view_func(request, *args, **kwargs)

    return _wrapped