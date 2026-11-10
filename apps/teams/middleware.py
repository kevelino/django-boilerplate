from django.utils.deprecation import MiddlewareMixin

from apps.teams.models import Team, TeamMembership


class CurrentTeamMiddleware(MiddlewareMixin):
    """Attach ``request.team`` (the user's currently selected team) to every request."""

    def process_request(self, request):
        request.team = None
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return
        team_id = request.session.get("current_team_id")
        membership = None
        if team_id:
            membership = TeamMembership.objects.filter(
                user=request.user, team_id=team_id
            ).select_related("team").first()
        if membership is None:
            membership = TeamMembership.objects.filter(user=request.user).select_related("team").first()
            if membership:
                request.session["current_team_id"] = membership.team_id
        if membership:
            request.team = membership.team
            request.team_membership = membership
        else:
            request.team_membership = None