import discord
import io
import datetime
from utils.data_manager import load_json, save_json, TICKETS_PATH, CONFIG_PATH

class AddUserModal(discord.ui.Modal):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(title="👥 Add Member to Ticket")
        self.channel = channel
        self.user_id_input = discord.ui.TextInput(label="User ID or Mention String", placeholder="123456789012345678")
        self.add_item(self.user_id_input)

    async def on_submit(self, interaction: discord.Interaction):
        val = self.user_id_input.value.strip().replace("<@", "").replace(">", "").replace("!", "")
        try:
            member = await interaction.guild.fetch_member(int(val))
            await self.channel.set_permissions(member, read_messages=True, send_messages=True, read_message_history=True)
            await interaction.response.send_message(f"✅ Added {member.mention} to this channel workspace.", ephemeral=True)
        except Exception:
            await interaction.response.send_message("❌ Invalid Member ID/Object.", ephemeral=True)

class RenameTicketModal(discord.ui.Modal):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(title="📝 Rename Ticket Channel")
        self.channel = channel
        self.new_name = discord.ui.TextInput(label="New Channel Title Structure", placeholder="ticket-custom-name")
        self.add_item(self.new_name)

    async def on_submit(self, interaction: discord.Interaction):
        await self.channel.edit(name=self.new_name.value.lower().replace(" ", "-"))
        await interaction.response.send_message(f"✅ Channel name rewritten to: `{self.channel.name}`", ephemeral=True)


class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def check_staff(self, interaction: discord.Interaction) -> bool:
        config = load_json(CONFIG_PATH).get(str(interaction.guild.id), {})
        staff_role_id = config.get("staff_role_id")
        if interaction.user.guild_permissions.administrator:
            return True
        if staff_role_id and discord.utils.get(interaction.user.roles, id=int(staff_role_id)):
            return True
        await interaction.response.send_message("❌ Error: Restricted execution. Staff clearance missing.", ephemeral=True)
        return False

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.primary, emoji="📌", custom_id="control:claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction): return
        
        tickets_data = load_json(TICKETS_PATH)
        t_info = tickets_data["active_tickets"].get(str(interaction.channel.id))
        
        if t_info and t_info.get("claimed_by"):
            await interaction.response.send_message("⚠️ This environment is already claimed by another operational agent.", ephemeral=True)
            return
            
        t_info["claimed_by"] = interaction.user.id
        tickets_data["claimed_tickets"] += 1
        
        # Track individual staff metrics
        staff_id = str(interaction.user.id)
        tickets_data["staff_stats"][staff_id] = tickets_data["staff_stats"].get(staff_id, 0) + 1
        save_json(TICKETS_PATH, tickets_data)
        
        await interaction.channel.set_permissions(interaction.user, read_messages=True, send_messages=True, manage_channels=True)
        await interaction.response.send_message(f"📌 **Ticket claimed by operational specialist:** {interaction.user.mention}")

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="control:close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction): return
        
        tickets_data = load_json(TICKETS_PATH)
        t_info = tickets_data["active_tickets"].get(str(interaction.channel.id))
        if t_info:
            t_info["status"] = "closed"
        save_json(TICKETS_PATH, tickets_data)
        
        # Revoke writer structural rights
        if t_info:
            creator = interaction.guild.get_member(int(t_info["creator_id"]))
            if creator:
                await interaction.channel.set_permissions(creator, read_messages=True, send_messages=False)

        await interaction.response.send_message("🔒 **Ticket system standard execution locked.** Interface is now closed.")

    @discord.ui.button(label="Reopen Ticket", style=discord.ButtonStyle.success, emoji="🔓", custom_id="control:reopen")
    async def reopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction): return
        
        tickets_data = load_json(TICKETS_PATH)
        t_info = tickets_data["active_tickets"].get(str(interaction.channel.id))
        if t_info:
            t_info["status"] = "open"
            creator = interaction.guild.get_member(int(t_info["creator_id"]))
            if creator:
                await interaction.channel.set_permissions(creator, read_messages=True, send_messages=True)
        save_json(TICKETS_PATH, tickets_data)
        await interaction.response.send_message("🔓 **Ticket reactivated.** Full structural context pipelines re-opened.")

    @discord.ui.button(label="Add User", style=discord.ButtonStyle.secondary, emoji="👥", custom_id="control:add_user")
    async def add_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction): return
        await interaction.response.send_modal(AddUserModal(interaction.channel))

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.secondary, emoji="📝", custom_id="control:rename")
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction): return
        await interaction.response.send_modal(RenameTicketModal(interaction.channel))

    @discord.ui.button(label="Transcript", style=discord.ButtonStyle.secondary, emoji="📂", custom_id="control:transcript")
    async def transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction): return
        await interaction.response.defer()
        
        # Build raw transcript data
        lines = [f"=== Transcript: #{interaction.channel.name} ==="]
        async for msg in interaction.channel.history(limit=None, oldest_first=True):
            ts = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"[{ts}] {msg.author} ({msg.author.id}): {msg.clean_content}")
            
        buffer = io.BytesIO("\n".join(lines).encode("utf-8"))
        f = discord.File(fp=buffer, filename=f"transcript-{interaction.channel.name}.txt")
        
        config = load_json(CONFIG_PATH).get(str(interaction.guild.id), {})
        log_chan_id = config.get("log_channel_id")
        
        if log_chan_id:
            log_channel = interaction.guild.get_channel(log_chan_id)
            if log_channel:
                await log_channel.send(content=f"📂 Transcript generated for channel: `{interaction.channel.name}`", file=f)
                await interaction.followup.send("✅ System transcript filed securely to logging outputs.", ephemeral=True)
                return
        await interaction.followup.send(file=f, ephemeral=True)

    @discord.ui.button(label="Delete Ticket", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="control:delete")
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin status required to delete core environments.", ephemeral=True)
            return
            
        tickets_data = load_json(TICKETS_PATH)
        tickets_data["active_tickets"].pop(str(interaction.channel.id), None)
        save_json(TICKETS_PATH, tickets_data)
        
        await interaction.response.send_message("⚠️ Destructive countdown initiated. Deleting channel in 5 seconds...")
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()
