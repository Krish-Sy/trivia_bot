import discord
from discord.ext import commands
import asyncio
from trivia_questions import questions
import os
from dotenv import load_dotenv

#loading env variables from .env files
load_dotenv()

token = os.getenv('DISCORD_BOT_TOKEN')


intents = discord.Intents.default()
intents.messages = True  # Receive messages through dms
intents.guild_messages = True  # Receive messages through channels
intents.message_content = True  # Enables access to message content


scores = {}
user_streaks = {}
current_question_index = 0

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Sorry, you don't have permission to use this command.")
    else:
        raise error


@bot.command()
@commands.has_permissions(administrator=True)
async def trivia(ctx):
    global current_question_index
    question, answer = questions[current_question_index]
    await ctx.send(question)
    
    def check(m):
        return m.author != bot.user and m.channel == ctx.channel
    

    answered_correctly = False
    while not answered_correctly:
        try:
            msg = await bot.wait_for('message', check=check, timeout=30.0)
            if msg.content.lower() == answer.lower():
                user_id = str(msg.author.id)
                scores[user_id] = scores.get(user_id, 0) + 1
                user_streaks[user_id] = user_streaks.get(user_id, 0) + 1
                if user_streaks[user_id] >= 3:
                    await ctx.send(f'🎉 {msg.author.mention} is on fire! {user_streaks[user_id]} correct answers in a row! 🎉')
                else:
                    await ctx.send(f'Correct answer {msg.author.mention}! Your score is now {scores[user_id]}. Your streak is {user_streaks[user_id]}.')
                answered_correctly = True
            else:
                user_streaks[str(msg.author.id)] = 0
                await ctx.send(f'Incorrect answer {msg.author.mention}. Try again!')

        except asyncio.TimeoutError:
            await ctx.send('Sorry, you took too long to answer.')

    current_question_index += 1
    if current_question_index >= len(questions):
        current_question_index = 0 

@bot.command()
@commands.has_permissions(administrator=True)
async def leaderboard(ctx):
    if not scores:
        await ctx.send("No scores to display yet.")
        return
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    leaderboard_msg = "**Leaderboard:**\n"
    for idx, (user_id, score) in enumerate(sorted_scores, start=1):
        user_name = await bot.fetch_user(user_id)
        leaderboard_msg += f"{idx}. {user_name} - {score}\n"
    
    await ctx.send(leaderboard_msg)

bot.run(token)
