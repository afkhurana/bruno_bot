import os
import sys
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
import random
import hashlib
import smtplib, ssl

import logging

logging.basicConfig(filename='bruno.log', encoding='utf-8')
logger = logging.getLogger('bruno_logger')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)



cwd = os.path.dirname(os.path.realpath(__file__))
message_ids_path = os.path.join(cwd, "message_ids.json")
roles_path = os.path.join(cwd, "roles.json")
info_path = os.path.join(cwd, "info.json")




load_dotenv()
DISCORD_TOKEN=os.getenv("DISCORD_TOKEN")
DISCORD_GUILD=os.getenv("DISCORD_GUILD")

SAY_PLEASE=os.getenv("SAY_PLEASE")

GOODMORNING_CHANNEL_NAME=os.getenv("GOODMORNING_CHANNEL")
INTRODUCTIONS_CHANNEL_NAME=os.getenv("INTRODUCTIONS_CHANNEL")

# load configs
with open(os.path.join("configs", "email_info.json")) as f:
	email_info = json.load(f)
with open(os.path.join("configs", "hi_strings.json")) as f:
	hi_strings = json.load(f)["hi_strings"]



# initialize client
intents = discord.Intents()
intents = intents.all()
bot = commands.Bot(command_prefix="bruno!", intents=intents)



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
			global glob_guild
			glob_guild = guild
			logger.info(f'{bot.user} is listening to guild {guild.name}')
			break
	for channel in glob_guild.channels:
		if channel.name == GOODMORNING_CHANNEL_NAME:
			global glob_goodmorning_channel
			glob_goodmorning_channel = channel
			logger.info(f'{bot.user} wants to say Good Morning! in #{channel.name}')
		elif channel.name == INTRODUCTIONS_CHANNEL_NAME:
			global glob_introductions_channel
			glob_introductions_channel = channel

	message_goodmorning.start()


# general purpose functions
def check_please(func):
	async def wrapper(ctx, *args):
		if SAY_PLEASE:
			if len(args[0]) == 0:
				await ctx.send("Say please!")
				
			elif args[0][-1].lower() != "please":
				await ctx.send("Say please!")

			else:
				await func(ctx, args)
	return wrapper


# ROLES/INFO
def load_roles():
	global roles_dict
	with open(roles_path, newline='') as f:
		roles_dict = json.load(f)
load_roles()

def load_info():
	global info_dict
	with open(info_path, newline='') as f:
		info_dict = json.load(f)
load_info()

@bot.command(name="load")
@check_please
async def load(ctx, *args):
	if args[0][0] == "roles":
		load_roles()
	elif args[0][0] == "info":
		load_info()

@bot.command(name="role")
@check_please
async def send_role_message(ctx, *args):
	load_roles()
	role_type = args[0][0]
	if role_type not in list(roles_dict.keys()):
		await ctx.send("Pardon me, didn't quite get that.")
		return
	# command success
	# send message
	message_content = roles_dict[role_type]["message"]
	if not isinstance(message_content, str):
		message_content = f"**React here for {role_type} role!**"
		if roles_dict[role_type]["unicode"]:
			for emoji, role_name in roles_dict[role_type]["emojis"].items():
				message_content += f"\n{emoji}: {role_name}"
		else:
			for emoji_name, role_name in roles_dict[role_type]["emojis"].items():
				emoji = get(bot.emojis, name=emoji_name)			
				message_content += f"\n<:{emoji_name}:{emoji.id}>: {role_name}"
	message = await ctx.send(message_content)
	# add reactions
	if roles_dict[role_type]["unicode"]:
		for emoji, role_name in roles_dict[role_type]["emojis"].items():
			await message.add_reaction(emoji)
	else:
		for emoji_name, role_name in roles_dict[role_type]["emojis"].items():
			emoji = get(bot.emojis, name=emoji_name)
	# dump id
	try:
		message_ids[role_type].append(message.id)
	except KeyError:
		message_ids[role_type] = [message.id]
	dump_ids()
	return

@bot.listen('on_raw_reaction_add')
async def listen_for_role(payload):
	emoji = str(payload.emoji)
	member = payload.member
	message_id = payload.message_id
	guild = member.guild

	if member.bot:
		return	
	verified_role = get(guild.roles, name="Verified Brownie")
	if verified_role not in member.roles:
		return
	
	# check which role
	load_roles()
	role_type = None
	for check_role_type, role_message_ids in message_ids.items():
		if message_id in role_message_ids:
			role_type = check_role_type
	if role_type is None:
		return
	role_name = roles_dict[role_type]["emojis"][emoji]
	role = get(guild.roles, name=role_name)
	await member.add_roles(role, reason="Roles by Bruno!")
	logger.info(f"Gave member {member} role {role_type} {role_name}")

@bot.command(name="info")
@check_please
async def send_info_message(ctx, *args):
	load_info()
	info_type = args[0][0]
	if info_type not in list(info_dict.keys()):
		await ctx.send("Pardon me, didn't quite get that.")
		return
	# command success
	# send message
	message_content = info_dict[info_type]["message"]
	if not isinstance(message_content, str):
		raise Exception(f"Arjun, check out the message for info.json/{info_type}")
	message = await ctx.send(message_content)
	return

