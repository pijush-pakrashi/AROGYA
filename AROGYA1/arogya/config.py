import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'arogya-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'arogya.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 900  # 15 minutes session timeout

    # ── Gmail SMTP Configuration ────────────────────────────────────
    # 1. Go to https://myaccount.google.com/apppasswords
    # 2. Sign in, choose App: "Mail", Device: "Windows Computer"
    # 3. Copy the 16-character App Password and paste it below.
    MAIL_SERVER   = 'smtp.gmail.com'
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'YOUR_GMAIL@gmail.com')  # <-- change this
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'YOUR_APP_PASSWORD')      # <-- change this
    MAIL_FROM     = os.environ.get('MAIL_USERNAME', 'YOUR_GMAIL@gmail.com')   # <-- change this
