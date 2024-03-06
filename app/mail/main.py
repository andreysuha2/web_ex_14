from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from app import settings
from pathlib import Path
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_EMAIL,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_SERVER,
    MAIL_FROM_NAME="Contact app",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates'
)

fm = FastMail(conf)

class SendMail():
    fm: FastMail = fm
    subtype: MessageType = MessageType.html
    subject: str
    template: str

    def __init__(self, email: EmailStr) -> None:
        self.email = email

    async def create_message(self, **body) -> MessageSchema:
        return MessageSchema(
            subject=self.subject,
            recipients=[self.email],
            template_body=body,
            subtype=self.subtype
        )

    async def __call__(self, **kwds: dict) -> None:
        try:
            message = await self.create_message(**kwds)
            await fm.send_message(message, template_name=self.template)
        except ConnectionErrors as errors:
            print(errors)