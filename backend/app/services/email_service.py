"""
邮件服务配置
支持 SMTP、SendGrid、Resend 等多种邮件服务商
"""

from pydantic import EmailStr
from typing import Optional
from jinja2 import Template
import aiohttp
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger


class EmailService:
    """邮件服务基类"""

    async def send_email(
        self,
        to_email: EmailStr,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """发送邮件"""
        raise NotImplementedError


class SMTPService(EmailService):
    """SMTP 邮件服务"""

    def __init__(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.from_email = from_email or username
        self.from_name = from_name or "PitchCube"

    async def send_email(
        self,
        to_email: EmailStr,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """通过 SMTP 发送邮件"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # 添加纯文本版本
            if text_content:
                message.attach(MIMEText(text_content, "plain", "utf-8"))

            # 添加 HTML 版本
            message.attach(MIMEText(html_content, "html", "utf-8"))

            # 发送邮件
            await aiosmtplib.send(
                message,
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls,
                start_tls=not self.use_tls and self.port == 587,
            )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False


class ResendService(EmailService):
    """Resend API 邮件服务（推荐，有免费额度）"""

    API_BASE = "https://api.resend.com"

    def __init__(self, api_key: str, from_email: str = "noreply@pitchcube.ai"):
        self.api_key = api_key
        self.from_email = from_email

    async def send_email(
        self,
        to_email: EmailStr,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """通过 Resend API 发送邮件"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "from": f"PitchCube <{self.from_email}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content,
                }

                if text_content:
                    payload["text"] = text_content

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }

                async with session.post(
                    f"{self.API_BASE}/emails", json=payload, headers=headers
                ) as response:
                    if response.status in [200, 202]:
                        result = await response.json()
                        logger.info(
                            f"Email sent via Resend to {to_email}, id: {result.get('id')}"
                        )
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Resend API error: {response.status} - {error_text}"
                        )
                        return False

        except Exception as e:
            logger.error(f"Failed to send email via Resend: {e}")
            return False


