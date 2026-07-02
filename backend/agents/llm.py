"""Purpose: call the configured AI model through LiteLLM when available.
Inputs: prompt text and model settings.
Outputs: model text or an empty fallback string.
"""

from backend.config import Settings


def complete_prompt(prompt: str, settings: Settings) -> str:
    if not settings.openrouter_api_key:
        return ""
    try:
        from litellm import completion
    except ImportError:
        return ""

    response = completion(
        model=settings.model_name,
        api_key=settings.openrouter_api_key,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    return content or ""
