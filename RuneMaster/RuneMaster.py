import discord

import DiceRoll
import Mode
import Initiative
import APIRequest
import Spells
import Enchantments
import Skills
import Items
import Spellcasting
import Conditions
import Monsters

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
		description += "\n" + "$mode - Sets the bot mode. Use `$help mode` for more details."
		description += "\n" + "$roll - Rolls dice given format `#d#`. Can add and subtract multiple values and rolls."
		description += "\n" + "$spell - Returns information for the given spell."
		description += "\n" + "$feature|skill - Returns information for the given feature."
		description += "\n" + "$item - Returns information for the given item (weapons and armor only)."
		description += "\n" + "$condition - Returns information for the given status condition."
		description += "\n" + "$monster - Returns stats and information for the given monster."
		description += "\n" + "$init - Allows for adding to and the display of an ordered initiative list."
		description += "\n" + "$enchant - Returns information for the given enchantment. Requires homebrew bot mode."
		description += "\n" + "$ping - Test command that gives the bot\'s latency time."

		embed = discord.Embed(color = 0x555555, title = "Rune Master Commands", description = description)
		await ctx.send(embed = embed)

@client.command(pass_context = True)
async def ping(ctx):
	await ctx.send("Pong! Latency: {} ms".format(round(client.latency, 1)))

# ---------------------------------------------------------------------------------------

@client.command(pass_context = True)
async def roll(ctx, *args):
	roll_string = ""
	for item in args:
		roll_string += item
	await ctx.send(embed = DiceRoll.roll_dice_embed(roll_string))

# ---------------------------------------------------------------------------------------

@client.command(pass_context = True, aliases = ["spells"])
async def spell(ctx, *args):
	spell_string = combine_args(*args)
	await ctx.send(embed = Spells.get_spell(spell_string))

# ---------------------------------------------------------------------------------------

@client.command(pass_context = True, aliases = ["skills","feature","features"])
async def skill(ctx, *args):
	skill_string = combine_args(*args)
	await ctx.send(embed = Skills.get_skill(skill_string))

# ---------------------------------------------------------------------------------------

@client.command(pass_context = True, aliases = ["items","equipment"])
async def item(ctx, *args):
	item_string = combine_args(*args)
	await ctx.send(embed = Items.get_item(item_string))

# ---------------------------------------------------------------------------------------

@client.command(pass_context = True)
async def condition(ctx, *args):
	cond_name = combine_args(*args)
	await ctx.send(embed = Conditions.get_condition(cond_name))

# ---------------------------------------------------------------------------------------

@client.command(pass_context = True)
async def spellcasting(ctx, *args):
	name_string = combine_args(*args)
	await ctx.send(embed = Spellcasting.get_spellcasting_info(name_string))

# ---------------------------------------------------------------------------------------

@help.command(pass_context = True, aliases = ["monsters"])
async def monster(ctx):
	description = "`$monster <monster name>`\n`$monster stats <monster name>`"
	description += "\n" + "Prints stats of the given monster."
	description += "\n\n" + "`$monster abilities <monster name>`"
	description += "\n" + "Prints special abilities of the given monster."
	description += "\n\n" + "`$monster actions|attacks <monster name>`"
	description += "\n" + "Prints actions and legendary actions (if any) of the given monster."
	description += "\n\n" + "`$monster all <monster name>`"
	description += "\n" + "Prints stats, abilites, and actions of the given monster."
	description += "\n\n" + "(\"DM\" or \"Dungeon Master\" role is required to use this command)"

	embed = discord.Embed(color = 0x555555, title = "Rune Master Command - $monster", description = description)
	await ctx.send(embed = embed)

