from pydantic import BaseModel


class MedicineRequest(BaseModel):
    medicine_name: str


class Alternative(BaseModel):
    medicine: str
    manufacturer: str
    actual_price: float
    predicted_price: float


class SearchedMedicine(BaseModel):
    name: str
    manufacturer: str
    actual_price: float
    predicted_price: float


class MedicineResponse(BaseModel):
    searched_medicine: SearchedMedicine
    alternatives: list[Alternative]