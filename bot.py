import discord
from discord.ext import commands, tasks
import os
import json
import random
from dotenv import load_dotenv

from flask import Flask
from threading import Thread

# ---------------- WEB SERVER ДЛЯ RENDER ----------------

app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------- DISCORD BOT ----------------

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

with open("questions.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

used_questions = []

@bot.event
async def on_ready():
    print(f"✅ Бот запущен: {bot.user}")
    if not send_question.is_running():
        send_question.start()

@tasks.loop(minutes=30)
async def send_question():
    if not bot.guilds:
        return

    question = get_question()

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(f"💬 **Вопрос дня:**\n{question}")
                break

def get_question():
    global used_questions

    if len(used_questions) == len(questions):
        used_questions = []

    available = [q for q in questions if q not in used_questions]

    question = random.choice(available)
    used_questions.append(question)

    return question

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

keep_alive()
bot.run(TOKEN)
