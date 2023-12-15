import discord
from discord.ext import commands
from openai import OpenAI
import requests
from io import BytesIO

client = OpenAI(api_key="")

def bot_chat(user_id, message):
    conversation_history = {}
    conversation = conversation_history.get(user_id, [])
    conversation.append({"role": "user", "content": message})
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "Tu es un assistant qui doit répondre aux questions des utilisateurs."},
            *conversation
        ]
    )
    response = completion.choices[0].message.content
    conversation.append({"role": "assistant", "content": response})
    conversation_history[user_id] = conversation
    return response


def image(message):
    response = client.images.generate(
        model="dall-e-3",
        prompt=message,
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = response.data[0].url
    image = requests.get(image_url)
    image_bytes = BytesIO(image.content)
    return image_bytes

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
TOKEN = ''

@bot.event
async def on_ready():
    print("Le bot est prêt !")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.tree.command(name="chat", description="Engagez un chat avec le bot")
async def fn_chat(interaction, prompt: str):
    await interaction.response.defer()
    user_id = str(interaction.user.id)
    response = bot_chat(user_id, prompt)
    await interaction.followup.send("Question : " + prompt + "\n" "Réponse : " + response)


@bot.tree.command(name="image", description="Générez une image grâce au bot")
async def generer_image(interaction, prompt: str):
    await interaction.response.defer()
    reponse = image(prompt)
    await interaction.followup.send("Question : " + prompt, file=discord.File(reponse, 'image.png'))

bot.run(TOKEN)
