from pydantic import BaseModel
from datetime import datetime
from typing import List

class Revenue(BaseModel):
    countryId: int
    countryCode: str
    unitId: int
    date: datetime
    stationaryRevenue: float
    stationaryOrderCount: int
    deliveryRevenue: float
    deliveryOrderCount: int
    revenue: float
    orderCount: int
    avgCheck: float

class RevenueResponse(BaseModel):
    countries: List[Revenue]
    errors: List[str]

class PreviousMonth(BaseModel):
    revenue: int
    name: str
    year: int

class YearAgo(BaseModel):
    revenue: int
    name: str
    year: int

class CountryFinStatsResponse(BaseModel):
    currency: str
    current_year_progressive_total: int
    previous_year_revenue: int
    current_month_progressive_total: int
    previous_month: PreviousMonth
    year_ago: YearAgo
    today_progressive_total: int
    working_pizzerias: int

class CountryRevenue(BaseModel):
    countryId: int
    countryCode: str
    currency: str
    revenue: int