class EmailTemplates:
    """邮件模板"""

    @staticmethod
    def verification_email(
        username: str, verification_code: str, expires_minutes: int = 30
    ) -> tuple:
        """生成邮箱验证邮件"""
        subject = "【PitchCube】验证您的邮箱"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .code {{ background: #fff; border: 2px solid #e5e7eb; border-radius: 8px; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #4f46e5; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 PitchCube</h1>
                </div>
                <div class="content">
                    <h2>您好，{username}！</h2>
                    <p>感谢您注册 PitchCube 路演魔方。请使用以下验证码完成邮箱验证：</p>
                    <div class="code">{verification_code}</div>
                    <p>此验证码将在 <strong>{expires_minutes} 分钟</strong> 后过期。</p>
                    <p>如果这不是您的操作，请忽略此邮件。</p>
                </div>
                <div class="footer">
                    <p>PitchCube 路演魔方 | 让创意变成现实</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        您好，{username}！

        感谢您注册 PitchCube 路演魔方。请使用以下验证码完成邮箱验证：

        {verification_code}

        此验证码将在 {expires_minutes} 分钟后过期。
        如果这不是您的操作，请忽略此邮件。

        PitchCube 路演魔方 | 让创意变成现实
        """

        return subject, html_content, text_content

    @staticmethod
    def password_reset_email(
        username: str, reset_token: str, expires_hours: int = 1
    ) -> tuple:
        """生成密码重置邮件"""
        subject = "【PitchCube】重置您的密码"

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #4f46e5; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 PitchCube</h1>
                </div>
                <div class="content">
                    <h2>您好，{username}！</h2>
                    <p>我们收到了重置您账户密码的请求。点击下面的按钮重置密码：</p>
                    <a href="{reset_url}" class="button">重置密码</a>
                    <p>或者复制以下链接到浏览器：</p>
                    <p style="word-break: break-all; color: #4f46e5;">{reset_url}</p>
                    <p>此链接将在 <strong>{expires_hours} 小时</strong> 后过期。</p>
                    <p>如果这不是您的操作，请忽略此邮件，您的密码将保持不变。</p>
                </div>
                <div class="footer">
                    <p>PitchCube 路演魔方 | 让创意变成现实</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        您好，{username}！

        我们收到了重置您账户密码的请求。请点击以下链接重置密码：

        {reset_url}

        此链接将在 {expires_hours} 小时后过期。
        如果这不是您的操作，请忽略此邮件，您的密码将保持不变。

        PitchCube 路演魔方 | 让创意变成现实
        """

        return subject, html_content, text_content

    @staticmethod
    def team_invitation_email(
        inviter_name: str,
        team_name: str,
        invite_token: str,
        role: str = "member",
        expires_days: int = 7,
    ) -> tuple:
        """生成团队邀请邮件"""
        subject = f"【PitchCube】{inviter_name} 邀请您加入 {team_name}"

        invite_url = f"{settings.FRONTEND_URL}/team/accept-invite?token={invite_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #4f46e5; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
                .team-info {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 PitchCube</h1>
                </div>
                <div class="content">
                    <h2>团队邀请</h2>
                    <p><strong>{inviter_name}</strong> 邀请您加入团队 <strong>{team_name}</strong></p>
                    <div class="team-info">
                        <p><strong>角色：</strong>{role}</p>
                        <p><strong>邀请有效期：</strong>{expires_days} 天</p>
                    </div>
                    <a href="{invite_url}" class="button">接受邀请</a>
                    <p>或者复制以下链接到浏览器：</p>
                    <p style="word-break: break-all; color: #4f46e5;">{invite_url}</p>
                    <p>如果您不想加入此团队，请忽略此邮件。</p>
                </div>
                <div class="footer">
                    <p>PitchCube 路演魔方 | 让创意变成现实</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        团队邀请

        {inviter_name} 邀请您加入团队 {team_name}

        角色：{role}
        邀请有效期：{expires_days} 天

        请点击以下链接接受邀请：
        {invite_url}

        如果您不想加入此团队，请忽略此邮件。

        PitchCube 路演魔方 | 让创意变成现实
        """

        return subject, html_content, text_content


# 全局邮件服务实例
email_service: Optional[EmailService] = None
email_templates = EmailTemplates()


def init_email_service():
    """初始化邮件服务"""
    global email_service

    # 优先使用 Resend（推荐，有免费额度）
    if hasattr(settings, "RESEND_API_KEY") and settings.RESEND_API_KEY:
        email_service = ResendService(
            api_key=settings.RESEND_API_KEY,
            from_email=getattr(settings, "RESEND_FROM_EMAIL", "noreply@pitchcube.ai"),
        )
        logger.info("Email service initialized: Resend")

    # 其次使用 SMTP
    elif hasattr(settings, "SMTP_HOST") and settings.SMTP_HOST:
        email_service = SMTPService(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            from_email=getattr(settings, "SMTP_FROM_EMAIL", settings.SMTP_USER),
            from_name=getattr(settings, "SMTP_FROM_NAME", "PitchCube"),
        )
        logger.info("Email service initialized: SMTP")

    else:
        logger.warning("No email service configured. Email features will be disabled.")


def get_email_service() -> Optional[EmailService]:
    """获取邮件服务实例"""
    if email_service is None:
        init_email_service()
    return email_service


async def send_verification_email(email: EmailStr, username: str, code: str) -> bool:
    """发送验证邮件"""
    service = get_email_service()
    if not service:
        logger.warning("Email service not available")
        return False

    subject, html, text = email_templates.verification_email(username, code)
    return await service.send_email(email, subject, html, text)


async def send_password_reset_email(email: EmailStr, username: str, token: str) -> bool:
    """发送密码重置邮件"""
    service = get_email_service()
    if not service:
        logger.warning("Email service not available")
        return False

    subject, html, text = email_templates.password_reset_email(username, token)
    return await service.send_email(email, subject, html, text)


async def send_team_invitation_email(
    email: EmailStr, inviter_name: str, team_name: str, token: str, role: str = "member"
) -> bool:
    """发送团队邀请邮件"""
    service = get_email_service()
    if not service:
        logger.warning("Email service not available")
        return False

    subject, html, text = email_templates.team_invitation_email(
        inviter_name, team_name, token, role
    )
    return await service.send_email(email, subject, html, text)
