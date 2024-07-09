import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

user_id_to_move = None
channel_id_1 = None
channel_id_2 = None
move_task = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='move')
async def move(ctx, user_id: int, ch_id_1: int, ch_id_2: int):
    global user_id_to_move, channel_id_1, channel_id_2, move_task
    
    user_id_to_move = user_id
    channel_id_1 = ch_id_1
    channel_id_2 = ch_id_2

    member = ctx.guild.get_member(user_id)
    
    if member is None:
        await ctx.send(f'User with ID {user_id} not found.')
        return

    if move_task is not None:
        move_task.cancel()
    
    move_task = bot.loop.create_task(move_member_loop(ctx.guild, member))
    await ctx.send(f'Started moving {member.display_name} between channels {channel_id_1} and {channel_id_2}', delete_after=5)
    

async def move_member_loop(guild, member):
    global user_id_to_move, channel_id_1, channel_id_2
    while True:
        try:
            if member.voice is not None:
                if member.voice.channel.id == channel_id_1:
                    await member.move_to(guild.get_channel(channel_id_2))
                elif member.voice.channel.id == channel_id_2:
                    await member.move_to(guild.get_channel(channel_id_1))
            else:
                print(f"{member.display_name} is not in a voice channel.")
                break
        except discord.HTTPException as e:
            print(f"HTTPException error: {e}")
            await asyncio.sleep(10)  
        except asyncio.CancelledError:
            print("Move task was cancelled.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

bot.run('YOUR_TOKEN') 
