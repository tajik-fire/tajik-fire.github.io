import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from typing import Optional
import secrets

from app.core.config import settings


class EmailService:
    @staticmethod
    def generate_code() -> str:
        return secrets.token_hex(3)
    
    @staticmethod
    async def send_email(to_email: str, subject: str, html_content: str) -> bool:
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            return False
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email
        
        part = MIMEText(html_content, "html")
        msg.attach(part)
        
        try:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Email send error: {e}")
            return False
    
    @staticmethod
    def get_verification_email_html(code: str, expire_minutes: int) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Подтверждение email</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Подтверждение email</h2>
                <p>Ваш код подтверждения: <strong style="font-size: 24px; color: #4CAF50;">{code}</strong></p>
                <p>Код действителен в течение {expire_minutes} минут.</p>
                <p>Если вы не запрашивали этот код, просто проигнорируйте это письмо.</p>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def get_reset_password_email_html(code: str, expire_minutes: int) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Сброс пароля</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #FF9800;">Сброс пароля</h2>
                <p>Ваш код для сброса пароля: <strong style="font-size: 24px; color: #FF9800;">{code}</strong></p>
                <p>Код действителен в течение {expire_minutes} минут.</p>
                <p>Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.</p>
            </div>
        </body>
        </html>
        """
