import aiohttp
import os

from aiocache import Cache, cached
from aiocache.serializers import JsonSerializer

from dotenv import load_dotenv
from typing import List

from src.models.basic import Country, Pizzeria, PizzeriaLite
from src.models.revenue import Revenue, CountryFinStatsResponse

cache = Cache.from_url("memory://")

class DodoAPI:
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv("PUBLIC_API_URL")
        self.global_url = os.getenv("GLOBAL_API_URL")
        self.headers = {"Accept": "application/json"}
    
    @cached(ttl=3600)
    async def get_countries(self) -> List[Country]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.global_url}countries/list") as resp:
                data = await resp.json()
                return [Country.model_validate(country) for country in data["countries"]]
    
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
    
    async def get_pizzeria_stats(self, country_id: int, pizzeria_id: int) -> tuple[Revenue, Revenue]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.global_url}revenue/pizzeria/{country_id}/{pizzeria_id}/yesterday") as yesterday_resp:
                yesterday_data = await yesterday_resp.json()
                yesterday_revenue = Revenue.model_validate(yesterday_data["countries"][0])

            async with session.get(f"{self.global_url}revenue/pizzeria/{country_id}/{pizzeria_id}/today") as today_resp:
                today_data = await today_resp.json()
                today_revenue = Revenue.model_validate(today_data["countries"][0])

            return  today_revenue, yesterday_revenue
        
    async def search_pizzerias_by_name(self, country_code: str, name: str) -> List[Pizzeria]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.base_url}/{country_code}/api/v1/unitinfo/pizzerias") as resp:
                if resp.status == 200:
                    pizzerias_data = await resp.json()
                    pizzerias = [
                        Pizzeria(**pizzeria) for pizzeria in pizzerias_data
                        if name.lower() in pizzeria['Name'].lower()
                    ]
                    return pizzerias
                else:
                    return []
