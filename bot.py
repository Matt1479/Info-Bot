# Docs:     https://discordpy.readthedocs.io/en/stable/#getting-started
# Tutorial: https://www.youtube.com/watch?v=UCmv8LxF8Xg

from Coinbase import Coinbase
import discord
from discord.ext import commands
import helpers
import requests

# Open token.txt in read mode, store the reference inside of
# token_file variable
with open("token.txt", "r") as token_file:
    # Read a single line and store it inside of token
    token = token_file.readline()

# Intents allow the bot to "subscribe" or "listen" to specific events
intents = discord.Intents.all()
# Create an instance of Bot class
bot = commands.Bot(command_prefix=".", intents=intents)

# coinbase gets a reference to a new instance of Coinbase class
coinbase = Coinbase(timeout=5)

# Create an instance of Plotter
plotter = helpers.Plotter()


@bot.event
async def on_ready():
    """Called when the bot has finished logging in and
    setting things up."""
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("--------")


@bot.command()
async def echo(context: commands.Context, *messages):
    """Repeats a message (or messages) back to the user."""
    separator = " "
    # Context refers to things like: the user invoking the command, etc.
    await context.send(separator.join(messages))


@bot.command()
async def uselessfact(context: commands.Context):
    """Basic HTTP GET request."""
    response = requests.get("https://uselessfacts.jsph.pl/random.json")

    if response.status_code == 200:
        json_response = response.json()
        await context.send(json_response["text"])


@bot.command()
async def get_crypto_price(context: commands.Context, *messages):
    if len(messages) != 2:
        await context.send("Usage: .get_crypto_price crypto_currency base_currency")
    else:
        price = coinbase.get_crypto_price(
            currency_pair={"base": messages[1], "crypto": messages[0]}
        )

        if price:
            await context.send(f"{price['amount']:.02f}")
        else:
            await context.send("Usage: .get_crypto_price crypto_currency base_currency")


@bot.command()
async def get_historic_prices(context: commands.Context, *messages):
    e_messages = [
        "Usage: .get_historic_prices crypto_currency base_currency start_date end_date",
        "start_date, end_date: YYYY-MM-DD",
        "start_date >= end_date and months <= 25",
    ]

    if len(messages) != 4:
        for e_message in e_messages:
            await context.send(e_message)
    else:
        await context.send("Fetching data...")

        try:
            historic_prices = coinbase.get_historic_prices(
                {
                    "start_date": messages[2],
                    "end_date": messages[3],
                    "currency_pair": {"base": messages[1], "crypto": messages[0]},
                }
            )
        # Also catch HTTP Errors
        except Exception as e:
            return await context.send(f"Could not fetch data (reason: {e}).")

        if historic_prices:
            plotter.plot(
                helpers.list_dict_to_list(historic_prices, "date"),
                helpers.list_dict_to_list(historic_prices, "amount"),
            )
            plotter.setup("Date", "Amount", "Historic Prices", True, False)

            plotter.save("out.png")
            await context.send(file=discord.File("out.png"))

            plotter.clear()
        else:
            for e_message in e_messages:
                await context.send(e_message)


# Run the bot with the API token
bot.run(token)
