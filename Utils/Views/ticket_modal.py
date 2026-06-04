import discord
from discord.ext import commands
import datetime
from utils.data_manager import load_json, save_json, TICKETS_PATH, CONFIG_PATH

class TicketSubmissionModal(discord.ui.Modal):
    def __init__(self, category: str):
        super().__init__(title=f"📝 {category} Ticket Details")
        self.category = category

        self.reason = discord.ui.TextInput(label="Reason for ticket", placeholder="Briefly summarize your issue...", min_length=5, max_length=100)
        self.description = discord.ui.TextInput(label="Full Description", style=discord.TextStyle.paragraph, placeholder="Provide as much detail as possible...", min_length=10)
        self.urgency = discord.ui.TextInput(label="Urgency Level", placeholder="Low, Medium, High, Emergency", min_length=3, max_length=15)
        self.notes = discord.ui.TextInput(label="Additional Notes (Optional)", style=discord.TextStyle.paragraph, required=False, max_length=200)

        self.add_item(self.reason)
        self.add_item(self.description)
        self.add_item(self.urgency)
        self.add_item(self.notes)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        guild_id = str(guild.id)
        
        config = load_json(CONFIG_PATH).get(guild_id, {})
        tickets_data = load_json(TICKETS_PATH)
        
        # Check active limits
        user_id = str(interaction.user.id)
        active_user_tickets = [t for t in tickets_data["active_tickets"].values() if t["creator_id"] == user_id and t["status"] == "open"]
        limit = config.get("ticket_limit", 1)
        
        if len(active_user_tickets) >= limit:
            await interaction.followup.send(f"❌ You already have {len(active_user_tickets)} open ticket(s). Your limit is {limit}.", ephemeral=True)
            return

        # Fetch setup info
        category_id = config.get("category_id")
        staff_role_id = config.get("staff_role_id")
        
        category_obj = guild.get_channel(category_id) if category_id else None
        staff_role = guild.get_role(staff_role_id) if staff_role_id else None

        # Permissions Setup
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True, manage_permissions=True)
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True, read_message_history=True)

        # Counter Increment
        tickets_data["total_tickets"] += 1
        ticket_number = tickets_data["total_tickets"]
        
        channel_name = f"ticket-{self.category.lower()}-{interaction.user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category_obj, overwrites=overwrites)

        # Embed Inside Ticket
        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_number} - {self.category}",
            description=f"Welcome {interaction.user.mention}! Support staff will be with you shortly.\nUse the action control layout below to manage this channel.",
            color=discord.Color.brand_green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Creator", value=interaction.user.mention, inline=True)
        embed.add_field(name="🚨 Urgency", value=self.urgency.value, inline=True)
        embed.add_field(name="📌 Reason", value=self.reason.value, inline=False)
        embed.add_field(name="📝 Description", value=self.description.value, inline=False)
        if self.notes.value:
            embed.add_field(name="🔍 Notes", value=self.notes.value, inline=False)
            
        embed.set_footer(text="Ticket King Framework", icon_url=guild.icon.url if guild.icon else None)

        from views.ticket_control import TicketControlView
        control_view = TicketControlView()
        control_msg = await ticket_channel.send(embed=embed, view=control_view)

        # Update JSON State
        tickets_data["active_tickets"][str(ticket_channel.id)] = {
            "ticket_id": ticket_number,
            "creator_id": user_id,
            "category": self.category,
            "status": "open",
            "claimed_by": None,
            "control_msg_id": control_msg.id
        }
        save_json(TICKETS_PATH, tickets_data)

        # Log Ticket Creation
        log_channel_id = config.get("log_channel_id")
        if log_channel_id:
            log_channel = guild.get_channel(log_channel_id)
            if log_channel:
                log_embed = discord.Embed(title="🟢 Ticket Created", color=discord.Color.green(), timestamp=datetime.datetime.now())
                log_embed.add_field(name="User", value=interaction.user.mention, inline=True)
                log_embed.add_field(name="Channel", value=ticket_channel.mention, inline=True)
                log_embed.add_field(name="Category", value=self.category, inline=True)
                await log_channel.send(embed=log_embed)

        await interaction.followup.send(f"✅ Ticket channel created successfully! Go to {ticket_channel.mention}", ephemeral=True)

