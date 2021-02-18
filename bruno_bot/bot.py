import os
import discord
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
import re
import json
import datetime
import pytz
import asyncio
import pprint as pp




cwd = os.path.dirname(os.path.realpath(__file__))
message_ids_path = os.path.join(cwd, "message_ids.json")


intents = discord.Intents()
intents = intents.all()


load_dotenv()
DISCORD_TOKEN=os.getenv("DISCORD_TOKEN")
DISCORD_GUILD=os.getenv("DISCORD_GUILD")

SAY_PLEASE=os.getenv("SAY_PLEASE")

GOODMORNING_CHANNEL_NAME=os.getenv("GOODMORNING_CHANNEL")
INTRODUCTIONS_CHANNEL_NAME=os.getenv("INTRODUCTIONS_CHANNEL")




# load configs
with open(os.path.join("configs", "games_list.json")) as f:
	games_list = json.load(f)

with open(os.path.join("configs", "hi_strings.json")) as f:
	hi_strings = json.load(f)["hi_strings"]



# initialize client
bot = commands.Bot(command_prefix="bruno!", intents=intents)
message_ids = None



def load_ids():
	global message_ids
	with open(message_ids_path, newline='') as f:
		message_ids = json.load(f)
load_ids()
def dump_ids():
	with open(message_ids_path, "w") as f:
		json.dump(message_ids, f, indent=4)




@bot.event
async def on_ready():
	for guild in bot.guilds:
		if guild.name == DISCORD_GUILD:
			glob_guild = guild
			print(f'{bot.user} is listening to guild {guild.name}')
			break
	for channel in glob_guild.channels:
		if channel.name == GOODMORNING_CHANNEL_NAME:
			global glob_goodmorning_channel
			glob_goodmorning_channel = channel
			print(f'{bot.user} wants to say Good Morning! in #{channel.name}')
		elif channel.name == INTRODUCTIONS_CHANNEL_NAME:
			global glob_introductions_channel
			glob_introductions_channel = channel

	message_goodmorning.start()



@bot.command(name="pronouns", ignore_extra=True)
async def pronouns(ctx, *args):
	guild = ctx.guild

	if SAY_PLEASE:
		if len(args) == 0:
			await ctx.send("Say please!")
			return			
		if args[0].lower() != "please":
			await ctx.send("Say please!")
			return

	message = await ctx.send("React here for pronouns!\n\n\N{FULL MOON SYMBOL}: he/him\n\N{BLACK SUN WITH RAYS}: she/her\n\N{WHITE MEDIUM STAR}:"
		"they/them\n(message @june if you want neopronouns)")
	await message.add_reaction("\N{FULL MOON SYMBOL}")
	await message.add_reaction("\N{BLACK SUN WITH RAYS}")
	await message.add_reaction("\N{WHITE MEDIUM STAR}")

	message_ids["pronouns"].append(message.id)
	dump_ids()

@bot.listen('on_raw_reaction_add')
async def listen_for_pronouns(payload):
	emoji = str(payload.emoji)
	member = payload.member
	message_id = payload.message_id
	guild = member.guild

	if member.bot:
		return
	
	#pronouns reacts
	if message_id in message_ids["pronouns"]:
		role = None
		if emoji == "\N{FULL MOON SYMBOL}":
			role = "he/him"
		elif emoji == "\N{BLACK SUN WITH RAYS}":
			role = "she/her"
		elif emoji == "\N{WHITE MEDIUM STAR}":
			role = "they/them"
		role = discord.utils.get(guild.roles, name=role)
		# member = [m for m in guild.members if m.id == user.id][0]
		await member.add_roles(role, reason="Pronouns by Bruno!")
		print(f"Gave member {member} pronouns {role}")




@bot.command(name="games", ignore_extra=True)
async def games(ctx, *args):

	guild = ctx.guild

	if SAY_PLEASE:
		if len(args) == 0:
			await ctx.send("Say please!")
			return			
		if args[0].lower() != "please":
			await ctx.send("Say please!")
			return

	message = "React here for games roles!\n"
	for game_name, game_emoji_name in games_list.items():
		game_emoji = get(bot.emojis, name=game_emoji_name)
		message += f"\n<:{game_emoji_name}:{game_emoji.id}>: {game_name}"

	message = await ctx.send(message)
	for game_name, game_emoji_name in games_list.items():
		await message.add_reaction(get(bot.emojis, name=game_emoji_name))

	message_ids["games"].append(message.id)
	dump_ids()

