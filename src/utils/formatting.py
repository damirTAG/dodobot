from src.models.basic import Pizzeria
from src.models.revenue import Revenue, CountryFinStatsResponse

# def format_country_info(country: Country) -> str:
#     return f"""
# <b>{country.name}</b>
# Total Revenue: ${country.total_revenue:,.2f}
# Number of Pizzerias: {len(country.pizzerias)}
# """

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
    restaurant_hours = "\n".join(
        f"{time.day_alias}: {time.working_time_start // 3600:02d}:00 - {time.working_time_end // 3600:02d}:00"
        for time in working_time_list
    )
    delivery_hours = "\n".join(
        f"{time.day_alias}: {time.working_time_start // 3600:02d}:00 - {time.working_time_end // 3600:02d}:00"
        for time in delivery_working_time_list
    )

    return f"""
<b>{pizzeria.name} 🍕</b>
<b>Адрес:</b> {pizzeria.address}
<b>Телефон менеджера:</b> {pizzeria.manager_phone_number or "Не указан"} 📞
<b>Начало работы:</b> {pizzeria.begin_date_work} 🗓️
<b>Количество сотрудников:</b> {pizzeria.employee_count or "Не указано"} 👥
<b>Временно закрыт:</b> {"Да" if pizzeria.is_temporarily_closed else "Нет"} 🚫

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