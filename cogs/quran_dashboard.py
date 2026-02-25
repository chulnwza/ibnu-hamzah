"""
Quran Dashboard Cog to provide a UI for interacting with Quranic verses and recitations.
"""
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

from utils.api_client import get_full_surah_audio, get_ayah_audio, RECITER_MAPPING
from utils.surahs import SURAHS

class AyahRangeModal(discord.ui.Modal, title="Set Ayah Range"):
    start_ayah = discord.ui.TextInput(
        label="Start Ayah Number",
        placeholder="e.g. 1",
        required=True
    )
    end_ayah = discord.ui.TextInput(
        label="End Ayah Number",
        placeholder="e.g. 5",
        required=True
    )

    def __init__(self, view: discord.ui.View):
        super().__init__()
        self.dashboard_view = view

    async def on_submit(self, interaction: discord.Interaction):
        try:
            start_val = int(self.start_ayah.value)
            end_val = int(self.end_ayah.value)
            if start_val > end_val or start_val < 1:
                await interaction.response.send_message("Invalid range.", ephemeral=True)
                return
            self.dashboard_view.start_ayah = start_val
            self.dashboard_view.end_ayah = end_val
            await interaction.response.send_message(f"Range set: Ayah {start_val} to {end_val}", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Please enter valid integers.", ephemeral=True)

class QuranDashboardView(discord.ui.View):
    """
    A View containing a Select menu for Reciter, along with Play/Stop buttons and Ayah Range setting.
    """
    def __init__(self, surah_number: int):
        super().__init__(timeout=None)
        self.surah_number = surah_number
        self.is_full_quran = (surah_number == 0)
        self.current_surah = 1 if self.is_full_quran else self.surah_number
        
        # Default selections
        self.start_ayah = None
        self.end_ayah = None
        self.selected_reciter = "mishary"
        
        # Audio playback state
        self.audio_queue = []
        self.play_task = None
        self.stop_event = asyncio.Event()

        # Select Reciter
        reciter_options = [
            discord.SelectOption(label="Mishary Rashid Alafasy", value="mishary", description="Kuwait"),
            discord.SelectOption(label="Abdul Rahman Al-Sudais", value="sudais", description="Mecca"),
            discord.SelectOption(label="Maher Al-Muaiqly", value="maher", description="Mecca"),
            discord.SelectOption(label="Saud Al-Shuraim", value="shuraim", description="Mecca"),
            discord.SelectOption(label="Saad Al-Ghamidi", value="ghamidi", description="Dammam"),
        ]
        reciter_select = discord.ui.Select(
            placeholder="Select Reciter",
            min_values=1,
            max_values=1,
            options=reciter_options,
            custom_id="reciter_select"
        )
        reciter_select.callback = self.reciter_callback
        self.add_item(reciter_select)

    async def reciter_callback(self, interaction: discord.Interaction):
        self.selected_reciter = interaction.data["values"][0]
        await interaction.response.defer()

    @discord.ui.button(label="Set Ayah Range", style=discord.ButtonStyle.secondary, custom_id="range_button")
    async def range_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AyahRangeModal(self))

    @discord.ui.button(label="▶️ Play Arabic", style=discord.ButtonStyle.primary, custom_id="play_button")
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Play audio in voice channel."""
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.response.send_message("You need to join a voice channel first!", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

        # Clear any existing playback
        self.stop_event.clear()
        if voice_client.is_playing():
            voice_client.stop()
        if self.play_task and not self.play_task.done():
            self.play_task.cancel()

        await interaction.response.send_message("Fetching audio...", ephemeral=True)
        
        reciter_config = RECITER_MAPPING.get(self.selected_reciter, RECITER_MAPPING["mishary"])

        try:
            if self.is_full_quran:
                self.play_task = asyncio.create_task(self.play_full_quran_loop(interaction, voice_client, reciter_config["quran_com"]))
                await interaction.edit_original_response(content="Starting Full Quran recitation...")
            elif self.start_ayah is None or self.end_ayah is None:
                # Play full surah
                audio_url = await get_full_surah_audio(self.surah_number, reciter_config["quran_com"])
                if not audio_url:
                    await interaction.edit_original_response(content="Could not retrieve full Surah audio URL.")
                    return
                
                if audio_url.startswith("//"):
                    audio_url = "https:" + audio_url
                    
                voice_client.play(discord.FFmpegPCMAudio(audio_url))
                await interaction.edit_original_response(content=f"Playing full Surah {self.surah_number}...")
            else:
                # Play range
                self.audio_queue = []
                self.play_task = asyncio.create_task(self.play_queue(interaction, voice_client, reciter_config["aladhan"]))
                await interaction.edit_original_response(content=f"Preparing to play Ayah {self.start_ayah} to {self.end_ayah}...")
                
        except Exception as e:
            await interaction.edit_original_response(content=f"An error occurred: {e}")

    async def play_full_quran_loop(self, interaction: discord.Interaction, voice_client: discord.VoiceClient, reciter_id: int):
        while self.current_surah <= 114:
            if self.stop_event.is_set():
                break
                
            try:
                audio_url = await get_full_surah_audio(self.current_surah, reciter_id)
                if not audio_url:
                    self.current_surah += 1
                    continue
                
                if audio_url.startswith("//"):
                    audio_url = "https:" + audio_url
                    
                # wait until voice client is not playing before playing the next
                while voice_client.is_playing():
                    await asyncio.sleep(0.5)
                    if self.stop_event.is_set():
                        break
                        
                if self.stop_event.is_set():
                    break
                    
                voice_client.play(discord.FFmpegPCMAudio(audio_url))
                self.current_surah += 1
            except Exception as e:
                print(f"Failed to play Surah {self.current_surah}: {e}")
                self.current_surah += 1
                continue
        
        # Finished
        if not self.stop_event.is_set():
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()

    async def play_queue(self, interaction: discord.Interaction, voice_client: discord.VoiceClient, reciter_string: str):
        for ayah_num in range(self.start_ayah, self.end_ayah + 1):
            if self.stop_event.is_set():
                break
                
            try:
                audio_url = await get_ayah_audio(self.surah_number, ayah_num, reciter_string)
                if not audio_url:
                    continue
                
                # wait until voice client is not playing before playing the next
                while voice_client.is_playing():
                    await asyncio.sleep(0.5)
                    if self.stop_event.is_set():
                        break
                        
                if self.stop_event.is_set():
                    break
                    
                voice_client.play(discord.FFmpegPCMAudio(audio_url))
            except Exception as e:
                print(f"Failed to play Ayah {ayah_num}: {e}")
                continue

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger, custom_id="stop_button")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Stop audio in voice channel."""
        self.stop_event.set()
        self.audio_queue.clear()
        
        if self.play_task and not self.play_task.done():
            self.play_task.cancel()
            
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            await interaction.response.send_message("Stopped playback and disconnected.", ephemeral=True)
        else:
            await interaction.response.send_message("The bot is not currently in a voice channel.", ephemeral=True)


