import nextcord
from nextcord.ext import commands
from nextcord import SlashOption

import os, yt_dlp

bot = commands.Bot()

@bot.slash_command(name="upload", description="Upload a video clip to the bot", force_global=True)
@commands.cooldown(1, 600, commands.BucketType.user)
async def upload(
    interaction: nextcord.Interaction,
    clip: nextcord.Attachment = SlashOption(
        name="clip", 
        description="The the clip you want to upload", 
        required=False
    ),

    youtube: str = SlashOption(
        name="youtube", 
        description="(Optional) Upload a video from youtube.com", 
        required=False
    )
):  
    if not clip and not youtube:
        return await interaction.response.send_message("❌ Please provide a video clip or a youtube link!", ephemeral=True)

    directory_path = f'videos/@{interaction.user.name}'
    os.makedirs(directory_path, exist_ok=True)

    if clip:
        file_extension = clip.filename.lower().split('.')[-1]
        if file_extension not in ['mp4', 'mkv', 'mov']:
            return await interaction.response.send_message("❌ Only video files (.mp4, .mkv, .mov) are allowed!", ephemeral=True)
        try:
            await clip.save(f'{directory_path}/{clip.filename}')
            return await interaction.response.send_message(f"Successfully saved {clip.filename}", ephemeral=True)
        except Exception:
            return await interaction.response.send_message(f"Error saving file", ephemeral=True)

    elif youtube:
        await interaction.response.defer(ephemeral=True)
        ydl_opts = {
            'outtmpl': f'{directory_path}/%(title)s.%(ext)s',
            'format': 'best',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await interaction.followup.send("### ⏳ Verifying video length...")
                info_dict = ydl.extract_info(youtube, download=False)
                duration = info_dict.get('duration', None)
            
                if duration is None:
                    return await interaction.followup.send(
                        "### ❌ Could not retrieve video duration!", ephemeral=True
                    )
                    
                if duration > 30:
                    return await interaction.followup.send(
                        "### ❌ The video is longer than 30 seconds!", ephemeral=True
                    )
                await interaction.followup.send("### ⏳ Downloading video...", ephemeral=True)
                ydl.download([youtube])
                return await interaction.followup.send(f"Successfully saved '{info_dict.get('title', None)}'", ephemeral=True)
        except Exception:
            return await interaction.followup.send(f"Error saving video", ephemeral=True)
    else:
        return await interaction.response.send_message("❌ Please provide a video clip or a youtube link!", ephemeral=True)

@upload.error
async def upload_error(interaction: nextcord.Interaction, error: commands.CommandError):
    if isinstance(error, commands.CommandOnCooldown):
        return await interaction.followup.send(
            f"❌ You are on cooldown! Please wait {round(error.retry_after, 1)} seconds before trying again.", ephemeral=True
        )
    else:
        return await interaction.followup.send("❌ An error occurred!", ephemeral=True)

bot.run("TOKEN")
