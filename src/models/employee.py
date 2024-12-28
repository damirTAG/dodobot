from pydantic import BaseModel

class Employee(BaseModel):
    Id: int
    UUId: str
    FirstName: str
    ActualCategoryName: str
    Status: str