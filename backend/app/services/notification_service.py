import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, body: str) -> bool:
    from app.config import settings
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("Email not configured, skipping")
        return False
    try:
        import aiosmtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_user
        msg["To"] = to_email
        msg.attach(MIMEText(body, "html", "utf-8"))

        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        return True
    except Exception as e:
        logger.error(f"Email send error: {e}")
        return False


async def send_telegram(chat_id: str, text: str) -> bool:
    from app.config import settings
    if not settings.telegram_bot_token:
        logger.warning("Telegram not configured, skipping")
        return False
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            )
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Telegram send error: {e}")
        return False


async def send_push(endpoint: str, p256dh: str, auth: str, title: str, body: str) -> bool:
    from app.config import settings
    if not settings.vapid_private_key:
        logger.warning("Push not configured, skipping")
        return False
    try:
        from pywebpush import webpush, WebPushException
        import json
        webpush(
            subscription_info={"endpoint": endpoint, "keys": {"p256dh": p256dh, "auth": auth}},
            data=json.dumps({"title": title, "body": body}),
            vapid_private_key=settings.vapid_private_key,
            vapid_claims={"sub": settings.vapid_email},
        )
        return True
    except Exception as e:
        logger.error(f"Push send error: {e}")
        return False


async def send_deadline_reminder(user, grant, days_before: int, db):
    from app.models.notification import NotificationLog
    subject = f"Напоминание: дедлайн гранта «{grant.source_name}» через {days_before} дней"
    body = f"""
    <h2>Напоминание о дедлайне гранта</h2>
    <p>Грант: <strong>{grant.source_name}</strong></p>
    <p>До закрытия приёма заявок осталось: <strong>{days_before} дней</strong></p>
    <p>Максимальная сумма: {grant.max_amount_text or 'не указана'}</p>
    <p><a href="{grant.source_url or '#'}">Перейти к гранту</a></p>
    """
    results = {}
    if user.notify_email and user.email:
        results["email"] = await send_email(user.email, subject, body)
    if user.notify_telegram and user.telegram_chat_id:
        text = f"<b>{subject}</b>\n\nГрант: {grant.source_name}\nДо дедлайна: {days_before} дней\nСумма: {grant.max_amount_text or 'не указана'}"
        results["telegram"] = await send_telegram(user.telegram_chat_id, text)
    if user.notify_push and user.push_endpoint:
        results["push"] = await send_push(user.push_endpoint, user.push_p256dh, user.push_auth, subject, f"До дедлайна {days_before} дней")

    # Log
    for channel, success in results.items():
        log = NotificationLog(
            user_id=user.id,
            grant_id=grant.id,
            channel=channel,
            message_type="deadline_reminder",
            days_before=days_before,
            success=success,
        )
        db.add(log)
    await db.commit()
    return results
