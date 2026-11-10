from django.core.exceptions import PermissionDenied

from apps.teams.models import TeamMembership


def require_team(request):
    if getattr(request, "team", None) is None:
        raise PermissionDenied("You must belong to a team to perform this action.")
    return request.team


def require_role(request, *roles):
    membership = getattr(request, "team_membership", None)
    if membership is None or membership.role not in roles:
        raise PermissionDenied("You do not have permission to perform this action.")
    return membership