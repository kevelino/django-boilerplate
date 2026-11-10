from django.conf import settings


def get_provider(provider=None):
    provider = provider or settings.AI_DEFAULT_PROVIDER
    if provider == "anthropic":
        import anthropic

        return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY), "anthropic"
    import openai

    return openai.OpenAI(api_key=settings.OPENAI_API_KEY), "openai"


def chat_completion(messages, model=None, provider=None, stream=False):
    client, prov = get_provider(provider)
    model = model or settings.AI_DEFAULT_MODEL
    if prov == "anthropic":
        # Convert messages to anthropic format
        system = ""
        user_msgs = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                user_msgs.append({"role": m["role"], "content": m["content"]})
        kwargs = {"model": model, "messages": user_msgs, "max_tokens": 1024}
        if system:
            kwargs["system"] = system
        if stream:
            return client.messages.stream(**kwargs)
        resp = client.messages.create(**kwargs)
        return resp.content[0].text
    if stream:
        return client.chat.completions.create(model=model, messages=messages, stream=True)
    resp = client.chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content