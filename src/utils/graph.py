import matplotlib.pyplot as plt
from io import BytesIO

def generate_revenue_chart(countries):
    country_names = []
    revenues = []
    currencies = []

    for country in countries:
        country_names.append(country.countryCode.upper())
        revenues.append(country.revenue)
        currencies.append(country.currency)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(country_names, revenues, color='skyblue')

    ax.set_title("Доход всех пиццерий Dodo за последний месяц", fontsize=14, fontweight='bold')
    ax.set_xlabel("Страны", fontsize=12)
    ax.set_ylabel("Доход", fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for i, revenue in enumerate(revenues):
        ax.text(i, revenue, f"{revenue:,} {currencies[i]}", ha='center', va='bottom', fontsize=10)

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)

    return buffer