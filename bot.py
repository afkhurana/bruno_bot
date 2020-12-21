# <:thinking:263a7f4eeb6f69e46d969fa479188592>



# bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import re
import json
import pprint as pp


intents = discord.Intents()
intents = intents.all()


load_dotenv()
DISCORD_TOKEN=os.getenv("DISCORD_TOKEN")
DISCORD_GUILD=os.getenv("DISCORD_GUILD")

SAY_PLEASE=os.getenv("SAY_PLEASE")

VERBOSE=eval(os.getenv("VERBOSE"))


with open("message_ids.json", newline='') as f:
	message_ids = json.load(f)


#initialize globals
glob_guild = None
glob_members = None
if "debug" in VERBOSE:
	glob_test = None


#initialize client
bot = commands.Bot(command_prefix="bruno!", intents=intents)





@bot.event
# @commands.bot_has_permissions(manage_nicknames=True)
async def on_ready():
	#set globs
	for guild in bot.guilds:
		if guild.name == DISCORD_GUILD:
			glob_guild = guild
			print(f'{bot.user} is listening to guild {guild.name}')
			break
	if "debug" in VERBOSE:
		pass



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
	with open("message_ids.json", "w") as f:
		json.dump(message_ids, f, indent=4)




@bot.event
async def on_reaction_add(reaction, user):
	guild = reaction.message.guild
	
	if reaction.message.id in message_ids["pronouns"]:
		role = None
		if reaction.emoji == "\N{FULL MOON SYMBOL}":
			role = "he/him"
		elif reaction.emoji == "\N{BLACK SUN WITH RAYS}":
			role = "she/her"
		elif reaction.emoji == "\N{WHITE MEDIUM STAR}":
			role = "they/them"
		role = discord.utils.get(guild.roles, name=role)
		member = [m for m in guild.members if m.id == user.id][0]
		await member.add_roles(role, reason="Pronouns by Bruno!")






bot.run(DISCORD_TOKEN)