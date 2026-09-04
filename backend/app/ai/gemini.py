import logging
import re
from fastapi import HTTPException
from ..config import settings
logger = logging.getLogger(__name__)
def generate(prompt:str)->str:
    if not settings.gemini_api_key: raise HTTPException(503,"AI is not configured. Add GEMINI_API_KEY to .env and restart the backend.")
    try:
        from google import genai
        from google.genai import types
        client=genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=120000),
        )
        try:
            return client.models.generate_content(model=settings.gemini_model,contents=prompt).text
        except Exception as first_error:
            # Projects can have different model entitlements. Discover models from this
            # key instead of guessing a model name when the configured one is unavailable.
            if "model" not in str(first_error).lower() and "404" not in str(first_error):
                raise
            available = [model.name.removeprefix("models/") for model in client.models.list()]
            preferred = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest"]
            compatible = next((model for model in preferred if model in available), None)
            if not compatible:
                raise first_error
            logger.info("Configured Gemini model unavailable; using compatible model %s", compatible)
            return client.models.generate_content(model=compatible, contents=prompt).text
    except Exception as exc:
        logger.warning("Gemini request failed (%s): %s", type(exc).__name__, str(exc)[:500])
        message = str(exc).lower()
        if "429" in message or "quota" in message or "rate" in message:
            detail = "Gemini quota or rate limit was reached. Wait for the quota window to reset, check the API project's quota, or use a Gemini key with available quota."
        elif "api key" in message or "api_key" in message or "permission" in message or "401" in message or "403" in message:
            detail = "Gemini rejected the API key. Confirm it is a valid Gemini API key and that the Generative Language API is enabled for its project."
        elif "499" in message or "cancelled" in message or "canceled" in message or "503" in message or "unavailable" in message or "504" in message or "deadline_exceeded" in message or "timeout" in message:
            detail = "Gemini is temporarily unavailable or overloaded. Wait a moment and try again, or check the Gemini API project's status and quota."
        elif "model" in message or "404" in message:
            detail = f"Gemini could not use the configured model '{settings.gemini_model}'. Check that the model is enabled for this API key and restart the backend after changing .env."
        else:
            detail = "Gemini could not complete the request. Check your internet connection and the Gemini API project's status."
        safe_reason = re.sub(r"AIza[\w-]+", "[redacted]", str(exc))[:350]
        raise HTTPException(502, f"{detail} Gemini diagnostic: {safe_reason}")
