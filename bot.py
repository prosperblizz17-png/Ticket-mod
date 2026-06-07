import discord
from discord.ext import commands
from utils.data_manager import initialize_files 
from views.ticket_panel import TicketPanelView
from views.ticket_control import TicketControlView
import os
from dotenv import load_dotenv

class TicketKingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="?", intents=intents)

    async def setup_hook(self):
        # Initialize JSON storage structures
        initialize_files()

        # Connect UI listeners to memory for persistent runtime capabilities
        self.add_view(TicketPanelView())
        self.add_view(TicketControlView())

        # Load cog modules
        await self.load_extension("cogs.admin")
        await self.load_extension("cogs.stats")

    async def on_ready(self):
        print(f"🚀 Success: {self.user.name} online environment initiated across Discord.")
        try:
            synced = await self.tree.sync()
            print(f"🔄 System Synchronized: Registered {len(synced)} global dynamic slash application structural commands.")
        except Exception as e:
            print(f"❌ Failed to sync slash command structural trees down to endpoints: {e}")

bot = TicketKingBot()

# Global Application Command Error Boundary
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ Verification Fault: Profile execution denied. Missing administrative permissions.", ephemeral=True)
    else:
        print(f"Unhandled Exception Core Node Stack Alert: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("⚠️ Server core internal operational pipeline fault error encountered.", ephemeral=True)

if __name__ == "__main__":
    # Insert token here
    bot.run(TOKEN)

