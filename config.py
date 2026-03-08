import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", 0))

# TimeWeb Cloud
TIMEWEB_API_TOKEN = os.getenv("TIMEWEB_API_TOKEN")
TIMEWEB_API_URL = "https://api.timeweb.cloud/api/v1"

# PolzaAI
POLZAAI_API_KEY = os.getenv("POLZAAI_API_KEY")
POLZAAI_USER_ID = os.getenv("POLZAAI_USER_ID")
POLZAAI_API_URL = os.getenv("POLZAAI_API_URL", "https://polza.ai/api/v1")

# Yandex Webmaster
YANDEX_OAUTH_TOKEN = os.getenv("YANDEX_OAUTH_TOKEN")
YANDEX_USER_ID = os.getenv("YANDEX_USER_ID")
YANDEX_HOST_ID = os.getenv("YANDEX_HOST_ID")
YANDEX_API_URL = "https://api.webmaster.yandex.net/v4"

# Пороги уведомлений
TIMEWEB_BALANCE_THRESHOLD = float(os.getenv("TIMEWEB_BALANCE_THRESHOLD", 50))
TIMEWEB_RUNWAY_HOURS_THRESHOLD = int(os.getenv("TIMEWEB_RUNWAY_HOURS_THRESHOLD", 24))
POLZAAI_BALANCE_THRESHOLD = float(os.getenv("POLZAAI_BALANCE_THRESHOLD", 50))

# Расписание
REPORT_HOUR = int(os.getenv("REPORT_HOUR", 9))
REPORT_MINUTE = int(os.getenv("REPORT_MINUTE", 0))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))  # минуты
