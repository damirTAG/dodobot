import matplotlib.pyplot as plt
import aiohttp, time, json, os

from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

EXCHANGE_API_URL = "https://api.exchangerate.host/live"
EXCHANGE_CACHE_FILE = "exchange_cache.json"
CACHE_DURATION = 86400

def _is_cache_valid() -> bool:
    if not os.path.exists(EXCHANGE_CACHE_FILE):
        return False
    cache_age = time.time() - os.path.getmtime(EXCHANGE_CACHE_FILE)
    return cache_age < CACHE_DURATION

async def fetch_currency_rates():
    if _is_cache_valid():
        with open(EXCHANGE_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    access_key = os.getenv("EXCHANGERATE_APIKEY")
    if not access_key:
        raise EnvironmentError("Missing EXCHANGERATE_APIKEY in .env")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{EXCHANGE_API_URL}?access_key={access_key}") as response:
            data = await response.json()

            if not data.get("success"):
                raise ValueError("❌ Currency API request failed")

            quotes = data.get("quotes", {})
            rates = {k[3:]: v for k, v in quotes.items()}  # 'USDKZT' → 'KZT': rate

            with open(EXCHANGE_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(rates, f)

            return rates

async def generate_revenue_chart(countries):
    currency_rates: dict = await fetch_currency_rates()
    country_names = []
    revenues_usd = []
    labels = []

    for country in countries:
        currency = country.currency.upper()
        rate = currency_rates.get(currency, 1.0)
        revenue_in_usd = country.revenue / rate

        country_names.append(country.countryCode.upper())
        revenues_usd.append(revenue_in_usd)
        labels.append(f"{round(revenue_in_usd):,} USD")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(country_names, revenues_usd, color='green')

    ax.set_title("Доход всех пиццерий Dodo за последний месяц (в USD)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Страны", fontsize=12)
    ax.set_ylabel("Доход (USD)", fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for i, usd in enumerate(revenues_usd):
        ax.text(i, usd, labels[i], ha='center', va='bottom', fontsize=10)

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)

    return buffer