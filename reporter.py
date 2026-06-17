from datetime import datetime, timezone, timedelta
import telegram
import config

_bot = telegram.Bot(token=config.BOT_TOKEN)

PERIOD_LABELS = {
    "06:00": "🌅 Утренний",
    "11:00": "☀️ Дневной",
    "16:00": "🌙 Вечерний",
}


def _period_label(utc_hour: int) -> str:
    if utc_hour < 9:
        return "🌅 Утренний"
    elif utc_hour < 14:
        return "☀️ Дневной"
    return "🌙 Вечерний"


def _format_group_report(group_name: str, analysis: dict) -> str:
    if "error" in analysis:
        return f"❌ Группа {group_name}: ошибка — {analysis['error']}\n"

    lines = [f"📌 Группа: {group_name}"]
    lines.append(f"💬 Сообщений: {analysis.get('total_messages', 0)} | 👥 Активных: {analysis.get('active_users', 0)}\n")

    # Top topics
    topics = analysis.get("top_topics", [])
    if topics:
        lines.append("🔥 *Горячие темы:*")
        for i, t in enumerate(topics[:5], 1):
            count_str = f"({t['count']} упом.)" if t.get("count") else ""
            lines.append(f"  {i}. {t['topic']} {count_str}")
            if t.get("summary"):
                lines.append(f"     _{t['summary']}_")
        lines.append("")

    # Marketplace questions
    questions = analysis.get("marketplace_questions", [])
    if questions:
        lines.append("❓ *Вопросы про маркетплейс — напиши им:*")
        lines.append("─" * 30)
        for q in questions:
            username = q.get("username") or "нет username"
            name = q.get("full_name", "")
            time_ = q.get("time", "")
            topic = q.get("topic", "")
            question = q.get("question", "")

            lines.append(f"👤 {name}  {username}  [{time_}]")
            if topic:
                lines.append(f"📂 {topic}")
            lines.append(f'"{question}"')
            lines.append("─" * 30)
    else:
        lines.append("✅ Вопросов про маркетплейс не найдено")

    return "\n".join(lines)


async def send_report(group_reports: dict[str, dict]) -> None:
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc + timedelta(hours=3)  # UTC+3
    period = _period_label(now_utc.hour)
    date_str = now_local.strftime("%d.%m.%Y %H:%M")

    header = f"📊 *{period} дайджест* | {date_str}\n{'═' * 32}\n"

    full_report = header
    for group, analysis in group_reports.items():
        full_report += _format_group_report(group, analysis) + "\n\n"

    # Telegram has 4096 char limit per message; split if needed
    chunks = _split_message(full_report, 4000)
    for chunk in chunks:
        await _bot.send_message(
            chat_id=config.REPORT_CHAT_ID,
            text=chunk,
            parse_mode="Markdown",
        )


def _split_message(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        parts.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return parts
