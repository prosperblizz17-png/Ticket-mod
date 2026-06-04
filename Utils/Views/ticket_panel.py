import discord
from views.ticket_modal import TicketSubmissionModal

class TicketCategoryDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Billing", description="Payment issues or subscription questions.", emoji="💳"),
            discord.SelectOption(label="Support", description="General inquiries and standard assistance.", emoji="🛠️"),
            discord.SelectOption(label="Partnership", description="Business or advertising inquiries.", emoji="🤝"),
            discord.SelectOption(label="Report User", description="Flag users violating rules.", emoji="🛡️"),
            discord.SelectOption(label="Appeal Ban", description="Submit appeals for moderations.", emoji="⚖️"),
            discord.SelectOption(label="Other", description="Anything else that does not fit categories.", emoji="📁"),
        ]
        super().__init__(placeholder="Select a support reason...", min_values=1, max_values=1, options=options, custom_id="persistent:ticket_dropdown")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketSubmissionModal(category=self.values[0]))


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistent
        self.add_item(TicketCategoryDropdown())

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.success, emoji="🎫", custom_id="persistent:create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        dropdown_view = discord.ui.View()
        dropdown_view.add_item(TicketCategoryDropdown())
        await interaction.response.send_message("🔽 Please choose a structural criteria category below:", view=dropdown_view, ephemeral=True)

    @discord.ui.button(label="FAQ / Help", style=discord.ButtonStyle.secondary, emoji="❓", custom_id="persistent:faq_btn")
    async def faq_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        faq_embed = discord.Embed(
            title="💡 Support FAQ Quick-Guide", 
            description="Before opening a ticket, verify standard documentation protocols:\n\n"
                        "1. **Payment Pending?** Financial clear runs typically take up to 24 hours.\n"
                        "2. **Report System?** Ensure valid screenshot IDs and timestamp parameters are ready.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=faq_embed, ephemeral=True)

