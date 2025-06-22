import matplotlib.pyplot as plt
import aiohttp
from io import BytesIO

EXCHANGE_API_URL = "https://api.exchangerate.host/latest?base=USD"

async def fetch_currency_rates():
    async with aiohttp.ClientSession() as session:
        async with session.get(EXCHANGE_API_URL) as response:
            data = await response.json()
            if not data.get("success", True):
                raise ValueError("Currency API returned failure")
            rates = data.get("rates", {})
            return {k.upper(): round(1 / v, 6) for k, v in rates.items()}

async def generate_revenue_chart(countries):
    currency_rates: dict = await fetch_currency_rates()
    country_names = []
    revenues_usd = []
    labels = []

    for country in countries:
        currency = country.currency.upper()
        rate = currency_rates.get(currency, 1.0)
        revenue_in_usd = country.revenue * rate

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