@bot.command(name="goodmorning", ignore_extra=True)
@check_please
async def goodmorning(ctx, *args):
	guild = ctx.guild
	await message_goodmorning()

@bot.listen('on_message')
async def listen_for_emoji_reacts(message):
	if message.is_system():
		return
	guild = message.guild
	if "good morning" in message.content.lower():
		await message.add_reaction("\N{HEAVY BLACK HEART}")
		await message.add_reaction(get(bot.emojis, name="bruno"))
	elif "bruno" in message.content.lower():
		await message.add_reaction(get(bot.emojis, name="bruno"))
	elif "darius" in message.content.lower():
		await message.add_reaction(get(bot.emojis, name="darius"))

@tasks.loop(hours=24)
async def message_goodmorning():
	logger.info("Good morning!")
	message = await glob_goodmorning_channel.send("Good morning!")
	message_ids["goodmornings"].append(message.id)
	dump_ids()

@message_goodmorning.before_loop
async def before_message_goodmorning():
	logger.info("Waiting to enter goodmorning loop")
	for _ in range(60*60*24):
		if datetime.datetime.now(pytz.timezone("US/Eastern")).hour == 9:
			logger.info("Entering goodmorning loop")
			break
		await asyncio.sleep(30)

@bot.listen('on_message')
async def listen_for_introduction(message):
	if message.channel != glob_introductions_channel:
		return
	if message.is_system():
		return
	if any(hi_string in message.content.lower() for hi_string in hi_strings):
		await message.add_reaction("\N{WAVING HAND SIGN}")



# VERIFICATION

def create_verification_code(*args):
	return hashlib.md5((str(args) + email_info["secret_key"]).encode("utf-8")).hexdigest()

def send_email(address, subject, body):

	sent_from = email_info["login_info"]["username"]
	to = [address]
	message = 'Subject: {}\n\n{}'.format(subject, body)

	context = ssl.create_default_context()
	with smtplib.SMTP("smtp.gmail.com", 587) as server:
		server.starttls(context=context)
		server.login(email_info["login_info"]["username"], email_info["login_info"]["password"])
		server.sendmail(sent_from, to, message)
		server.close()


welcome_message = ("Welcome! In order to gain access to the Brown Class of 2025 Discord server, "
					"we ask that you complete a verification with your Brown email address.")
please_send_email_message = "Please send your email in the format *email@brown.edu*"
email_invalid_message = "Sorry, the email you sent was not a Brown email. Please try again."
emailed_code_message = ("I emailed you a verification code! Please send it back to me here."
						"\n(If you don't receive a code, type anything to start over)")
code_invalid_message = "Sorry, the code doesn't match. Try again!"
success_message = "Congrats! You are now a verified Brownie!"


secret_key = "foo_test"


@bot.listen('on_member_join')
async def dm_member_on_join(member):
	await member.send(welcome_message)
	await member.send(please_send_email_message)
	return


# @bot.command("verify_everyone")
# async def verify_everyone(ctx, *args):
# 	for member in glob_guild.members:
# 		await member.send(welcome_message)
# 		await member.send(please_send_email_message)
# @bot.command("verify")
# async def verify_member(ctx, *args):


@bot.command("verify")
@check_please
async def verify_me(ctx, *args):
	try:
		if args[0][0].lower().startswith('<@!'):
			user_id = int(args[0][0][3:-1])
			member = ctx.guild.get_member(user_id)
			await member.send(welcome_message)
			await member.send(please_send_email_message)
		elif args[0][0].lower() == "me":
			member = ctx.author
			await member.send(welcome_message)
			await member.send(please_send_email_message)
	except AttributeError as e:
		logger.exception(f'Error in verify_me: args {args}')


@bot.listen('on_message')
async def handle_dm(message):
	if message.guild:
		return
	if message.is_system():
		return
	if message.author.bot:
		return
	# message is DM
	last_message = await message.channel.history(limit=10).find(lambda m: m.author.id == bot.user.id)
	last_message = last_message.content
	verification_code = create_verification_code(message.author.id, secret_key)
	if last_message == please_send_email_message:
		# message is email address
		if not message.content.endswith("@brown.edu"):
			await message.channel.send(email_invalid_message)
			await message.channel.send(please_send_email_message)
		else:
			address = message.content
			subject = "Brown '25 Discord Verification Code"
			body = "Here is your verification code! Copy-paste this into your DM with Bruno (me):\n\n" + verification_code #TODO make pretty
			send_email(address, subject, body)
			await message.channel.send(emailed_code_message)
	elif last_message == emailed_code_message:
		# message is verification code
		if message.content != verification_code:
			await message.channel.send(code_invalid_message)
			await message.channel.send(please_send_email_message)
		else:
			await give_user_brown_verified_role(message.author)
			await message.channel.send(success_message)
	return

async def give_user_brown_verified_role(user):
	member = glob_guild.get_member(user.id)
	role = discord.utils.get(glob_guild.roles, name="Verified Brownie")
	await member.add_roles(role, reason="Verification by Bruno!")
	return

# END VERIFICATION


bot.run(DISCORD_TOKEN)
