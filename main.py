import discord
from discord.ext import commands
from discord import app_commands 
import requests

class Client(commands.Bot ):
    async def on_ready(self):
        print('ready')
        try:
            guild = discord.Object(id=1337795713517621359)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands')
        except Exception as e:
            print('Error: ' + e)

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix='!', intents=intents)

GUILD_ID = discord.Object(id=1337795713517621359)

# DAILY COMMAND
@client.tree.command(name="daily", description="Get daily stock data", guild=GUILD_ID)
async def daily_printer(interaction: discord.Interaction, ticker: str):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey='
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        await interaction.response.send_message(f"Error fetching data for {ticker}. Please check the ticker symbol or try again later.")
        return

    latest_date = list(data["Time Series (Daily)"].keys())[0]
    daily_data = data["Time Series (Daily)"][latest_date]

    embed = discord.Embed(title=f"Daily Stock Data for {ticker.upper()}", description=f"Date: {latest_date}", color=discord.Color.blue())
    embed.add_field(name="Open", value=f"${daily_data['1. open']}", inline=True)
    embed.add_field(name="High", value=f"${daily_data['2. high']}", inline=True)
    embed.add_field(name="Low", value=f"${daily_data['3. low']}", inline=True)
    embed.add_field(name="Close", value=f"${daily_data['4. close']}", inline=True)
    embed.add_field(name="Volume", value=f"{daily_data['5. volume']}", inline=True)

    await interaction.response.send_message(embed=embed)

# WEEKLY COMMAND
@client.tree.command(name="weekly", description="Get weekly stock data", guild=GUILD_ID)
async def weekly_printer(interaction: discord.Interaction, ticker: str):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker}&apikey='
    response = requests.get(url)
    data = response.json()

    if "Weekly Time Series" not in data:
        await interaction.response.send_message(f"Error fetching data for {ticker}. Please check the ticker symbol or try again later.")
        return

    latest_date = list(data["Weekly Time Series"].keys())[0]
    weekly_data = data["Weekly Time Series"][latest_date]

    embed = discord.Embed(title=f"Weekly Stock Data for {ticker.upper()}", description=f"Week Ending: {latest_date}", color=discord.Color.blue())
    embed.add_field(name="Open", value=f"${weekly_data['1. open']}", inline=True)
    embed.add_field(name="High", value=f"${weekly_data['2. high']}", inline=True)
    embed.add_field(name="Low", value=f"${weekly_data['3. low']}", inline=True)
    embed.add_field(name="Close", value=f"${weekly_data['4. close']}", inline=True)
    embed.add_field(name="Volume", value=f"{weekly_data['5. volume']}", inline=True)

    await interaction.response.send_message(embed=embed)

# TICKER SEARCH COMMAND
@client.tree.command(name="search", description="Search for a ticker", guild=GUILD_ID)
async def ticker_search(interaction: discord.Interaction, keywords: str):
    url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={keywords}&apikey='
    response = requests.get(url)
    data = response.json()

    if "bestMatches" not in data:
        await interaction.response.send_message(f"Error fetching data for {ticker}. Please check the ticker symbol or try again later.")
        return

    # Access the first match
    first_match = data["bestMatches"][0]
    symbol = first_match["1. symbol"]
    name = first_match["2. name"]
    region = first_match["4. region"]
    currency = first_match["8. currency"]

    # Fetch additional stock data using the symbol
    stock_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey='
    stock_response = requests.get(stock_url)
    stock_data = stock_response.json()

    # Check if the stock data is available
    if "Weekly Time Series" not in stock_data:
        await interaction.response.send_message(f"Error fetching stock data for {symbol}. Please try again later.")
        return

    latest_date = list(stock_data["Weekly Time Series"].keys())[0]
    weekly_data = stock_data["Weekly Time Series"][latest_date]

    # Create and send the embed with stock information
    embed = discord.Embed(
        title=f"{name} ({symbol}) - {region}",
        description=f"Currency: {currency}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Week Ending", value=latest_date, inline=False)
    embed.add_field(name="Open", value=f"${weekly_data['1. open']}", inline=True)
    embed.add_field(name="High", value=f"${weekly_data['2. high']}", inline=True)
    embed.add_field(name="Low", value=f"${weekly_data['3. low']}", inline=True)
    embed.add_field(name="Close", value=f"${weekly_data['4. close']}", inline=True)
    embed.add_field(name="Volume", value=f"{weekly_data['5. volume']}", inline=True)

    await interaction.response.send_message(embed=embed)

