from flask import Flask, request
from threading import Thread
import subprocess
import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

# Serve homepage
@app.route('/')
def index():
    return open("upload.html").read()

# Upload bot route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('botfile')
        if file and file.filename.endswith('.py'):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            # Run bot in background
            subprocess.Popen(["python", filepath])
            return "✅ Bot uploaded and running!"
        return "❌ Invalid file"
    else:
        return "Use the upload form to POST a bot file."

# Run Flask server in a thread (keeps it alive)
def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# -------------------------
# Start web server
keep_alive()

# -------------------------
# Optional: run default bot directly here (replace TOKEN)
import discord
from discord.ext import commands
import random
import json

# ---------- Discord Bot ----------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

points_data = {}
active_questions = {}

def save_points():
    with open("points.json", "w") as f:
        json.dump(points_data, f)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def math(ctx):
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    op = random.choice(["+", "-", "*"])
    answer = eval(f"{a}{op}{b}")
    active_questions[ctx.author.id] = answer
    await ctx.send(f"🧮 **Math Question**\nWhat is **{a} {op} {b}** ?")

@bot.command()
async def answer(ctx, *, user_answer):
    correct = active_questions.get(ctx.author.id)
    if correct is None:
        await ctx.send("❌ You don’t have an active math question.")
        return
    try:
        user_answer = float(user_answer.strip())
    except ValueError:
        await ctx.send("❌ Please type a valid number!")
        return
    if float(user_answer) == float(correct):
        uid = str(ctx.author.id)
        points_data[uid] = points_data.get(uid, 0) + 10
        save_points()
        del active_questions[ctx.author.id]
        await ctx.send(f"✅ Correct! You earned **10 points**\n🏆 Total: **{points_data[uid]}**")
    else:
        await ctx.send("❌ Wrong answer. Try again!")

@bot.command(name="points")
async def points_command(ctx):
    uid = str(ctx.author.id)
    await ctx.send(f"🪙 **Your points:** {points_data.get(uid, 0)}")

@bot.command()
async def leaderboard(ctx):
    if not points_data:
        await ctx.send("No points yet 😴")
        return
    sorted_users = sorted(points_data.items(), key=lambda x: x[1], reverse=True)
    text = "🏆 **Leaderboard**\n"
    for i, (uid, score) in enumerate(sorted_users[:10], start=1):
        try:
            user = await bot.fetch_user(int(uid))
            text += f"{i}. {user.name} — {score} points\n"
        except:
            text += f"{i}. Unknown User — {score} points\n"
    await ctx.send(text)

# -------------------------
# Start Discord bot
import os
TOKEN = os.getenv("DISCORD_TOKEN")  # safer to use env variable
bot.run(TOKEN)
