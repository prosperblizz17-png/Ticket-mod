import discord
from discord.ext import commands
from discord import app_commands
from utils.data_manager import load_json, save_json, CONFIG_PATH
from views.ticket_panel import TicketPanelView

class AdminTicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setstaffrole", description="Set the staff role allowed to manage tickets.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_staff_role(self, interaction: discord.Interaction, role: discord.Role):
        data = load_json(CONFIG_PATH)
        guild_id = str(interaction.guild.id)
        if guild_id not in data: data[guild_id] = {}
        data[guild_id]["staff_role_id"] = role.id
        save_json(CONFIG_PATH, data)
        await interaction.response.send_message(f"✅ Staff control configuration assigned to role: {role.mention}")

    @app_commands.command(name="setcategory", description="Set the category where new ticket channels will open.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        data = load_json(CONFIG_PATH)
        guild_id = str(interaction.guild.id)
        if guild_id not in data: data[guild_id] = {}
        data[guild_id]["category_id"] = category.id
        save_json(CONFIG_PATH, data)
        await interaction.response.send_message(f"✅ Active ticket spawning bounded inside target category: `{category.name}`")

    @app_commands.command(name="setlogs", description="Define target auditing transcript feedback text channels.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_logs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = load_json(CONFIG_PATH)
        guild_id = str(interaction.guild.id)
        if guild_id not in data: data[guild_id] = {}
        data[guild_id]["log_channel_id"] = channel.id
        save_json(CONFIG_PATH, data)
        await interaction.response.send_message(f"✅ Secure audit trails redirected to text destination: {channel.mention}")

    @app_commands.command(name="ticketlimit", description="Configure concurrent ticket parameters permitted per single account user profile.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_limit(self, interaction: discord.Interaction, limit: int):
        if limit < 1:
            await interaction.response.send_message("❌ Setting metric profile targets must scale above 0.", ephemeral=True)
            return
        data = load_json(CONFIG_PATH)
        guild_id = str(interaction.guild.id)
        if guild_id not in data: data[guild_id] = {}
        data[guild_id]["ticket_limit"] = limit
        save_json(CONFIG_PATH, data)
        await interaction.response.send_message(f"✅ Active user threshold capped to: `{limit}` current open threads.")

    @app_commands.command(name="ticketpanel", description="Deploy the permanent Ticket Selection landing page panel embed.")
    @app_commands.checks.has_permissions(administrator=True)
    async def spawn_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Support Center Portal",
            description="Require institutional assistance? Choose the category that best fits your issue from the menu or select the standard activation path below.\n\n"
                        "**⚠️ Warning Notice:** Spimming or abusing ticket generation workflows will trigger administrative sanctions.",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.add_field(name="⏰ Operations Availability", value="24/7/365 Support Queue Systems Matrix", inline=False)
        embed.set_footer(text="Ticket King Framework Engine Core Execution Mode", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        
        await interaction.response.send_message("Deploying Interactive Support Hub layout panel embed structure...", ephemeral=True)
        await interaction.channel.send(embed=embed, view=TicketPanelView())

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminTicketCog(bot))
