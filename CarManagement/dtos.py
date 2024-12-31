from datetime import date
from pydantic import BaseModel


class CreateMaintenanceRequest(BaseModel):
    garage_id: int
    car_id: int
    service_type: str
    scheduled_date: date


class CreateCarRequest(BaseModel):
    make: str | None
    model: str | None
    production_year: date | None
    licence_plate: str | None
    garage_ids: list[int] | None


class CreateGarageRequest(BaseModel):
    name: str
    location: str
    city: str
    capacity: int


class UpdateMaintenanceRequest(BaseModel):
    car_id: int | None
    service_type: str | None
    scheduled_date: date | None
    garage_id: int


class ResponseMaintenance(BaseModel):
    id: int | None
    car_id: int | None
    car_name: str | None
    service_type: str | None
    scheduled_date: date | None
    garage_id: int | None
    garage_name: str | None


class UpdateGarageRequest(BaseModel):
    name: str | None
    location: str | None
    capacity: int | None
    city: str | None


class ResponseGarage(BaseModel):
    id: int
    name: str
    location: str
    city: str
    capacity: int


class UpdateCarRequest(BaseModel):
    make: str | None
    model: str | None
    production_year: int | None
    licence_plate: str | None
    garage_ids: list[int] | None


class ResponseCar(BaseModel):
    id: int | None
    make: str | None
    model: str | None
    production_year: int | None
    licence_plate: str | None
    garages: list[ResponseGarage] | None


class MonthlyRequestsReport(BaseModel):
    year_month: str | None
    requests: int | None


class GarageDailyAvailability(BaseModel):
    date: date | None
    requests: int | None
    availabilityCapacity: int | None