class SurahListPaginationView(discord.ui.View):
    def __init__(self, embeds: list[discord.Embed]):
        super().__init__(timeout=180)
        self.embeds = embeds
        self.current_page = 0

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary, custom_id="prev_button", disabled=True)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary, custom_id="next_button")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        # Update button states
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == len(self.embeds) - 1)
        
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)


class QuranDashboardCog(commands.Cog):
    """
    Cog for the Quran dashboard.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="quran", description="Open the Quran Dashboard")
    @app_commands.describe(surah_number="Surah number 1-114, or 0 to play the entire Quran from the beginning")
    async def quran(self, interaction: discord.Interaction, surah_number: int):
        """
        Responds with an embed and a view to select reciter and play options.
        """
        if surah_number < 0 or surah_number > 114:
            await interaction.response.send_message("Surah number must be between 0 and 114.", ephemeral=True)
            return
            
        if surah_number == 0:
            embed = discord.Embed(
                title="📖 Now Playing: The Noble Quran (Full Recitation)",
                description="Use the selection menu to choose a Reciter, then press play to listen.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Current Progress: Surah 1 of 114 (Requested by {interaction.user.display_name})")
        else:
            embed = discord.Embed(
                title=f"📖 Quran Dashboard (Surah {surah_number})",
                description="Use the selection menu to choose a Reciter. You can set an Ayah range, or directly press play to listen to the full Surah.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        view = QuranDashboardView(surah_number)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="surah_list", description="Display a list of all 114 Surahs")
    async def surah_list(self, interaction: discord.Interaction):
        """
        Responds with paginated embeds listing all Surahs.
        """
        embeds = []
        chunk_size = 30 # Display 30 per page
        
        for i in range(0, len(SURAHS), chunk_size):
            chunk = SURAHS[i:i + chunk_size]
            description = "\n".join(chunk)
            
            embed = discord.Embed(
                title="📖 Table of Surahs",
                description=description,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Page {len(embeds) + 1} of {(len(SURAHS) + chunk_size - 1) // chunk_size}")
            embeds.append(embed)
            
        view = SurahListPaginationView(embeds)
        await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Extension setup function.
    """
    await bot.add_cog(QuranDashboardCog(bot))
