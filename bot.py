# <:thinking:263a7f4eeb6f69e46d969fa479188592>



# bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

import pprint as pp


intents = discord.Intents()
intents = intents.all()


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_NAME = os.getenv('DISCORD_GUILD')

VERBOSE = eval(os.getenv('VERBOSE'))




#initialize globals
glob_guild = None
glob_members = None
if "debug" in VERBOSE:
	glob_test = None


#initialize client
bot = commands.Bot(command_prefix="bruno!", intents=intents)


async def get_all_user_profiles(guild):
	members = guild.members
	print(members)
	for member in members:
		#DEBUG
		print(member)
		profile = await member.profile()
		print(profile)
		break


@bot.event
# @commands.bot_has_permissions(manage_nicknames=True)
async def on_ready():
	#set globs
	for guild in bot.guilds:
		if guild.name == GUILD_NAME:
			glob_guild = guild
			print(f'{bot.user} is listening to guild {guild.name}')
			break 
	#members = await glob_guild.chunk()
	#glob_members = await glob_guild.fetch_members().flatten()

	if "debug" in VERBOSE:
		pass

	await get_all_user_profiles(glob_guild)




bot.run(TOKEN)