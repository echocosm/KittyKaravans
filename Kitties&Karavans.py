# ~ ~ ~ K I T T Y ~ K A R A V A N S ~ ~ ~

# ~ ~ ~ I M P O R T S ~ ~ ~ 
try:
    import os
    import reactionmenu
    from reactionmenu import ViewMenu, ViewButton
    import json
    import subprocess
    from typing import Literal, Optional

    # Basic bot dependencies
    import discord
    from discord import app_commands
    from discord.errors import PrivilegedIntentsRequired
    from discord.ext import commands, tasks
    import platform
    import asyncio
    from threading import Thread
    #from keep_alive import keep_alive
    from dotenv import load_dotenv
    load_dotenv()

    intents = discord.Intents.all()
    intents.typing = False
    intents.guilds=True
    intents.reactions=True
    intents.presences = False
    intents.members = True
    intents.messages = True

    # Import configurations
    import configs

    # Imports for system tray icon
    from pystray import Icon, Menu, MenuItem
    from PIL import Image
    import webbrowser

    print("Imports successful.")
except ImportError as e:
    print(f"Error importing modules: {e}")

# ~ ~ ~ C R E A T E - L I F E ~ ~ ~ 

# Create a bot client with a description and a command prefix

# Your desired bot permissions
# Example: Read Messages, Send Messages, Connect to Voice
CLIENT_ID=configs.SOURCE_CLIENT
PERMISSIONS = discord.Permissions(administrator=True)
invite_url = discord.utils.oauth_url(CLIENT_ID, permissions=PERMISSIONS)

MY_GUILD = discord.Object(id=configs.SOURCE_GUILD)  # replace with your guild id

class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents,command_prefix=configs.BOT_PREFIX)
bot= MyClient(intents=intents)

@bot.event
async def on_ready():
    print('--------')
    print(' ~ ~ ~ K I T T Y ~ K A R A V A N S ~ ~ ~')
    print('--------')
    print('Discord Idle Game')
    print('--------')
    print('by echocosm')
    print('--------')
    print('Logged in as ' + bot.user.name + ' (ID:' + str(bot.user.id) + ') | Connected to ' + str(len(bot.guilds)) + ' servers: ' + ', '.join([guild.name for guild in bot.guilds]) + ' | Connected to ' + str(len(set(bot.get_all_members()))) + ' users')
    print('--------')
    print(f'Current Discord.py Version: {discord.__version__} | Current Python Version: {platform.python_version()}')
    print('--------')
    print(f'Use this link to invite {bot.user.name}:')
    print('--------')
    print(f'{invite_url}')
    print('--------')
    #await bot.change_presence(activity=discord.Game(name='all sides against the middle'))

@bot.event
async def on_interaction(interaction: discord.Interaction):
    # Handle slash command interactions here
    if interaction.type == discord.InteractionType.application_command:
        await bot.tree.dispatch_interaction(interaction)

# ~ ~ ~ M O D U L E S ~ ~ ~ 

# ~ ~ ~ C O U N T E R ~ ~ ~ 

# File path for storing user message counts

