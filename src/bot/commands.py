import discord
from discord import app_commands
from discord.ext import commands
import asyncio

from src.utils.logger import get_logger
from src.ai.groq import generate_response as groq_generate
from src.ai.openai import generate_response as openai_generate

logger = get_logger(__name__)

from src.bot.client import message_manager

async def register_commands(bot):
    try:
        logger.info("Sincronizando comandos slash...")
        await bot.tree.sync()
        logger.info("Comandos slash sincronizados com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao sincronizar comandos slash: {e}")

class AIChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ajuda")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📚 Comandos Disponíveis",
            description="Aqui estão os comandos que você pode usar:",
            color=discord.Color.blue()
        )

        embed.add_field(name="!ajuda", value="Mostra esta mensagem de ajuda", inline=False)
        embed.add_field(name="!conversar [mensagem]", value="Conversa com a IA", inline=False)
        embed.add_field(name="!limpar", value="Limpa o histórico de conversa atual", inline=False)
        embed.add_field(name="/conversar", value="Comando slash para conversar com a IA", inline=False)
        embed.add_field(name="/limpar", value="Comando slash para limpar o histórico", inline=False)

        await ctx.send(embed=embed)

    @app_commands.command(name="conversar", description="Conversa com a IA")
    @app_commands.describe(mensagem="O que você quer dizer para a IA")
    async def chat_slash(self, interaction: discord.Interaction, mensagem: str):
        await interaction.response.defer(thinking=True)

        channel_id = str(interaction.channel_id)
        user_id = str(interaction.user.id)
        username = interaction.user.display_name

        response = await self._process_ai_message(channel_id, user_id, username, mensagem)

        if not response:
            await interaction.followup.send("❌ Desculpe, ocorreu um erro ao gerar a resposta.")
            return

        await interaction.followup.send(response[:2000])

        if len(response) > 2000:
            for i in range(2000, len(response), 2000):
                chunk = response[i:i+2000]
                if chunk:
                    await interaction.followup.send(chunk)

    @commands.command(name="conversar")
    async def chat_command(self, ctx, *, mensagem: str = None):
        if not mensagem:
            await ctx.send("⚠️ Por favor, forneça uma mensagem para conversar com a IA.")
            return

        async with ctx.typing():
            channel_id = str(ctx.channel.id)
            user_id = str(ctx.author.id)
            username = ctx.author.display_name

            response = await self._process_ai_message(channel_id, user_id, username, mensagem)

            if not response:
                await ctx.send("❌ Desculpe, ocorreu um erro ao gerar a resposta.")
                return

        if len(response) <= 2000:
            await ctx.send(response)
        else:
            for i in range(0, len(response), 2000):
                chunk = response[i:i+2000]
                if chunk:
                    await ctx.send(chunk)

    async def _process_ai_message(self, channel_id, user_id, username, mensagem):
        store = message_manager.get_store(channel_id)

        store.add_user_message(user_id, username, mensagem)

        try:
            response = await groq_generate(store.get_messages())
        except Exception as e:
            logger.warning(f"Erro ao usar Groq, tentando OpenAI: {e}")
            try:
                response = await openai_generate(store.get_messages())
            except Exception as e2:
                logger.error(f"Erro também na OpenAI: {e2}")
                return None

        store.add_assistant_message(response)
        return response

    @app_commands.command(name="limpar", description="Limpa o histórico de conversa")
    async def clear_history_slash(self, interaction: discord.Interaction):
        channel_id = str(interaction.channel_id)

        if message_manager.clear_store(channel_id):
            await interaction.response.send_message("🧹 Histórico de conversa deste canal foi limpo!")
        else:
            await interaction.response.send_message("ℹ️ Este canal ainda não tem um histórico de conversa.")

    @commands.command(name="limpar")
    async def clear_history_command(self, ctx):
        channel_id = str(ctx.channel.id)

        if message_manager.clear_store(channel_id):
            await ctx.send("🧹 Histórico de conversa deste canal foi limpo!")
        else:
            await ctx.send("ℹ️ Este canal ainda não tem um histórico de conversa.")

def setup(bot):
    bot.add_cog(AIChatCommands(bot))
    logger.info("Comandos de chat com IA registrados!")
