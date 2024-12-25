from dataclasses import dataclass
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional

@dataclass
class Address(BaseModel):
    text: str
class AddressDetails(BaseModel):
    locality_id: Optional[int] = Field(alias="LocalityId", default=None)
    locality_name: Optional[str] = Field(alias="LocalityName", default=None)
    street_id: Optional[int] = Field(alias="StreetId", default=None)
    street_name: Optional[str] = Field(alias="StreetName", default=None)
    street_type: Optional[str] = Field(alias="StreetType", default=None)
    house_number: Optional[str] = Field(alias="HouseNumber", default=None)
    comment: Optional[str] = Field(alias="Comment", default=None)

class Location(BaseModel):
    latitude: Optional[float] = Field(alias="Latitude", default=None)
    longitude: Optional[float] = Field(alias="Longitude", default=None)

class WorkingTime(BaseModel):
    day_index: int = Field(alias="DayIndex")
    day_alias: str = Field(alias="DayAlias")
    working_time_start: Optional[int] = Field(alias="WorkingTimeStart", default=None)
    working_time_end: Optional[int] = Field(alias="WorkingTimeEnd", default=None)

class Pizzeria(BaseModel):
    id: int = Field(alias="Id")
    country_id: int = Field(alias="CountryId")
    name: str = Field(alias="Name")
    alias: Optional[str] = Field(alias="Alias", default=None)
    address: str = Field(alias="Address")
    address_text: Optional[str] = Field(alias="AddressText")
    orientation: Optional[str] = Field(alias="Orientation", default=None)
    square: Optional[float] = Field(alias="Square", default=None)
    format_name: Optional[str] = Field(alias="FormatName", default=None)
    delivery_enabled: bool = Field(alias="DeliveryEnabled", default=False)
    stationary_enabled: bool = Field(alias="StationaryEnabled", default=False)
    is_express: bool = Field(alias="IsExpress", default=False)
    min_delivery_order_price: Optional[float] = Field(alias="MinDeliveryOrderPrice", default=None)
    manager_phone_number: Optional[str] = Field(alias="ManagerPhoneNumber", default=None)
    location: Optional[Location] = Field(alias="Location")
    address_details: AddressDetails = Field(alias="AddressDetails")

    # в апишке додопиццы есть различия данных
    # между public и global api
    # пришлось делать так
    restaurant_week_working_time: Optional[List[WorkingTime]] = Field(alias="RestaurantWeekWorkingTime", default=[])
    stationary_week_working_time: Optional[List[WorkingTime]] = Field(alias="StationaryWeekWorkTime", default=[])
    delivery_week_working_time: Optional[List[WorkingTime]] = Field(alias="DeliveryWeekWorkingTime", default=[])
    delivery_week_work_time: Optional[List[WorkingTime]] = Field(alias="DeliveryWeekWorkTime", default=[])
    
    begin_date_work: Optional[str] = Field(alias="BeginDateWork")
    employee_count: Optional[int] = Field(alias="EmployeeCount", default=None)
    is_temporarily_closed: bool = Field(alias="IsTemporarilyClosed", default=False)

    class Config:
        populate_by_name = True

    @model_validator(mode='before')
    def check_optional_fields(cls, values):
        for field in cls.__annotations__:
            if values.get(field) is None and field not in values:
                values[field] = None
        return values

class PizzeriaLite(BaseModel):
    id: int
    name: str
    address: str
    startDate: str
    address: Address

@dataclass
class Country(BaseModel):
    id: int
    code: str
    name: str
    currency: str