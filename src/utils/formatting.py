from src.models.basic import Pizzeria
from src.models.revenue import Revenue, CountryFinStatsResponse, CountryRevenue

from itertools import groupby
from typing import List

# def format_country_info(country: Country) -> str:
#     return f"""
# <b>{country.name}</b>
# Total Revenue: ${country.total_revenue:,.2f}
# Number of Pizzerias: {len(country.pizzerias)}
# """
def format_working_hours(working_time_list: List) -> str:
    day_map = {
        "Monday": "Mon",
        "Tuesday": "Tue",
        "Wednesday": "Wed",
        "Thursday": "Thu",
        "Friday": "Fri",
        "Saturday": "Sat",
        "Sunday": "Sun",
    }

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    working_time_list.sort(key=lambda x: (days_order.index(x.day_alias), x.working_time_start, x.working_time_end))

    grouped = []
    for _, group in groupby(
        working_time_list, 
        key=lambda x: (x.working_time_start, x.working_time_end)
    ):
        group = list(group)
        start_time = f"{group[0].working_time_start // 3600:02d}:00"
        end_time = f"{group[0].working_time_end // 3600:02d}:00"
        days = [day_map[time.day_alias] for time in group]

        formatted_days = []
        temp = [days[0]]
        for i in range(1, len(days)):
            if days_order.index(group[i].day_alias) == days_order.index(group[i - 1].day_alias) + 1:
                temp.append(days[i])
            else:
                formatted_days.append(f"{temp[0]}-{temp[-1]}" if len(temp) > 1 else temp[0])
                temp = [days[i]]
        formatted_days.append(f"{temp[0]}-{temp[-1]}" if len(temp) > 1 else temp[0])

        grouped.append(f"{', '.join(formatted_days)}: {start_time}-{end_time}")

    return "\n".join(grouped)

def format_pizzeria_info(pizzeria: Pizzeria) -> str:
    working_time_list = (
        pizzeria.restaurant_week_working_time
        if hasattr(pizzeria, 'restaurant_week_working_time') and pizzeria.restaurant_week_working_time
        else getattr(pizzeria, 'stationary_week_working_time', [])
    )
    delivery_working_time_list = (
        pizzeria.delivery_week_working_time
        if hasattr(pizzeria, 'delivery_week_working_time') and pizzeria.delivery_week_working_time
        else getattr(pizzeria, 'delivery_week_work_time', [])
    )
    restaurant_hours = format_working_hours(working_time_list)
    delivery_hours = format_working_hours(delivery_working_time_list)

    return f"""
<b>{pizzeria.name} 🍕</b>
<b>Адрес:</b> {pizzeria.address}
<b>Телефон менеджера:</b> {pizzeria.manager_phone_number or "Не указан"} 📞
<b>Начало работы:</b> {pizzeria.begin_date_work if pizzeria.begin_date_work else 'Не указано'} 🗓️
<b>Количество сотрудников:</b> {pizzeria.employee_count or "Не указано"} 👥
<b>Временно закрыт:</b> {"Да" if pizzeria.is_temporarily_closed else "Нет"} 🚫
<b>Мин. сумма на доставку:</b> {pizzeria.min_delivery_order_price if pizzeria.min_delivery_order_price else "Неизв."} 😋

<b>Режим работы ресторана 🏢:</b>
{restaurant_hours}

<b>Режим работы доставки 🚚:</b>
{delivery_hours}
"""

def format_stats(stats: Revenue, currency: str) -> str:
    return f"""
<b>Дата:</b> {stats.date.strftime('%Y-%m-%d')}
🏠 <b>Доход от кассы:</b> {stats.stationaryRevenue:,.2f} {currency} ({stats.stationaryOrderCount} заказов)
🚚 <b>Доход от доставки:</b> {stats.deliveryRevenue:,.2f} {currency} ({stats.deliveryOrderCount} заказов)
💵 <b>Общий доход:</b> {stats.revenue:,.2f} {currency}
📦 <b>Общее количество заказов:</b> {stats.orderCount}
📊 <b>Средняя стоимость заказа:</b> {stats.avgCheck:,.2f} {currency}
"""

def format_country_stats(country_name: str, stats: CountryFinStatsResponse) -> str:
    return f"""
<b>{country_name}</b>:

💰 <b>Валюта:</b> {stats.currency}

<b>Доходы:</b>
- <b>текущего года:</b> {stats.current_year_progressive_total:,.0f} {stats.currency}
- <b>прошлого года:</b> {stats.previous_year_revenue:,.0f} {stats.currency}
- <b>текущего месяца:</b> {stats.current_month_progressive_total:,.0f} {stats.currency}
- <b>в прошлом месяце ({stats.previous_month.name} {stats.previous_month.year}):</b> {stats.previous_month.revenue:,.0f} {stats.currency}
- <b>за тот же месяц год назад ({stats.year_ago.name} {stats.year_ago.year}):</b> {stats.year_ago.revenue:,.0f} {stats.currency}
- <b>сегодня:</b> {stats.today_progressive_total:,.0f} {stats.currency}

🍕 <b>Работающие пиццерии:</b> {stats.working_pizzerias}
"""

import locale
import pycountry
import flag

locale.setlocale(locale.LC_ALL, '')

def format_revenue(countries: List[CountryRevenue]):
    formatted_revenue = []

    for country in countries:
        country_data = pycountry.countries.get(alpha_2=country.countryCode.upper())
        country_name = country_data.name if country_data else "Неизвестная страна"
        country_emoji = flag.flag(country.countryCode) if country_data else "🏳️"

        revenue = locale.format_string("%d", country.revenue, grouping=True)
        formatted_revenue.append(
            f"{country_emoji} {country_name}: {revenue:,.2f} {country.currency}"
        )

    return "\n".join(formatted_revenue)

def get_currency_from_country_code(country_code: str) -> str:
    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if not country:
            return "UNKNOWN"

        currency = pycountry.currencies.get(numeric=country.numeric)
        return currency.alpha_3 if currency else "UNKNOWN"
    except Exception as e:
        print(f"Ошибка при получении валюты для страны {country_code}: {e}")
        return "UNKNOWN"