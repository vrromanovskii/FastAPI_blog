import os
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

# Загружаем переменные
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "").strip()
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "").strip()
MAIL_FROM = os.getenv("MAIL_FROM", "").strip()
MAIL_PORT = int(os.getenv("MAIL_PORT", "465"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.yandex.ru").strip()

# Для Яндекс.Почты используем SSL (STARTTLS = False, SSL_TLS = True)
MAIL_STARTTLS = False
MAIL_SSL_TLS = True

# Проверяем, все ли переменные заполнены
if not all([MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM]):
    print("WARNING: Email credentials not set. Email sending disabled.")


    async def send_welcome_email(email: str, username: str):
        print(f"[MOCK] Would send welcome email to {email} (user: {username})")
else:
    # Правильная конфигурация для fastapi-mail
    conf = ConnectionConfig(
        MAIL_USERNAME=MAIL_USERNAME,
        MAIL_PASSWORD=MAIL_PASSWORD,
        MAIL_FROM=MAIL_FROM,
        MAIL_PORT=MAIL_PORT,
        MAIL_SERVER=MAIL_SERVER,
        MAIL_STARTTLS=MAIL_STARTTLS,
        MAIL_SSL_TLS=MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )


    async def send_welcome_email(email: str, username: str):
        """Отправляет приветственное письмо после регистрации"""
        html = f"""
        <html>
        <body>
            <h2>Добро пожаловать, {username}!</h2>
            <p>Вы успешно зарегистрировались на нашем сервисе Marketplace Blog.</p>
            <p>Теперь вы можете создавать и управлять своими публикациями.</p>
            <br>
            <p>С уважением,<br>Команда Marketplace Blog</p>
        </body>
        </html>
        """

        message = MessageSchema(
            subject="Добро пожаловать на Marketplace Blog",
            recipients=[email],
            body=html,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        print(f"Welcome email sent to {email}")