# TOP GAINERS AND LOSERS COMMAND
@client.tree.command(name="active", description="Get top gainers, losers, and most active stocks", guild=GUILD_ID)
async def active(interaction: discord.Interaction):
    url = 'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey='
    response = requests.get(url)
    data = response.json()

    if "metadata" not in data:
        await interaction.response.send_message("Error fetching data. Please try again later.")
        return

    # Format the embed with top gainers, losers, and active stocks
    embed = discord.Embed(title="Stock Market Overview", color=discord.Color.blue())
    embed.add_field(name="Top Gainers", value="```" + "\n".join(
        [f"{item['ticker']} - {item['price']} (+{item['change_percentage']}%)" for item in data['top_gainers']]) + "```", inline=False)
    embed.add_field(name="Top Losers", value="```" + "\n".join(
        [f"{item['ticker']} - {item['price']} ({item['change_percentage']}%)" for item in data['top_losers']]) + "```", inline=False)
    embed.add_field(name="Most Active", value="```" + "\n".join(
        [f"{item['ticker']} - {item['price']} (Volume: {item['volume']})" for item in data['most_actively_traded']]) + "```", inline=False)

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="news", description="Get the latest news sentiment for a specific ticker", guild=GUILD_ID)
async def news(interaction: discord.Interaction, ticker: str):
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey='
    response = requests.get(url)
    data = response.json()

    if "title" not in data:
        await interaction.response.send_message(f"Error fetching news data for {ticker.upper()}. Please try again later.")
        return

    # Get the top 5 news
    news_items = data['feed'][:5]

    embed = discord.Embed(title=f"Latest News for {ticker.upper()}", color=discord.Color.blue())

    for item in news_items:
        title = item['title']
        url = item['url']
        sentiment = item['overall_sentiment_label']
        summary = item['summary']

        embed.add_field(
            name=title,
            value=f"[Read more]({url})\nSentiment: {sentiment}\n\nSummary: {summary}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

# EARNINGS DATA COMMAND
@client.tree.command(name="earnings", description="Get the earnings data for a specific ticker", guild=GUILD_ID)
async def earnings_data(interaction: discord.Interaction, ticker: str):
    url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={ticker.upper()}&apikey='
    response = requests.get(url)
    data = response.json()

    # Check if 'annualEarnings' exists in the response
    if "annualEarnings" not in data:
        # Handle the error if 'annualEarnings' is missing
        if 'error' in data:
            error_message = data.get('error', 'Unknown error occurred.')
            await interaction.response.send_message(f"Error fetching earnings data for {ticker.upper()}: {error_message}")
        else:
            await interaction.response.send_message(f"Error fetching earnings data for {ticker.upper()}. Please try again later.")
        return

    # Get the last 5 years of earnings data
    earnings_data = data['annualEarnings'][:5]

    embed = discord.Embed(title=f"Earnings Data for {ticker.upper()}", color=discord.Color.blue())

    for item in earnings_data:
        fiscal_date = item['fiscalDateEnding']
        reported_eps = item['reportedEPS']

        embed.add_field(
            name=f"Fiscal Year Ending {fiscal_date}",
            value=f"Reported EPS: ${reported_eps}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


client.run('MTMzNzc5NjcxOTAwNTQwNTMxNg.GDNUU3.r9ei6U_W52N7ypur1u60MHNQhn1dM-_YfUCKxw')