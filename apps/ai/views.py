from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.ai.models import Conversation, Message
from apps.ai.services import chat_completion
from apps.billing.decorators import subscription_required


@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(user=request.user)
    return render(request, "ai/conversation_list.html", {"conversations": conversations})


@login_required
@require_POST
def conversation_create(request):
    conv = Conversation.objects.create(
        user=request.user,
        title=request.POST.get("title", "New conversation"),
        provider=request.POST.get("provider", "openai"),
        model=request.POST.get("model", "gpt-4o-mini"),
    )
    return redirect("conversation_detail", pk=conv.pk)


@login_required
def conversation_detail(request, pk):
    conv = get_object_or_404(Conversation, pk=pk, user=request.user)
    messages_list = conv.messages.all()
    return render(request, "ai/conversation_detail.html", {"conversation": conv, "messages": messages_list})


@login_required
@require_POST
@subscription_required
def send_message(request, pk):
    conv = get_object_or_404(Conversation, pk=pk, user=request.user)
    content = request.POST.get("content", "").strip()
    if not content:
        return redirect("conversation_detail", pk=pk)
    Message.objects.create(conversation=conv, role="user", content=content)
    history = [{"role": m.role, "content": m.content} for m in conv.messages.all()]
    try:
        reply = chat_completion(history, model=conv.model, provider=conv.provider)
    except Exception as exc:
        reply = f"Error: {exc}"
    Message.objects.create(conversation=conv, role="assistant", content=reply)
    if request.headers.get("HX-Request"):
        return render(request, "ai/_messages.html", {"conversation": conv, "messages": conv.messages.all()})
    return redirect("conversation_detail", pk=pk)