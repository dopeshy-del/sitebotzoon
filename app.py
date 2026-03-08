import threading
import asyncio
from flask import Flask
from bot import main

app = Flask(__name__)

@app.route("/")
def health():
    return "OK", 200

def run_bot():
    asyncio.run(main())

thread = threading.Thread(target=run_bot, daemon=True)
thread.start()
