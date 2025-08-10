import requests
from .config import os

def notify_text(msg: str):
    # placeholder: print for now. Later you can add Telegram or Slack.
    print("[NOTIFY]", msg)
