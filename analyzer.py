import json
import anthropic
import config

_client = anthropic.Anthropic(api_key=config.CLAUDE_API_KEY)


def analyze_messages(messages: list[dict], group_name: str) -> dict:
    """Use Claude to analyze messages and extract insights."""
    if not messages:
        return {"error": "no_messages"}

    messages_text = "\n".join(
        f"[{m['date']}] {m['full_name']} ({m['username'] or 'нет username'}): {m['text'][:300]}"
        for m in messages[:30]  # test limit
    )

    prompt = f"""Ты аналитик чата продавцов на маркетплейсах. Вот сообщения из группы за последние несколько часов:

---
{messages_text}
---

Выполни два задания:

1. ОБЩАЯ АНАЛИТИКА:
   - Найди ТОП-5 наиболее часто обсуждаемых тем или вопросов (сгруппируй похожие)
   - Для каждой темы укажи примерное количество упоминаний

2. ВОПРОСЫ ПРО МАРКЕТПЛЕЙС (приоритет для личного ответа):
   - Найди сообщения, где человек явно спрашивает что-то о работе маркетплейса (Wildberries, Ozon, Яндекс.Маркет, Lamoda, AliExpress и т.д.): комиссии, правила, штрафы, выплаты, карточки, логистика, рейтинг и т.п.
   - Включай ТОЛЬКО реальные вопросы, а не обсуждения или ответы
   - Для каждого вопроса укажи: username, full_name, time, и точную цитату вопроса

Верни СТРОГО JSON (без markdown блоков, без пояснений):
{{
  "top_topics": [
    {{"topic": "название темы", "count": 3, "summary": "краткое описание"}},
    ...
  ],
  "marketplace_questions": [
    {{
      "username": "@username или null",
      "full_name": "Имя Фамилия",
      "time": "HH:MM",
      "question": "точная цитата вопроса",
      "topic": "тема вопроса (1-3 слова)"
    }},
    ...
  ],
  "total_messages": {len(messages)},
  "active_users": 0
}}

active_users = количество уникальных пользователей, написавших хоть одно сообщение."""

    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)

    # Count unique users
    unique = {m["sender_id"] for m in messages if m.get("sender_id")}
    result["active_users"] = len(unique)

    return result
