import requests
from app.core.config import settings


def generate_ai_explanation(event_log):
    try:
        prompt = f"""You are a concise IoT security analyst. Write exactly one sentence (20-30 words) summarizing this alert. Be direct and professional. No preamble, no labels, no bullet points — output the sentence only.

CONTEXT:
Device {event_log.device_id} triggered "{event_log.event}" ({event_log.severity} / {event_log.status}) in {event_log.zone or "an unmonitored area"} at heart rate {event_log.heart_rate} bpm.
Core reason: {event_log.reason}.

RULES:
- Must mention: device location context + physiological indicator + risk outcome
- Exactly 20-30 words
- One sentence, plain text only"""

        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_BASE_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,     
                    "top_p": 0.85,
                    "num_predict": 60,      
                    "stop": [".", "\n"]      
                }
            },
            timeout=30
        )

        response.raise_for_status()
        raw = response.json().get("response", "").strip()

        # ensure it ends with a period
        if raw and not raw.endswith("."):
            raw = raw + "."

        return raw

    except Exception as e:
        return f"AI evaluation unavailable: {str(e)}"