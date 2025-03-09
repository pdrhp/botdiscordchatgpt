import discord
from discord import app_commands
from discord.ext import commands
import asyncio

from src.utils.logger import get_logger
from src.ai.message_store import MessageStore
from src.ai.message_manager import message_manager
from src.ai.groq import generate_response as groq_generate
from src.ai.openai import generate_response as openai_generate
from src.ai.personality import get_personality, set_personality

logger = get_logger(__name__)

async def register_commands(bot):
    try:
        commands = bot.tree.get_commands()
        logger.info(f"Comandos registrados na árvore: {len(commands)}")
        for cmd in commands:
            logger.info(f"Comando registrado: /{cmd.name}")

        logger.info("Sincronizando comandos slash globalmente...")
        global_commands = await bot.tree.sync()
        logger.info(f"Sincronizados {len(global_commands)} comandos globalmente")

        if len(bot.guilds) > 0:
            logger.info(f"Bot está presente em {len(bot.guilds)} servidores")

            for guild in bot.guilds:
                try:
                    logger.info(f"Sincronizando comandos para o servidor {guild.name} (ID: {guild.id})...")
                    guild_commands = await bot.tree.sync(guild=discord.Object(id=guild.id))
                    logger.info(f"Sincronizados {len(guild_commands)} comandos para o servidor {guild.name} (ID: {guild.id})")
                except Exception as e:
                    logger.error(f"Erro ao sincronizar comandos para o servidor {guild.name} (ID: {guild.id}): {e}")
        else:
            logger.warning("Bot não está presente em nenhum servidor ainda")
    except Exception as e:
        logger.error(f"Erro ao sincronizar comandos slash: {e}")

class AIChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("Comandos de chat com IA inicializados")

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
        embed.add_field(name="!personalidade", value="Mostra a personalidade atual do bot", inline=False)
        embed.add_field(name="!personalidade [nova]", value="Altera a personalidade do bot (apenas administradores)", inline=False)
        embed.add_field(name="/conversar", value="Comando slash para conversar com a IA", inline=False)
        embed.add_field(name="/limpar", value="Comando slash para limpar o histórico", inline=False)
        embed.add_field(name="/personalidade", value="Comando slash para gerenciar a personalidade", inline=False)

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

    @commands.command(name="personalidade")
    async def personality_command(self, ctx, *, nova_personalidade: str = None):
        if nova_personalidade is None:
            personalidade_atual = get_personality()
            await ctx.send(f"**Personalidade atual do bot:**\n```\n{personalidade_atual}\n```")
            return

        if not ctx.author.guild_permissions.administrator:
            await ctx.send("⚠️ Apenas administradores podem alterar a personalidade do bot.")
            return

        set_personality(nova_personalidade)

        for channel_id in list(message_manager.stores.keys()):
            message_manager.clear_store(channel_id)

        await ctx.send("✅ Personalidade do bot atualizada com sucesso!")

    @app_commands.command(name="personalidade", description="Mostra ou altera a personalidade do bot")
    @app_commands.describe(nova_personalidade="Nova personalidade para o bot (apenas administradores)")
    async def personality_slash(self, interaction: discord.Interaction, nova_personalidade: str = None):
        if nova_personalidade is None:
            personalidade_atual = get_personality()
            await interaction.response.send_message(f"**Personalidade atual do bot:**\n```\n{personalidade_atual}\n```")
            return

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⚠️ Apenas administradores podem alterar a personalidade do bot.")
            return

        set_personality(nova_personalidade)

        for channel_id in list(message_manager.stores.keys()):
            message_manager.clear_store(channel_id)

        await interaction.response.send_message("✅ Personalidade do bot atualizada com sucesso!")

    @commands.command(name="diagnostico")
    @commands.is_owner()  # Apenas o dono do bot pode usar este comando
    async def diagnostic_command(self, ctx):
        """Comando para diagnosticar problemas com os comandos slash."""
        global_commands = self.bot.tree.get_commands()
        guild_commands = []

        if ctx.guild:
            guild_commands = self.bot.tree.get_commands(guild=discord.Object(id=ctx.guild.id))

        embed = discord.Embed(
            title="Diagnóstico do Bot",
            description="Informações sobre o estado atual do bot",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Informações Gerais",
            value=f"Nome: {self.bot.user.name}\nID: {self.bot.user.id}\nServidores: {len(self.bot.guilds)}",
            inline=False
        )

        global_cmd_list = "\n".join([f"/{cmd.name}" for cmd in global_commands]) or "Nenhum comando global encontrado"
        embed.add_field(
            name=f"Comandos Globais ({len(global_commands)})",
            value=f"```{global_cmd_list}```",
            inline=False
        )

        if ctx.guild:
            guild_cmd_list = "\n".join([f"/{cmd.name}" for cmd in guild_commands]) or "Nenhum comando específico do servidor encontrado"
            embed.add_field(
                name=f"Comandos do Servidor ({len(guild_commands)})",
                value=f"```{guild_cmd_list}```",
                inline=False
            )

        await ctx.send(embed=embed)

def setup(bot):
    cog = AIChatCommands(bot)
    bot.add_cog(cog)

    bot.tree.add_command(cog.chat_slash)
    bot.tree.add_command(cog.clear_history_slash)
    bot.tree.add_command(cog.personality_slash)

    logger.info(f"Comandos de chat com IA registrados! Comandos slash: {len(bot.tree.get_commands())}")
