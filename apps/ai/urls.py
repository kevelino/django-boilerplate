from django.urls import path

from apps.ai import views

urlpatterns = [
    path("", views.conversation_list, name="conversation_list"),
    path("create/", views.conversation_create, name="conversation_create"),
    path("<int:pk>/", views.conversation_detail, name="conversation_detail"),
    path("<int:pk>/send/", views.send_message, name="send_message"),
]