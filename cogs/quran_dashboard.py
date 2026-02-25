"""
Quran Dashboard Cog to provide a UI for interacting with Quranic verses and recitations.
"""
import discord
from discord import app_commands
from discord.ext import commands

class QuranDashboardView(discord.ui.View):
    """
    A View containing a Select menu for Surah, Ayah, and Reciter, along with Play/Stop buttons.
    """
    def __init__(self):
        super().__init__(timeout=None)
        
        # Select Surah
        surah_options = [
            discord.SelectOption(label="Al-Fatihah", description="The Opener", value="1"),
            discord.SelectOption(label="Al-Baqarah", description="The Cow", value="2"),
        ]
        surah_select = discord.ui.Select(
            placeholder="Select Surah",
            min_values=1,
            max_values=1,
            options=surah_options,
            custom_id="surah_select"
        )
        
        # Select Ayah
        ayah_options = [
            discord.SelectOption(label="All", description="Whole Surah", value="all"),
            discord.SelectOption(label="1", description="Ayah 1", value="1"),
            discord.SelectOption(label="2", description="Ayah 2", value="2"),
            discord.SelectOption(label="3", description="Ayah 3", value="3"),
        ]
        ayah_select = discord.ui.Select(
            placeholder="Select Ayah",
            min_values=1,
            max_values=1,
            options=ayah_options,
            custom_id="ayah_select"
        )
        
        # Select Reciter
        reciter_options = [
            discord.SelectOption(label="Mishary Rashid Alafasy", value="mishary"),
            discord.SelectOption(label="AbdulBaset AbdulSamad", value="abdul_baset"),
        ]
        reciter_select = discord.ui.Select(
            placeholder="Select Reciter",
            min_values=1,
            max_values=1,
            options=reciter_options,
            custom_id="reciter_select"
        )

        # Assign callbacks to prevent interaction failure
        surah_select.callback = self.surah_callback
        ayah_select.callback = self.ayah_callback
        reciter_select.callback = self.reciter_callback

        self.add_item(surah_select)
        self.add_item(ayah_select)
        self.add_item(reciter_select)

    async def surah_callback(self, interaction: discord.Interaction):
        # Acknowledge the interaction
        await interaction.response.defer()
        
    async def ayah_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

    async def reciter_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

    @discord.ui.button(label="▶️ Play Arabic", style=discord.ButtonStyle.primary, custom_id="play_button")
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Play audio in voice channel."""
        await interaction.response.send_message("Playing Arabic audio...", ephemeral=True)

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger, custom_id="stop_button")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Stop audio in voice channel."""
        await interaction.response.send_message("Stopped playback.", ephemeral=True)


class QuranDashboardCog(commands.Cog):
    """
    Cog for the Quran dashboard.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="quran", description="Open the Quran Dashboard")
    async def quran(self, interaction: discord.Interaction):
        """
        Responds with an embed and a view to select surah, ayah, and reciter.
        """
        embed = discord.Embed(
            title="📖 Quran Dashboard",
            description="Use the selection menus below to choose a Surah, Ayah, and Reciter. Then press play to listen.",
            color=discord.Color.green()
        )
        if interaction.user.avatar:
            embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        else:
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        view = QuranDashboardView()
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    """
    Extension setup function.
    """
    await bot.add_cog(QuranDashboardCog(bot))
