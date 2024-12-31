from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

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

class MetricsData(BaseModel):
    unitId: int
    revenue: float
    count: int
    stationaryRevenue: float
    stationaryCount: int
    deliveryRevenue: float
    deliveryCount: int
    pickupRevenue: float
    pickupCount: int
    stationaryMobileRevenue: float
    stationaryMobileCount: int
    deliveryMobileRevenue: float
    deliveryMobileCount: int
    pickupMobileRevenue: float
    pickupMobileCount: int

class CountryRevenue(BaseModel):
    countryId: int
    countryCode: str
    metrics: List[MetricsData]

class ErrorData(BaseModel):
    countryId: int
    countryCode: str

class CountryRevenueResponse(BaseModel):
    countries: List[CountryRevenue]
    errors: Optional[List[ErrorData]] = None
    day: str

class CountriesRevenue(BaseModel):
    countryId: int
    countryCode: str
    currency: str
    revenue: int