@bot.listen('on_raw_reaction_add')
async def listen_for_games(payload):
	emoji = payload.emoji
	member = payload.member
	message_id = payload.message_id
	guild = member.guild

	if member.bot:
		return
	
	#pronouns reacts
	if message_id in message_ids["games"]:
		role = None
		for game_name, game_emoji_name in games_list.items():
			if emoji.name == game_emoji_name:
				role = game_name
		role = discord.utils.get(guild.roles, name=role)
		# member = [m for m in guild.members if m.id == user.id][0]
		await member.add_roles(role, reason="Games by Bruno!")
		print(f"Gave member {member} game role {role}")




@bot.command(name="dev", ignore_extra=True)
async def dev(ctx, *args):

	guild = ctx.guild

	if SAY_PLEASE:
		if len(args) == 0:
			await ctx.send("Say please!")
			return			
		if args[0].lower() != "please":
			await ctx.send("Say please!")
			return

	dev_role = discord.utils.get(guild.roles, name="bruno!dev")
	await ctx.author.add_roles(dev_role, reason="Dev_role by Bruno!")
	await ctx.message.add_reaction(get(bot.emojis, name="bruno"))
	message = "You're now a bruno dev! Check out the source code at https://github.com/afkhurana/bruno_bot"
	message = await ctx.send(message)


@bot.command(name="questionnaire", ignore_extra=True)
async def questionnaire(ctx, *args):

	guild = ctx.guild

	if SAY_PLEASE:
		if len(args) == 0:
			await ctx.send("Say please!")
			return			
		if args[0].lower() != "please":
			await ctx.send("Say please!")
			return

	dev_role = discord.utils.get(guild.roles, name="questionnaire")
	await ctx.author.add_roles(dev_role, reason="Questionnaire role by Bruno!")
	await ctx.message.add_reaction(get(bot.emojis, name="bruno"))
	message = "You're now authorized to help with Dave's questionnaire!"
	message = await ctx.send(message)





@bot.listen('on_message')
async def listen_for_goodmorning(message):
	guild = message.guild

	if message.is_system():
		return

	if "good morning" in message.content.lower():
		await message.add_reaction("\N{HEAVY BLACK HEART}")
		await message.add_reaction(get(bot.emojis, name="bruno"))

@tasks.loop(hours=24)
async def message_goodmorning():
	print("Good morning!")
	message = await glob_goodmorning_channel.send("Good morning!")
	message_ids["goodmornings"].append(message.id)
	dump_ids()

@message_goodmorning.before_loop
async def before_message_goodmorning():
	print("Waiting to enter goodmorning loop")
	for _ in range(60*60*24):
		if datetime.datetime.now(pytz.timezone("US/Eastern")).hour == 9:
			print("Entering goodmorning loop")
			break
		await asyncio.sleep(10)





@bot.listen('on_message')
async def listen_for_introduction(message):
	if message.channel != glob_introductions_channel:
		return
	if message.is_system():
		return

	if any(hi_string in message.content.lower() for hi_string in hi_strings):
		await message.add_reaction("\N{WAVING HAND SIGN}")



@bot.command("collect_bible")
async def collect_bible(ctx, *args):
	
	load_dotenv()
	ARJUN_ID=os.getenv("ARJUN_ID")

	if ctx.author.id != ARJUN_ID:
		return

	with open(os.path.join("configs", "channel_ids.json")) as f:
		if ctx.channel.id != json.load(f)["bible-discussion-study-meeting"]:
			return

	# arjun sent this message to the bible discussion channel
	pins = await ctx.channel.pins()
	for message in pins:
		screenshot = message.attachments[-1]
		path = os.path.join("screenshots", message.author.name, message.filename.split(".")[-1])
		await screenshot.save(path)
		print(f"Saved message from {message.author.name}")


bot.run(DISCORD_TOKEN)
