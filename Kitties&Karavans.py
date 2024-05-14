# ~ ~ ~ K I T T Y ~ K A R A V A N S ~ ~ ~

# ~ ~ ~ I M P O R T S ~ ~ ~ 
try:
    import os
    import random
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

# ~ ~ L O A D ~ ~ 
def load_data(data): #data: file to load
    try:
        with open(data, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# ~ ~ S A V E ~ ~ 
def save_data(data, file_path): # data: file to save
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file)
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")

# ~ ~ O N ~ M E S S A G E ~ ~ 
@bot.event
async def on_message(message):
    pastries = load_data('pastries.json')
    karavan_data = load_data('karavan_data.json')
    print(message.author, ">", message.content)
    if not message.author.bot:
        user_id = str(message.author.name)
        karavan = None
        for karavan_name, karavan_info in karavan_data.items():
            if user_id in karavan_info['members']:
                karavan = karavan_name
                break
        
        if karavan:
            role_data = karavan_data.get(karavan, {})
            members_data = role_data.get('members', {})
            user_slots = members_data.get(user_id, {})
            #print("User Slots >", user_slots)  # Check if user_slots contains the expected values
            #print("Values >", user_slots.values())
            values_dict = next(iter(user_slots.values()))
            # Access the 'pastries' dictionary
            pastries_dict = user_slots['pastries']

            # Select a slot randomly based on weights in the 'pastries' dictionary
            selected_slot = random.choices(list(pastries_dict.keys()), weights=pastries_dict.values(), k=1)[0]

            #print("checkpoint3")
            # Increment the selected slot in pastries_data by 1
            pastries_data = pastries.setdefault(karavan, {}).setdefault('members', {}).setdefault(user_id, {}).setdefault('pastries', {})
            pastries_data[selected_slot] = pastries_data.get(selected_slot, 0) + 1
            
            #print("Updated Pastries:", pastries)  # Check the updated pastries data
            save_data(pastries, "pastries.json")

    
    await bot.process_commands(message)

# ~ ~ S H U T D O W N ~ ~ 
@bot.event
async def on_shutdown():
    save_data(pastries, "pastries.json")

# ~ ~ J O I N ~ ~ 
@bot.tree.command(name="join", description='Start a Karavan or join an existing one')
async def join(interaction: discord.Interaction, *, karavan: str, user: discord.Member):
    karavan_name = karavan.capitalize() + ' Karavan'
    
        # Check if the user already has a role containing the word "Karavan"
    existing_karavan_roles = [role for role in user.roles if "Karavan" in role.name]
    if existing_karavan_roles:
        await interaction.response.send_message(f"{user.name} is already in a Karavan.")
        return
    
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
    if role in user.roles:
        await interaction.response.send_message(f"{user.name} is already in the {role}.")
        return
    try:
        await user.add_roles(role)
        print(f"{user.name} given the role {role}.")
        message += f"\n{user.name} given the role {role}."
    except Exception as e:
        print(f"Error: {e}")
        await interaction.response.send_message(f"Error granting role {role}.")
        return
    try:
        pastries = load_data('pastries.json')
        role_str = str(role)
        if role_str not in pastries:
            pastries[role_str] = {'members': {}}
        if user.name not in pastries[role_str]['members']:
            pastries[role_str]['members'][user.name] = {'pastries': {'🫓': 0,'🍞': 0,'🥯': 0,'🥐': 0,'🥟': 0,'🍪': 0,'🍩': 0,'🧁': 0,'🍰': 0}}
        save_data(pastries, "pastries.json")
        karavan_data = load_data('karavan_data.json')
        if role_str not in karavan_data:
            karavan_data[role_str] = {'members': {}}
        if user.name not in karavan_data[role_str]['members']:
            karavan_data[role_str]['members'][user.name] = {'pastries': {'🫓': 40,'🍞': 5,'🥯': 5,'🥐': 5,'🥟': 5,'🍪': 5,'🍩': 5,'🧁': 5,'🍰': 5}}
        save_data(karavan_data, "karavan_data.json")
    except Exception as e:
        print(f"could not save: {e}")
        return
    try:
        await interaction.response.send_message(message)
    except Exception as e:
        print(f"Error sending message: {e}")