# ~ ~ L O A D ~ ~ 
# Function to load user message counts or karavans from file
def load_data(data): #data: file to load
    try:
        with open(data, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save user message counts to file
def save_data(data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file)
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")

# Dictionary to store user message counts
user_message_counts = load_data('user_message_counts.json')

@bot.event
async def on_message(message):
    print(message.author, ">", message.content)
    if message.author != bot.user:
        # Increment message count for the user
        user_id = str(message.author)
        if user_id not in user_message_counts:
            user_message_counts[user_id] = {'🫓': 0, '🍞': 0, '🥐': 0, '🥟': 0, '🍪': 0, '🍩': 0, '🧁': 0, '🍰': 0}
        # For example, to increment the count for the slot theyre on
        user_message_counts[user_id]['🍞'] += 1
        save_data(user_message_counts, "user_message_counts.json")
    await bot.process_commands(message)

# ~ ~ S H U T D O W N ~ ~ 
@bot.event
async def on_shutdown():
    save_data(user_message_counts, "user_message_counts.json")

# Module: screenshot
# Description: Takes a screenshot and sends it back
# Usage: !screenshot or !screenshot secondsToScreenshot
@bot.tree.command(name = "test", description = 'grabs all 3 displays')
#@Logger(bot)
async def test(interaction: discord.Interaction):
    await test_module.test(interaction)

# ~ ~ J O I N ~ ~ 
@bot.tree.command(name="join", description='Start a Karavan or join an existing one')
async def join(interaction: discord.Interaction, *, karavan: str, user: discord.Member):
    karavan_name = karavan.capitalize() + ' Karavan'
    existing_role = discord.utils.get(interaction.guild.roles, name=karavan_name)
    if existing_role is not None:
        role = existing_role
        print(f"Role '{karavan_name}' already exists.")
        message = f"The {role} already exists."
    else:
        try:
            role = await interaction.guild.create_role(name=karavan_name)
            print(f"Role '{karavan_name}' created successfully.")
            message = f"Created New Karavan! The {role}."
        except Exception as e:
            print(f"Error creating role: {e}")
            await interaction.response.send_message("Error creating role.")
            return
    if user is None:
        print("User not found in the guild.")
        await interaction.response.send_message("User not found in the guild.")
        return
    # Check if the user is already in the role
    if role in user.roles:
        await interaction.response.send_message(f"{user.name} is already in the {role}.")
        return
    try:
        await user.add_roles(role)
        print(f"{user.name} successfully joined the {role}.")
        message += f"\n{user.name} successfully joined the {role}."
    except Exception as e:
        print(f"Error: {e}")
        await interaction.response.send_message(f"Error adding user to the {role}.")
        return
    try:
        karavan_data = load_data('karavan_data.json')
        role_str = str(role)
        if role_str not in karavan_data:
            karavan_data[role_str] = {'members': []}
        if user.name not in karavan_data:
            karavan_data[role_str]['members'].append(str(user.name))
        save_data(karavan_data, "karavan_data.json")
    except Exception as e:
        print(f"could not save: {e}")
        return
    try:
        await interaction.response.send_message(message)
    except Exception as e:
        print(f"Error sending message: {e}")

# Kick a player from a caravan
@bot.tree.command(name="kick", description='Kick a player from a Karavan')
async def kick(interaction: discord.Interaction, *, karavan: str, user: discord.Member):
    karavan_name = karavan.capitalize() + ' Karavan'
    existing_role = discord.utils.get(interaction.guild.roles, name=karavan_name)
    if existing_role is None:
        await interaction.response.send_message(f"The {karavan_name} does not exist.")
        return

    # Check if the user is not in the role
    if existing_role not in user.roles:
        await interaction.response.send_message(f"{user.name} is not in the {existing_role}.")
        return

    try:
        await user.remove_roles(existing_role)
        await interaction.response.send_message(f"{user.name} has been kicked from the {existing_role}.")

        # Load existing Karavan data
        karavan_data = load_data('karavan_data')
        role_str = str(existing_role)

        # Check if the role exists in karavan_data
        if role_str in karavan_data:
            # Remove user name from the list of members. Not working
            karavan_data[role_str]['members'].remove(user.name)

            # Save updated Karavan data
            save_data(karavan_data, 'karavan_data')
    except Exception as e:
        print(f"Error kicking user: {e}")
        await interaction.response.send_message("Error kicking user.")

# Delete a caravan
@bot.tree.command(name="delete", description='Delete a Karavan')
async def delete(interaction: discord.Interaction, *, karavan: str):
    karavan_name = karavan.capitalize() + ' Karavan'
    existing_role = discord.utils.get(interaction.guild.roles, name=karavan_name)
    if existing_role is None:
        await interaction.response.send_message(f"The {karavan_name} does not exist.")
        return

    try:
        await existing_role.delete()
        await interaction.response.send_message(f"The {karavan_name} has been deleted.")

        # Load existing Karavan data
        karavan_data = load_data('karavan_data')
        role_str = str(existing_role)

        # Check if the role exists in karavan_data
        if role_str in karavan_data:
            # Remove the role from karavan_data
            del karavan_data[role_str]

            # Save updated Karavan data
            save_data(karavan_data, 'karavan_data')
    except Exception as e:
        print(f"Error deleting role: {e}")
        await interaction.response.send_message("Error deleting role.")


# Module: inventory
# Description: Executes cmd command
# Usage: /inventory "command" "arg1" "arg2" ...
@bot.tree.command(name = "inventory", description = 'print inventory')
#@Logger(client)
async def inventory(interaction: discord.Interaction):
    print(">> command received >> inventory")
    menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed)
    for member in set(bot.get_all_members()):
            if member.avatar:
                try:
                    embed = discord.Embed(description='test')
                except Exception as e:
                    print(f"Error: {e}")
                embed.set_author(name=member.name, icon_url=member.avatar.url)
                menu.add_page(embed)
    
    menu.add_button(ViewButton.back())
    menu.add_button(ViewButton.next())
    menu.add_button(ViewButton.end_session())
    
    await menu.start()
    print(user_message_counts)
    await interaction.response.send_message(user_message_counts)
    
# ~ ~ ~ S Y N C ~ ~ ~ 

@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
    
# ~ ~ ~ S Y S T E M - T R A Y ~ ~ ~ 

# Starts the bot client
def iconRun():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    #print('TOKEN = '+str(configs.BOT_TOKEN))
    loop.create_task(bot.start(configs.BOT_TOKEN))
    t1=Thread(target=loop.run_forever)
    t1.start()

# Shows logs folder
def showLogs(): os.startfile("logs")

# Shows shortcuts folder
def showShortcuts(): os.startfile("shortcuts")

# Opens bot invitation link in the browser
def connectInfo():
    webbrowser.open(invite_url)

# Exits the application
def applicationExit():
    # This doesn't quit the bot client. To do that you need to call client.logout or .close
    # This merely stops the icon from showing on the taskbar. A full solution will be implemented later
    icon.visible = False
    icon.stop()

# Create system tray icon and start running the client
def iconSetup():
    iconImage = Image.open("wagon.png")
    iconMenu = Menu(
        MenuItem("Connect", action=connectInfo, default=True),
        MenuItem("Show Logs", action=showLogs),
        MenuItem("Show Shortcuts", action=showShortcuts),
        MenuItem("Exit", action=applicationExit),
    )
    icon = Icon('KKWagon', icon=iconImage, menu=iconMenu)
    return icon

# Application Entry Point - starts icon and bot client
icon = iconSetup()
iconRun()
icon.run()
