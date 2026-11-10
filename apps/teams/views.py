import uuid
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.teams.models import Team, TeamInvitation, TeamMembership
from apps.teams.permissions import require_role


@login_required
def team_list(request):
    memberships = TeamMembership.objects.filter(user=request.user).select_related("team")
    return render(request, "teams/team_list.html", {"memberships": memberships})


@login_required
@require_http_methods(["GET", "POST"])
def team_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            messages.error(request, "Team name is required.")
            return render(request, "teams/team_create.html")
        team = Team.objects.create(name=name, owner=request.user)
        TeamMembership.objects.create(team=team, user=request.user, role=TeamMembership.ROLE_OWNER)
        request.session["current_team_id"] = team.id
        messages.success(request, f"Team '{team.name}' created.")
        return redirect("team_detail", slug=team.slug)
    return render(request, "teams/team_create.html")


@login_required
def team_detail(request, slug):
    team = get_object_or_404(Team, slug=slug)
    membership = TeamMembership.objects.filter(team=team, user=request.user).first()
    if membership is None:
        raise PermissionDenied
    members = TeamMembership.objects.filter(team=team).select_related("user")
    invitations = TeamInvitation.objects.filter(team=team, accepted=False)
    return render(request, "teams/team_detail.html", {
        "team": team,
        "membership": membership,
        "members": members,
        "invitations": invitations,
    })


@login_required
@require_http_methods(["POST"])
def team_switch(request, slug):
    team = get_object_or_404(Team, slug=slug)
    if not TeamMembership.objects.filter(team=team, user=request.user).exists():
        raise PermissionDenied
    request.session["current_team_id"] = team.id
    messages.success(request, f"Switched to '{team.name}'.")
    return redirect(request.POST.get("next") or "team_detail", slug=team.slug)


@login_required
@require_http_methods(["POST"])
def team_invite(request, slug):
    team = get_object_or_404(Team, slug=slug)
    require_role(request, TeamMembership.ROLE_OWNER, TeamMembership.ROLE_ADMIN)
    # ensure request.team matches
    email = request.POST.get("email", "").strip()
    role = request.POST.get("role", TeamMembership.ROLE_MEMBER)
    if not email:
        messages.error(request, "Email is required.")
        return redirect("team_detail", slug=slug)
    invitation = TeamInvitation.objects.create(
        team=team,
        email=email,
        role=role,
        invited_by=request.user,
        expires_at=timezone.now() + timedelta(days=7),
    )
    # send email (console backend in dev)
    from django.core.mail import send_mail
    accept_url = request.build_absolute_uri(f"/teams/invitations/{invitation.token}/accept/")
    send_mail(
        subject=f"You're invited to join {team.name}",
        message=f"Join {team.name}: {accept_url}",
        from_email=None,
        recipient_list=[email],
    )
    messages.success(request, f"Invitation sent to {email}.")
    return redirect("team_detail", slug=slug)


@login_required
def invitation_accept(request, token):
    invitation = get_object_or_404(TeamInvitation, token=token)
    if not invitation.is_valid:
        messages.error(request, "This invitation is no longer valid.")
        return redirect("team_list")
    if invitation.email.lower() != request.user.email.lower():
        messages.error(request, "This invitation was sent to a different email address.")
        return redirect("team_list")
    TeamMembership.objects.get_or_create(
        team=invitation.team,
        user=request.user,
        defaults={"role": invitation.role},
    )
    invitation.accepted = True
    invitation.accepted_by = request.user
    invitation.save(update_fields=["accepted", "accepted_by", "updated_at"])
    request.session["current_team_id"] = invitation.team.id
    messages.success(request, f"You joined '{invitation.team.name}'.")
    return redirect("team_detail", slug=invitation.team.slug)


@login_required
@require_http_methods(["POST"])
def member_update_role(request, slug, user_id):
    team = get_object_or_404(Team, slug=slug)
    require_role(request, TeamMembership.ROLE_OWNER)
    membership = get_object_or_404(TeamMembership, team=team, user_id=user_id)
    if membership.role == TeamMembership.ROLE_OWNER:
        messages.error(request, "Cannot change the owner's role.")
        return redirect("team_detail", slug=slug)
    new_role = request.POST.get("role")
    if new_role in dict(TeamMembership.ROLE_CHOICES):
        membership.role = new_role
        membership.save(update_fields=["role", "updated_at"])
        messages.success(request, "Role updated.")
    return redirect("team_detail", slug=slug)


@login_required
@require_http_methods(["POST"])
def member_remove(request, slug, user_id):
    team = get_object_or_404(Team, slug=slug)
    require_role(request, TeamMembership.ROLE_OWNER, TeamMembership.ROLE_ADMIN)
    membership = get_object_or_404(TeamMembership, team=team, user_id=user_id)
    if membership.role == TeamMembership.ROLE_OWNER:
        messages.error(request, "Cannot remove the team owner.")
        return redirect("team_detail", slug=slug)
    membership.delete()
    messages.success(request, "Member removed.")
    return redirect("team_detail", slug=slug)