import threading
import asyncio
from flask import Flask
from bot import main  # ваш основной бот

app = Flask(__name__)

@app.route("/")
def health():
    return "OK", 200

def run_bot():
    asyncio.run(main())

# Запуск бота в отдельном потоке
thread = threading.Thread(target=run_bot, daemon=True)
thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

И добавьте `flask` в `requirements.txt`:
```
aiogram==3.7.0
aiohttp==3.9.5
apscheduler==3.10.4
python-dotenv==1.0.1
flask==3.0.3