@client.command(pass_context = True, aliases = ["monsters"])
async def monster(ctx, *args):
	if check_perms(ctx):
		#try:
		lower = args[0].lower()
		if lower == "abilities" or lower == "ability":
			monster_string = combine_args(*args, ignore_first = True)
			await ctx.send(embed = Monsters.get_abilities(monster_string))
		elif lower == "actions" or lower == "action" or lower == "attacks" or lower == "attack":
			monster_string = combine_args(*args, ignore_first = True)
			await ctx.send(embed = Monsters.get_actions(monster_string))
		elif lower == "stats":
			monster_string = combine_args(*args, ignore_first = True)
			await ctx.send(embed = Monsters.get_monster_stats(monster_string))
		elif lower == "all":
			monster_string = combine_args(*args, ignore_first = True)
			embed_stats = Monsters.get_monster_stats(monster_string)
			if embed_stats.title != "Attempting to Get Info":
				await ctx.send(embed = embed_stats)
				await ctx.send(embed = Monsters.get_abilities(monster_string))
				await ctx.send(embed = Monsters.get_actions(monster_string))
			else:
				await ctx.send(embed = embed_stats)
		else:
			monster_string = combine_args(*args)
			embed_stats = Monsters.get_monster_stats(monster_string)
			if embed_stats.title != "Attempting to Get Info":
				await ctx.send(embed = embed_stats)
				await ctx.send(embed = Monsters.get_abilities(monster_string))
				await ctx.send(embed = Monsters.get_actions(monster_string))
			else:
				await ctx.send(embed = embed_stats)
		#except:
		#	description = "There was an error with retrieving the data from the API:\n"
		#	description += "Something is missing from the API, and the data cannot be retrieved properly!"
		#	embed = discord.Embed(color = 0xff0000, title = "Attempting to Get Info", description = description)
		#	await ctx.send(embed = embed)
	else:
		await ctx.send(embed = insufficient_perms())

# ---------------------------------------------------------------------------------------

@help.command(pass_context = True, aliases = ["initiative"])
async def init(ctx):
	description = "`$init print|display`"
	description += "\n" + "`$init print|display <display numbers>`"
	description += "\n" + "`$init print|display <channel ID> <display numbers>`"
	description += "\n" + "Prints the initiative list. If a channel ID is provided, prints into the designated channel."
	description += "\n" + "If `<display numbers>` is `true`, initiative numbers will be displayed. By default, this is disabled."
	description += "\n" + "(\"DM\" or \"Dungeon Master\" role is required to print with numbers)"
	description += "\n\n" + "`$init shuffle`"
	description += "\n" + "Shuffles the order of all initiative items with the same value"
	description += "\n\n" + "`$init clear|empty`"
	description += "\n" + "Removes all entries from the initiative list."
	description += "\n\n" + "`$init remove <name>`"
	description += "\n" + "Removes entry with name `<name>` from the initiative list, if it exists."
	description += "\n\n" + "`$init <name> <value>`"
	description += "\n" + "Adds entry to initiative list with name `<name>` and value `<value>`. `<value>` must be an integer."
	description += "\n" + "Alternatively, `<value>` can be `auto+#` or `auto-#` (no spaces) to automatically roll a d20 with a modifier, where `#` is any integer."
	description += "\n\n" + "`init title <title>`"
	description += "\n" + "Sets a title for the initiative list when printing."
	description += "\n" + "Resets when initiative list becomes empty."
	description += "\n\n" + "(\"DM\" or \"Dungeon Master\" role is required to use this command)"

	embed = discord.Embed(color = 0x555555, title = "Rune Master Command - $init", description = description)
	await ctx.send(embed = embed)

@client.command(pass_context = True, aliases = ["initiative"])
async def init(ctx, *args):
	# Check permissions
	if not check_perms(ctx):
			await ctx.send(embed = insufficient_perms())
			return

	# If no arguments
	if len(args) == 0:
		embed = discord.Embed(color=0xff0000, title = "Invalid Arguments", description = "Please input initiatives using the format `$init <name> <value>`\nOr use `$help init` for detailed help")
		await ctx.send(embed = embed)

	# Print/display
	elif args[0].lower() == "print" or args[0].lower() == "display":
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

	# Shuffle list
	elif args[0].lower() == "shuffle":
		Initiative.Init_List.list = Initiative.shuffle_list(Initiative.Init_List.list)
		embed = discord.Embed(color = 0x0080ff, title = "Success", description = "Successfully shuffled initiative list")
		await ctx.send(embed = embed)

	# Clear list
	elif args[0].lower() == "clear" or args[0].lower() == "empty":
		await ctx.send(embed = Initiative.clear())

	# Remove from list
	elif args[0].lower() == "remove":
		name = ""
		for i, item in enumerate(args):
			if i == 0:
				continue
			elif i == len(args) - 1:
				name += item
			else:
				name += item + " "
		await ctx.send(embed = Initiative.remove_initiative(name))

	# Set list title
	elif args[0].lower() == "title":
		title_string = ""
		for i, item in enumerate(args):
			if i != 0:
				title_string += item + " "
		Initiative.Init_List.title = title_string
		embed = discord.Embed(Color=0x00ff80, title = "Success", description = "Successfully changed initiative list title to `{}`".format(title_string))
		await ctx.send(embed = embed)

	# Add to list
	else:
		if len(args) > 1:
			try:
				init = 0
				name = ""
				for i, item in enumerate(args):
					if i == len(args) - 1:
						if "auto" in item:
							init = DiceRoll.init_auto_dice_roll(item)
						else:
							init = int(item)
					else:
						name += item + " "
				name = name.strip()
				await ctx.send(embed = Initiative.add_initiative(init, name))
			except:
				embed = discord.Embed(color=0xff0000, title = "Invalid Arguments", description = "Please input initiatives using the format `$init <name> <value>`\nOr use `$help init` for detailed help")
				await ctx.send(embed = embed)
		else:
			embed = discord.Embed(color=0xff0000, title = "Invalid Arguments", description = "Please input initiatives using the format `$init <name> <value>`\nOr use `$help init` for detailed help")
			await ctx.send(embed = embed)

