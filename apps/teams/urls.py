from django.urls import path

from apps.teams import views

urlpatterns = [
    path("", views.team_list, name="team_list"),
    path("create/", views.team_create, name="team_create"),
    path("<slug:slug>/", views.team_detail, name="team_detail"),
    path("<slug:slug>/switch/", views.team_switch, name="team_switch"),
    path("<slug:slug>/invite/", views.team_invite, name="team_invite"),
    path("<slug:slug>/members/<int:user_id>/role/", views.member_update_role, name="member_update_role"),
    path("<slug:slug>/members/<int:user_id>/remove/", views.member_remove, name="member_remove"),
    path("invitations/<uuid:token>/accept/", views.invitation_accept, name="invitation_accept"),
]