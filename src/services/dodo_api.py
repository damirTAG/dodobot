import aiohttp
import asyncio
import os

from aiocache import Cache, cached

from dotenv import load_dotenv
from typing import List, Optional

from src.models.basic import Country, City, Pizzeria, PizzeriaLite
from src.models.revenue import Revenue, CountryFinStatsResponse, CountryRevenue, RevenueResponse
from src.models.employee import Employee

cache = Cache.from_url("memory://")

class DodoAPI:
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv("PUBLIC_API_URL")
        self.global_url = os.getenv("GLOBAL_API_URL")
        self.headers = {"Accept": "application/json"}
    
    @cached(ttl=360, key_builder=lambda self, f, country_code: f"pizzerias_base:{country_code}")
    async def _get_pizzerias_base(self, country_code: str) -> List[dict]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.base_url}/{country_code}/api/v1/unitinfo/pizzerias") as resp:
                if resp.status == 200:
                    return await resp.json()
                return []

    @cached(ttl=360, key_builder=lambda self, f, country_code, name: f"search_pizzerias:{country_code}:{name.lower()}")
    async def search_pizzerias_by_name(self, country_code: str, name: str) -> List[Pizzeria]:
        pizzerias_data = await self._get_pizzerias_base(country_code)
        return [
            Pizzeria(**pizzeria) 
            for pizzeria in pizzerias_data 
            if (name.lower() in pizzeria['Name'].lower()) or (name.lower() in pizzeria['Address'].lower())
        ]

    @cached(ttl=360, key_builder=lambda self, f, country_code, name: f"pizzerias:{country_code}:{name.lower()}")
    async def get_pizzerias_by_name(self, country_code: str, name: str) -> List[Pizzeria]:
        pizzerias_data = await self._get_pizzerias_base(country_code)
        return [
            Pizzeria(**pizzeria) 
            for pizzeria in pizzerias_data 
            if (name.lower() in pizzeria['Name'].lower())
        ]

    @cached(ttl=120)
    async def get_total_revenue_last_month(self) -> List[CountryRevenue]:
        cache_key = "total_revenue"
        cached_data = await cache.get(cache_key)

        if cached_data:
            return cached_data
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.global_url}revenue/monthes/last") as resp:
                data = await resp.json()
                countries = data.get("countries", [])
                data = [CountryRevenue(**country) for country in countries]
                await cache.set(cache_key, data)
                return data

    # Daily revenue
    # 
    async def get_daily_revenue(
            self, 
            country_id: int, 
            unit_id: int, 
            year: int, 
            month: int, 
            day: int
        ) -> Optional[List[CountryRevenue]]:
        url = f"{self.global_url}revenue/pizzeria/{country_id}/{unit_id}/daily/{year}/{month}/{day}"
        
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        print(f"Failed to fetch revenue data: {response.status} - {await response.text()}")
                        return None
                    
                    data = await response.json()
                    countries = data.get('countries', [])

                    revenue_data = [CountryRevenue(**country) for country in countries]
                    
                    return revenue_data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


    @cached(ttl=3600)
    async def get_countries(self) -> List[Country]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.global_url}countries/list") as resp:
                data = await resp.json()
                return [Country.model_validate(country) for country in data["countries"]]
    
    @cached(ttl=3600)
    async def get_cities(self, country_code) -> List[City]:
        cache_key = f"cities:{country_code}"
        cached_data = await cache.get(cache_key)

        if cached_data:
            return cached_data
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.base_url}/{country_code}/api/v1/GetLocalities") as resp:
                data = await resp.json()
                cities = [
                    City(
                        id=city['Id'],
                        uuid=city['UUId'],
                        name=city['Name']
                    )
                    for city in data
                ]

                await cache.set(cache_key, cities)

                return cities
    
    async def get_country_stats(self, country_code: str) -> CountryFinStatsResponse:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.base_url}/{country_code}/api/v1/FinancialMetrics") as resp:
                data = await resp.json()
                # print(data)
                return CountryFinStatsResponse(**data['response'])

    @cached(ttl=3600)
    async def get_pizzerias(self, country_id: int) -> List[Pizzeria]:
        cache_key = f"pizzerias:{country_id}"
        cached_data = await cache.get(cache_key)

        if cached_data:
            return cached_data

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.global_url}pizzerias/all/{country_id}") as resp:
                data = await resp.json()

                for country in data["countries"]:
                    if country["countryId"] == country_id:
                        pizzerias = [PizzeriaLite.model_validate(pizzeria) for pizzeria in country["pizzerias"]]

                        await cache.set(cache_key, pizzerias)
                        return pizzerias

                return []
            
    @cached(ttl=360)
    async def get_pizzeria_details(self, id: int, country_code: str) -> Pizzeria:
        cache_key = f"pizzeria:{country_code}:{id}"
        cached_data = await cache.get(cache_key)

        if cached_data:
            return cached_data 

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.base_url}/{country_code}/api/v1/unitinfo/{id}") as resp:
                data = await resp.json()
                pizzeria = Pizzeria(**data)

                await cache.set(cache_key, pizzeria)
                return pizzeria
            
    async def get_pizzeria_details_global(self, country_id, pizzeria_id):
        cache_key = f"pizzeria:{country_id}:{pizzeria_id}"
        cached_data = await cache.get(cache_key)

        if cached_data:
            return cached_data
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.global_url}pizzerias/unit/{country_id}/{pizzeria_id}") as resp:
                data = await resp.json()
                pizzeria = data['countries']

                await cache.set(cache_key, pizzeria)
                return pizzeria
    
    async def get_pizzeria_stats(self, country_id: int, pizzeria_id: int) -> tuple[Revenue, Revenue, float]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            yesterday_resp, today_resp, month_resp = await asyncio.gather(
                session.get(f"{self.global_url}revenue/pizzeria/{country_id}/{pizzeria_id}/yesterday"),
                session.get(f"{self.global_url}revenue/pizzeria/{country_id}/{pizzeria_id}/today"),
                session.get(f"{self.global_url}revenue/pizzeria/{country_id}/{pizzeria_id}/monthes/last")
            )
            
            yesterday_data = await yesterday_resp.json()
            today_data = await today_resp.json()
            month_data = await month_resp.json()

            yesterday_revenue = Revenue.model_validate(yesterday_data["countries"][0])
            today_revenue = Revenue.model_validate(today_data["countries"][0])
            month_revenue = month_data['countries'][0]['monthes'][0]['revenue']

            return today_revenue, yesterday_revenue, month_revenue

    @cached(ttl=3600)
    async def get_top_products_month(
        self, 
        country_code: str, 
        start_date: str, 
        end_date: str
        ):
        cache_key = f"products_top:{country_code}"
        cached_data = await cache.get(cache_key)

        if cached_data:
            return cached_data
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.base_url}/{country_code}/api/v1/products/top?start={start_date}&end={end_date}") as resp: 
                data = resp.json()
                await cache.set(cache_key, data)
                return data
    # Employees
    # https://publicapi.dodois.io/{country_code}/api/v1/AllEmployeesOnShift/{unitid}
    @cached(ttl=4600)
    async def get_employee_onshift(self, country_code: str, unitid: int) -> List[Employee]:
        cache_key = f"employees:{country_code}:{unitid}"
        cached_data = await cache.get(cache_key)

        if cached_data:
            return cached_data
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.base_url}/{country_code}/api/v1/EmployeesOnShift/{id}") as resp:
                data = await resp.json()
                emp = [
                    Employee(
                        **employees
                    )
                    for employees in data
                ]

                await cache.set(cache_key, emp)

                return emp