# ---------------------------------------------------------------------------------------

@client.command(pass_context = True, aliases = ["enchantment"])
async def enchant(ctx, *args):
	enchant_string = combine_args(*args)
	await ctx.send(embed = Enchantments.get_enchantment(enchant_string))

# ---------------------------------------------------------------------------------------

@help.command(pass_context = True)
async def mode(ctx):
	description = "Current Mode: `{}`".format(Mode.Mode.current)
	description += "\n\n" + "3 Modes Available:"
	description += "\n" + "`Vanilla`"
	description += "\n" + "Standard D&D 5e only, with no homebrew."
	description += "\n\n" + "`Limited`"
	description += "\n" + "Standard D&D 5e with Runic Cataclysm spells and monsters."
	description += "\n\n" + "`Homebrew`"
	description += "\n" + "Standard D&D 5e with all of Runic Cataclysm."

	embed = discord.Embed(color = 0x555555, title = "Rune Master Command - $mode", description = description)
	await ctx.send(embed = embed)

@client.command(pass_context = True)
async def mode(ctx, *args):
	if check_perms(ctx):
		try:
			if len(args) == 0:
				await ctx.send("Bot mode is currently set to `{}`.".format(Mode.Mode.current))
				return

			arg = args[0].lower()
			if arg == "vanilla":
				if Mode.Mode.current != "vanilla":
					Mode.Mode.current = "vanilla"
					await ctx.send("Bot mode set to `vanilla`.")
				else:
					await ctx.send("Bot mode is already set to `vanilla`!")
			elif arg == "homebrew":
				if Mode.Mode.current != "homebrew":
					Mode.Mode.current = "homebrew"
					await ctx.send("Bot mode set to `homebrew`.")
				else:
					await ctx.send("Bot mode is already set to `homebrew`!")
			elif arg == "limited":
				if Mode.Mode.current != "limited":
					Mode.Mode.current = "limited"
					await ctx.send("Bot mode set to `limited`.")
				else:
					await ctx.send("Bot mode is already set to `limited`!")
			else:
				raise SyntaxError
		except:
			await ctx.send("Please enter a valid argument!")

	else:
		await ctx.send(embed = insufficient_perms())

# ---------------------------------------------------------------------------------------

#@client.command(pass_context = True)
#async def test(ctx, *args):
#	await ctx.send(str(Spells.check_rc_spells("Blinding Light")))

def check_perms(ctx):
	id1 = discord.utils.get(ctx.guild.roles, name="DM")
	id2 = discord.utils.get(ctx.guild.roles, name="Dungeon Master")
	if id1 in ctx.author.roles or id2 in ctx.author.roles:
		return True
	return False

def insufficient_perms():
	description = "The \"DM\" or \"Dungeon Master\" role is required to use this command."
	embed = discord.Embed(color = 0xff0000, title = "Insufficient Permissions", description = description)
	return embed

# ---------------------------------------------------------------------------------------

def combine_args(*args, ignore_first = False):
	output = ""
	for i, item in enumerate(args):
		if ignore_first and i == 0:
			continue
		if item.lower() == "of":
			output += item.lower()
		else:
			output += item.lower().capitalize()
		if i < len(args) - 1:
			output += " "
	return output

# Access code removed for security purposes
client.run("")