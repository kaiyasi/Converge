import threading
from main import bot, run_discord_bot

# 當 gunicorn 啟動時執行
def on_starting(server):
    # 啟動 Discord bot
    discord_thread = threading.Thread(target=run_discord_bot, daemon=True)
    discord_thread.start()

# gunicorn 設定
bind = "0.0.0.0:10000"
workers = 1  # 使用單一 worker
worker_class = "gevent"  # 使用 gevent worker 