# ~ ~ K I C K ~ ~ 
@bot.tree.command(name="kick", description='Kick a player from a Karavan')
async def kick(interaction: discord.Interaction, *, karavan: str, user: discord.Member):
    karavan_name = karavan.capitalize() + ' Karavan'
    existing_role = discord.utils.get(interaction.guild.roles, name=karavan_name)
    if existing_role is None:
        await interaction.response.send_message(f"The {karavan_name} does not exist.")
        return

    if existing_role not in user.roles: # Check if the user is not in the role
        await interaction.response.send_message(f"{user.name} is not in the {existing_role}.")
        return

    try:
        await user.remove_roles(existing_role)
        await interaction.response.send_message(f"{user.name} has been kicked from the {existing_role}.")

        # Load existing Karavan data
        karavan_data = load_data('karavan_data.json')
        role_str = str(existing_role)
        pastries = load_data('pastries.json')

        # Check if the role exists in karavan_data
        if role_str in karavan_data:
            # Remove user name from the list of members. Not working
            karavan_data[role_str]['members'].remove(user.name)
            save_data(karavan_data, "karavan_data.json")
        # Remove user data from pastries
        if user.name in pastries.get(role_str, {}).get('members', {}):
            try:
                del pastries[role_str]['members'][user.name]
                save_data(pastries, 'pastries.json')
            except Exception as e:
                print(f"Error deleting user pastries: {e}")
        else:
            print(f"{user.name} not in pastries")

    except Exception as e:
        print(f"Error kicking user: {e}")
        await interaction.response.send_message("Error kicking user.")

# ~ ~ D E L E T E ~ ~ 
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
        karavan_data = load_data('karavan_data.json')
        role_str = str(existing_role)
        pastries = load_data('pastries.json')
        # Check if the role exists in karavan_data
        if role_str in karavan_data:
            del karavan_data[role_str] # Remove the role from karavan_data
            save_data(karavan_data, "karavan_data.json")
        if role_str in pastries:
            del pastries[role_str] # Remove the role from pastries
            save_data(pastries, "pastries.json")
    except Exception as e:
        print(f"Error deleting role: {e}")
        await interaction.response.send_message("Error deleting role.")

# ~ ~ I N V E N T O R Y ~ ~ 
@bot.tree.command(name="inventory", description='Print Inventory')
async def inventory(interaction: discord.Interaction, *, karavan: str):
    karavan_name = karavan.capitalize() + ' Karavan'
    print(">> Command received >> Inventory")

    # Load karavan data
    karavan_data = load_data('karavan_data.json')
    members_with_role = []
    pastries = load_data('pastries.json')
    # Retrieve members with the specific role
    for member in interaction.guild.members:
        if any(role.name == karavan_name for role in member.roles):
            members_with_role.append(member)

    menu = ViewMenu(interaction, menu_type=ViewMenu.TypeEmbed)

    # Add pages for members with the specific role
    for member in members_with_role:
        if member.avatar:
            embed = discord.Embed(title=f'Pastries - {member.name}')
            embed.set_thumbnail(url=member.avatar.url)
            
            # Format values as italics
            value_emojis = ['🫓', '🍞', '🥯', '🥐', '🥟', '🍪', '🍩', '🧁', '🍰']
            for emoji in value_emojis:
                value = pastries[karavan_name]['members'][member.name]["pastries"][emoji]
                value_code_block = f"*{value}*"  # Format value as italics
                embed.add_field(name=emoji, value=value_code_block, inline=True)

            menu.add_page(embed)
            
    # Add buttons to the menu
    menu.add_button(ViewButton.back())
    menu.add_button(ViewButton.next())
    menu.add_button(ViewButton.end_session())

    # Start the menu
    await menu.start()

# ~ ~ U P G R A D E ~ ~ 
@bot.tree.command(name="upgrade", description='Buy Upgrades')
async def inventory(interaction: discord.Interaction):
    print(">> Command received >> Upgrade")

    # Load pastries data
    pastries = load_data('pastries.json')

    # Get the user who used the command
    user = interaction.user
    print(user.name)
    print(pastries)
    # Check if the user has pastries data
    if user.name in pastries:
        # Create an embed for the user's inventory
        embed = discord.Embed(title=f'Pastries - {user.name}')
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)

        # Add the pastries of the user to the embed
        for emoji, value in pastries[user.name]["pastries"].items():
            value_italics = f"*{value}*"
            embed.add_field(name=emoji, value=value_italics, inline=True)

        # Create buttons for each emoji in the user's inventory
        buttons = []
        for emoji in pastries[user.name]["pastries"].keys():
            button = reactionmenu.create_button(style=reactionmenu.Style.PRIMARY, label=emoji, custom_id=emoji)
            buttons.append(button)

        # Create a reaction menu with the buttons
        menu = reactionmenu.Menu(embed=embed, buttons=buttons)
        await menu.send(interaction)
    else:
        # If the user does not have pastries data, inform them
        await interaction.response.send_message("You don't have any pastries data yet.")


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
