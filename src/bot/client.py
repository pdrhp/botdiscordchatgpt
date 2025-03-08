import discord
from discord.ext import commands
from discord.ext import tasks

from src.utils.logger import get_logger
from src.ai.message_manager import message_manager

logger = get_logger(__name__)

def create_bot(config):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    command_prefix = config.command_prefix

    bot = commands.Bot(
        command_prefix=command_prefix,
        intents=intents,
        help_command=None,
        description=config.description
    )

    @bot.event
    async def on_ready():
        logger.info(f"Bot conectado como {bot.user.name} (ID: {bot.user.id})")
        logger.info(f"Usando discord.py versão {discord.__version__}")

        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{command_prefix}ajuda | Conversando com IA"
        )
        await bot.change_presence(activity=activity)

        from src.bot.commands import register_commands
        await register_commands(bot)

        logger.info("Bot está pronto para uso!")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"⚠️ Argumento ausente: {error.param.name}")
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⚠️ Você não tem permissão para usar este comando.")
            return

        logger.error(f"Erro no comando {ctx.command}: {error}")
        await ctx.send("❌ Ocorreu um erro ao processar o comando.")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        await bot.process_commands(message)

        if bot.user.mentioned_in(message) and not message.mention_everyone:
            store = message_manager.get_store(str(message.channel.id))

            store.add_user_message(
                str(message.author.id),
                message.author.display_name,
                message.content.replace(f'<@{bot.user.id}>', '').strip()
            )

            async with message.channel.typing():
                try:
                    from src.ai.groq import generate_response as groq_generate
                    from src.ai.openai import generate_response as openai_generate

                    try:
                        response = await groq_generate(store.get_messages())
                    except Exception as e:
                        logger.warning(f"Erro ao usar Groq, tentando OpenAI: {e}")
                        response = await openai_generate(store.get_messages())

                    store.add_assistant_message(response)

                    if len(response) <= 2000:
                        await message.reply(response)
                    else:
                        for i in range(0, len(response), 2000):
                            chunk = response[i:i+2000]
                            if chunk:
                                if i == 0:
                                    await message.reply(chunk)
                                else:
                                    await message.channel.send(chunk)

                except Exception as e:
                    logger.error(f"Erro ao processar menção: {e}")
                    await message.reply("❌ Desculpe, ocorreu um erro ao processar sua mensagem.")

    @tasks.loop(hours=24)
    async def cleanup_old_data():
        try:
            removed = message_manager.cleanup_old_stores(max_age_seconds=86400)
            if removed > 0:
                logger.info(f"Limpeza: {removed} armazenamentos de mensagens inativos removidos")

            if message_manager.use_persistence:
                deleted = message_manager.cleanup_db(max_age_seconds=604800)
                if deleted > 0:
                    logger.info(f"Limpeza: {deleted} mensagens antigas removidas do banco de dados")

        except Exception as e:
            logger.error(f"Erro durante limpeza periódica: {e}")

    @cleanup_old_data.before_loop
    async def before_cleanup():
        await bot.wait_until_ready()

    cleanup_old_data.start()

    return bot
