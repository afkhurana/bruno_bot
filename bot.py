# <:thinking:263a7f4eeb6f69e46d969fa479188592>



# bot.py
import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import re
import json
import datetime
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

VERBOSE=eval(os.getenv("VERBOSE"))





#initialize globals
glob_guild = None
glob_goodmorning_channel = None
if "debug" in VERBOSE:
	glob_test = None


#initialize client
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
# @commands.bot_has_permissions(manage_nicknames=True)
async def on_ready():
	#set globs
	global glob_guild
	global glob_goodmorning_channel

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
			break
	if "debug" in VERBOSE:
		pass

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


@bot.listen('on_message')
async def listen_for_goodmorning(message):
	guild = message.guild

	if message.is_system():
		return

	if "good morning" in message.content.lower():
		await message.add_reaction("\N{HEAVY BLACK HEART}")
		await message.add_reaction("\N{BEAR FACE}")




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
		if datetime.datetime.now().hour == 9:
			print("Entering goodmorning loop")
			break
		await asyncio.sleep(10)


bot.run(DISCORD_TOKEN)
