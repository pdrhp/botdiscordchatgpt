import os
import discord
import openai
from dotenv import load_dotenv

load_dotenv('tokens.env')

client = discord.Client()
openai.api_key = os.getenv('OPENAI_API_KEY')

@client.event
async def on_ready():
    print(f'{client.user} está conectado ao Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!pergunta'):
        question = message.content.split('!pergunta ',1)[1]
        response = openai.Completion.create(
            engine='davinci',
            prompt=f'Q: {question}\nA:',
            temperature=0.5,
            max_tokens=1024,
            n=1,
            stop=None,
            timeout=10,
        )
        answer = response.choices[0].text
        await message.channel.send(answer)
        
TOKEN = os.getenv('DISCORD_TOKEN')
client.run(TOKEN)
