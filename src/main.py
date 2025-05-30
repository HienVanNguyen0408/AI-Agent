# main.py
from interfaces.discord_interface import start_run_discord

if __name__ == "__main__":
    try:
        start_run_discord()

    except Exception as e:
        print(f"⚠️ Đã xảy ra lỗi: {e}")
