from sqlalchemy.orm import Session as ORMSession
from model import Maintenance, Car, Garage
from fastapi import HTTPException
from dtos import CreateMaintenanceRequest, ResponseMaintenance, UpdateMaintenanceRequest
from database import Session, engine
from datetime import date


def get_maintenance_by_id(id: int, session: ORMSession):
    maintenance = session.get(Maintenance, id)
    if id is None:
        raise HTTPException(status_code=400, detail="Bad request!")
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Maintenance not found!")
    return maintenance


def get_maintenances(car_id: int | None, garage_id: int | None,
                     start_date: date | None, end_date: date | None) -> list[ResponseMaintenance]:
    with Session() as session:
        query = session.query(Maintenance).join(Maintenance.car).join(Maintenance.garage).distinct()
        if car_id:
            query = query.where(Maintenance.car_id == car_id)
        if garage_id:
            query = query.where(Maintenance.garage_id == garage_id)
        if start_date:
            query = query.where(Maintenance.scheduled_date >= start_date)
        if end_date:
            query = query.where(Maintenance.scheduled_date <= end_date)

        maintenances = query.all()
        if not maintenances:
            raise HTTPException(status_code=404, detail="No maintenances found")
        return [map_maintenance_to_response(maintenance) for maintenance in maintenances]


def create_maintenance(request: CreateMaintenanceRequest) -> ResponseMaintenance:
    with Session() as session:
        if request.car_id is None or request.garage_id is None or request.service_type is None or request.scheduled_date is None:
            raise HTTPException(status_code=400, detail="Bad request!")

        car = session.query(Car).where(Car.id == request.car_id).first()
        garage = session.query(Garage).where(Garage.id == request.garage_id)

        if not car:
            raise HTTPException(status_code=400, detail="Invalid car_id")
        if not garage:
            raise HTTPException(status_code=400, detail="Invalid garage_id")

        new_maintenance = map_request_to_maintenance(request)
        session.add(new_maintenance)
        session.commit()
        session.refresh(new_maintenance)
        return map_maintenance_to_response(new_maintenance)



# def update_maintenance(id: int, update_maintenance: UpdateMaintenance) -> ResponseMaintenance:
#     with Session() as session:
#         maintenance = get_maintenance_by_id(id, session)
#         if id is None:
#             raise HTTPException(status_code=400, detail="Bad Request!")
#         if not maintenance:
#             raise HTTPException(status_code=404, detail="Maintenance not found.")
#         if update_maintenance.


def map_maintenance_to_response(maintenance: Maintenance) -> ResponseMaintenance:
    return ResponseMaintenance(
        id=maintenance.id,
        car_id=maintenance.car_id,
        car_name=maintenance.car.make if maintenance.car else None,
        service_type=maintenance.service_type,
        scheduled_date=maintenance.scheduled_date,
        garage_id=maintenance.garage_id,
        garage_name=maintenance.garage.name if maintenance.garage else None
    )


def map_request_to_maintenance(request: CreateMaintenanceRequest) -> Maintenance:
    return Maintenance(
        garage_id=request.garage_id,
        car_id=request.car_id,
        service_type=request.service_type,
        scheduled_date=request.scheduled_date
    )