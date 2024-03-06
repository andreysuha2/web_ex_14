from fastapi_mail import MessageSchema
from app.mail import SendMail
from users.auth import auth

class ConfirmationEmail(SendMail):
    subject = 'Please confirm your email address'
    template = "confirm_email.html"

    async def create_message(self, **body) -> MessageSchema:
        body["token"] = await auth.token.create_email_confirm({"sub": self.email})
        return await super().create_message(**body)