import discord

import DiceRoll
import Initiative
import APIRequest
import Spells
import Skills

from discord.ext import commands
from discord.utils import get

#cl = discord.Client()
client = commands.Bot(command_prefix = '$')
client.remove_command("help")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.group(pass_context = True)
async def help(ctx):
	if ctx.invoked_subcommand is None:
		description = "$help - Lists all available bot commands."
		description += "\n" + "$roll - Rolls dice given format `#d#`. Can add and subtract multiple values and rolls."
		description += "\n" + "$spell - Returns information for the given spell."
		description += "\n" + "$feature|skill - Returns information for the given feature."
		description += "\n" + "$init - Allows for adding to and the display of an ordered initiative list."
		description += "\n" + "$ping - Test command that gives the bot\'s latency time."

		embed = discord.Embed(color = 0x555555, title = "Rune Master Commands", description = description)
		await ctx.send(embed = embed)

@help.command(pass_context = True, aliases = ["initiative"])
async def init(ctx):
	description = "`$init print|display`"
	description += "\n" + "`$init print|display <display numbers>`"
	description += "\n" + "`$init print|display <channel ID> <display numbers>`"
	description += "\n" + "Prints the initiative list. If a channel ID is provided, prints into the designated channel."
	description += "\n" + "If `<display numbers>` is `true`, initiative numbers will be displayed. By default, this is disabled."
	description += "\n\n" + "`$init clear|empty`"
	description += "\n" + "Removes all entries from the initiative list."
	description += "\n\n" + "`$init <name> <value>`"
	description += "\n" + "Adds entry to initiative list with name `<name>` and value `<value>`. `<value>` must be an integer."

	embed = discord.Embed(color = 0x555555, title = "Rune Master Command - $init", description = description)
	await ctx.send(embed = embed)

@client.command(pass_context = True)
async def ping(ctx):
	await ctx.send("Pong! Latency: {} ms".format(round(client.latency, 1)))

@client.command(pass_context = True)
async def roll(ctx, *args):
	roll_string = ""
	for item in args:
		roll_string += item
	await ctx.send(embed = DiceRoll.roll_dice_embed(roll_string))

@client.command(pass_context = True, aliases = ["spells"])
async def spell(ctx, *args):
	spell_string = ""
	for i, item in enumerate(args):
		spell_string += item.lower().capitalize()
		if i < len(args) - 1:
			spell_string += " "
	await ctx.send(embed = Spells.get_spell(spell_string))

@client.command(pass_context = True, aliases = ["skills","feature","features"])
async def skill(ctx, *args):
	skill_string = ""
	for i, item in enumerate(args):
		skill_string += item.lower().capitalize()
		if i < len(args) - 1:
			skill_string += " "
	await ctx.send(embed = Skills.get_skill(skill_string))

@client.command(pass_context = True, aliases = ["initiative"])
async def init(ctx, *args):
	# Print/display
	if args[0].lower() == "print" or args[0].lower() == "display":
		# Get inputs
		display_numbers = False
		channel_id = ""
		try:
			if args[1].lower() == "true":
				display_numbers = True
			elif args[1].lower() != "false":
				channel_id = args[1]
				if args[2].lower() == "true":
					display_numbers = True
		except:
			None
		# Check which channel to send to, and print in appropriate channel
		try:
			if bool(channel_id):
				if len(Initiative.Init_List.list) > 0:
					channel = client.get_channel(int(channel_id))
					await channel.send(embed = Initiative.print_list(display_numbers))
					embed = discord.Embed(color = 0x0080ff)
					embed.add_field(name = "Success", value = "Successfully printed initiative list in channel \"{0}\"".format(channel.name), inline = False)
					await ctx.send(embed = embed)
				else:
					await ctx.send(embed = Initiative.print_list(display_numbers))
			else:
				await ctx.send(embed = Initiative.print_list(display_numbers))
		except:
			print("Failed to send message to channel {channel}".format(str(channel_id)))

	# Clear list
	elif args[0].lower() == "clear" or args[0].lower() == "empty":
		await ctx.send(embed = Initiative.clear())

	# Add to list
	else:
		if len(args) > 1:
			try:
				init = 0
				name = ""
				for i, item in enumerate(args):
					if i == len(args) - 1:
						init = int(item)
					else:
						name += item + " "
				name = name.strip()
				await ctx.send(embed = Initiative.add_initiative(init, name))
			except:
				embed = discord.Embed(color=0xff0000)
				embed.add_field(name = "Invalid Arguments", value = "Please input initiatives using the format `$init <name> <value>`", inline = False)
				await ctx.send(embed = embed)
		else:
			embed = discord.Embed(color=0xff0000)
			embed.add_field(name = "Invalid Arguments", value = "Please input initiatives using the format `$init <name> <value>`", inline = False)
			await ctx.send(embed = embed)

# Access code removed for security purposes
client.run("")