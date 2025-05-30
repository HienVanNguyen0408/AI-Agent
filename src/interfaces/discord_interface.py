import discord
from discord.ext import commands
from agent.agent import get_ai_answer
from config.config import load_config

config = load_config()
if not config:
    raise ValueError(
        "❌ Không tìm thấy cấu hình Discord. Vui lòng kiểm tra lại file config."
    )
discord_config = config.get("discord", {})
if not discord_config:
    raise ValueError(
        "❌ Không tìm thấy cấu hình Discord trong file config. Vui lòng kiểm tra lại file config."
    )

if not discord_config.get("token"):
    raise ValueError(
        "❌ Không tìm thấy token Discord trong cấu hình. Vui lòng kiểm tra lại file config."
    )

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    allowed_channel_ids_str = discord_config.get("allowed_channel_ids", [])
    if not allowed_channel_ids_str:
        print("❌ Không có danh sách channel được phép trong cấu hình Discord.")
        return

    allowed_channel_ids = [
        int(cid.strip()) for cid in f"{allowed_channel_ids_str}".split(",")
    ]
    if not isinstance(allowed_channel_ids, list):
        allowed_channel_ids = []

    # Không xử lý nếu không đúng channel hoặc không có danh sách channel được phép
    if not allowed_channel_ids or message.channel.id not in allowed_channel_ids:
        return

    await message.channel.typing()
    try:
        answer = get_ai_answer(message.content)
        if len(answer) >= 2000:
            with open("answer.md", "w", encoding="utf-8") as f:
                f.write(answer)
            await message.channel.send(
                "📄 Trả lời quá dài, vui lòng xem file đính kèm:",
                file=discord.File("answer.md"),
            )
        else:
            await message.channel.send(answer)

    except Exception as e:
        await message.channel.send(f"❌ Lỗi khi xử lý câu hỏi: {e}")


def start_run_discord():
    """Khởi chạy bot Discord để tiếp nhận prompt"""
    discord_token = discord_config.get("token", "")
    if not discord_token:
        raise ValueError(
            "❌ Không tìm thấy token Discord trong cấu hình. Vui lòng kiểm tra lại file config."
        )
    client.run(discord_token)
