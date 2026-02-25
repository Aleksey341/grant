import anthropic
import hashlib
import json
from typing import Optional, Dict, Any
from app.config import settings

_client: Optional[anthropic.AsyncAnthropic] = None


def get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def get_hint_for_field(
    field_name: str,
    current_value: str,
    grant_info: str,
    applicant_type: str = "individual",
) -> str:
    if not settings.anthropic_api_key:
        return "AI подсказки недоступны. Укажите ANTHROPIC_API_KEY в настройках."

    client = get_client()
    prompt = f"""Ты помощник по заполнению грантовых заявок. Дай 2-4 конкретных практических совета для поля "{field_name}".

Текущее значение поля: {current_value or "(пусто)"}

Информация о гранте:
{grant_info}

Тип заявителя: {applicant_type}

Дай краткие, конкретные советы на русском языке. Формат: нумерованный список."""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


async def check_text(text: str, context: str = "") -> Dict[str, Any]:
    if not settings.anthropic_api_key:
        return {"improved_text": text, "changes": []}

    client = get_client()
    prompt = f"""Улучши следующий текст для грантовой заявки. Сделай его более профессиональным, конкретным и убедительным.

Текст:
{text}

{f"Контекст: {context}" if context else ""}

Верни JSON в формате:
{{"improved_text": "улучшенный текст", "changes": ["описание изменения 1", "описание изменения 2"]}}

Только JSON, без дополнительного текста."""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return json.loads(message.content[0].text)
    except Exception:
        return {"improved_text": message.content[0].text, "changes": []}


async def generate_section(
    section_name: str,
    project_topic: str,
    target_audience: str,
    applicant_data: Dict[str, Any],
    grant_requirements: str = "",
) -> str:
    if not settings.anthropic_api_key:
        return f"[Раздел: {section_name}]\n\nAI генерация недоступна. Укажите ANTHROPIC_API_KEY."

    client = get_client()
    prompt = f"""Напиши раздел "{section_name}" для грантовой заявки.

Тема проекта: {project_topic}
Целевая аудитория: {target_audience}
Данные заявителя: {json.dumps(applicant_data, ensure_ascii=False)}
{f"Требования гранта: {grant_requirements}" if grant_requirements else ""}

Напиши профессиональный, конкретный текст раздела на русском языке. Объём: 200-400 слов."""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        temperature=0.6,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


async def extract_grant_data(page_text: str, grant_name: str = "") -> Dict[str, Any]:
    """Extract structured grant data from scraped page text using Claude."""
    if not settings.anthropic_api_key:
        return {}

    client = get_client()
    prompt = f"""Проанализируй текст страницы гранта и извлеки структурированную информацию.

Название гранта: {grant_name}

Текст страницы (до 8000 символов):
{page_text[:8000]}

Верни JSON:
{{
  "deadlines": [{{"date": "YYYY-MM-DD или null", "label": "описание", "is_confirmed": true/false}}],
  "max_amount": число в рублях или null,
  "is_accepting_now": true/false/null,
  "changes_detected": false,
  "window_schedule": "описание окон подачи",
  "notes": "важные изменения или новости"
}}

Только JSON."""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        text = message.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return {"error": "parse_failed", "raw": message.content[0].text}
