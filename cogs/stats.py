import discord
from discord.ext import commands
from discord import app_commands
from utils.data_manager import load_json, TICKETS_PATH

class StatsTicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ticketstats", description="Display full operations analytics dashboard diagnostics statistics data arrays.")
    @app_commands.checks.has_permissions(administrator=True)
    async def stats_command(self, interaction: discord.Interaction):
        t_data = load_json(TICKETS_PATH)
        active = t_data.get("active_tickets", {})
        
        open_count = sum(1 for t in active.values() if t["status"] == "open")
        closed_count = sum(1 for t in active.values() if t["status"] == "closed")
        claimed_count = sum(1 for t in active.values() if t.get("claimed_by") is not None)

        embed = discord.Embed(title="📊 Operational Ticket Statistics Dashboard", color=discord.Color.gold())
        embed.add_field(name="🔢 Cumulative Global Tickets Set", value=f"`{t_data.get('total_tickets', 0)}` total items tracking", inline=True)
        embed.add_field(name="🟢 Total Active Opened", value=f"`{open_count}` instances running", inline=True)
        embed.add_field(name="🔒 Semi-Archived Closed Saved", value=f"`{closed_count}` files marked", inline=True)
        embed.add_field(name="📌 Assigned Claims", value=f"`{claimed_count}` channels handled", inline=True)

        # Leaderboard Extraction
        staff_stats = t_data.get("staff_stats", {})
        if staff_stats:
            sorted_staff = sorted(staff_stats.items(), key=lambda item: item[1], reverse=True)[:5]
            lb_text = ""
            for rank, (s_id, count) in enumerate(sorted_staff, start=1):
                lb_text += f"**#{rank}** <@{s_id}> - `{count}` resolution procedures managed.\n"
            embed.add_field(name="🏆 Top Staff Responders Leaderboard", value=lb_text, inline=False)
        else:
            embed.add_field(name="🏆 Top Staff Responders Leaderboard", value="*No tracking claims instances logged yet.*", inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(StatsTicketCog(bot))
