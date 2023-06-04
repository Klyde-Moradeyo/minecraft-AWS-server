import discord

def create_info_embed(title, description, fields):
    embed = discord.Embed(title=title, description=description, color=0x5CDBF0)  # You can choose your own color
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    return embed