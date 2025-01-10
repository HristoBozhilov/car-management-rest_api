from sqlalchemy import extract, func
from sqlalchemy.orm import Session as ORMSession
from model import Maintenance, Car, Garage
from fastapi import HTTPException
from dtos import CreateMaintenanceRequest, MaintenanceResponse, UpdateMaintenanceRequest, MonthlyRequestsReport
from database import Session, engine
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def get_maintenance_by_id(id: int, session: ORMSession):
    maintenance = session.get(Maintenance, id)
    if id is None:
        raise HTTPException(status_code=400, detail="Bad request!")
    if maintenance is None:
        raise HTTPException(status_code=404, detail="Maintenance not found!")
    return maintenance


def get_maintenances(car_id: int | None, garage_id: int | None,
                     start_date: date | None, end_date: date | None) -> list[MaintenanceResponse]:
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


def create_maintenance(request: CreateMaintenanceRequest) -> MaintenanceResponse:
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


def update_maintenance(id: int, request: UpdateMaintenanceRequest) -> MaintenanceResponse:
    with Session() as session:
        maintenance = session.query(Maintenance).where(Maintenance.id == id).first()
        if id is None:
            raise HTTPException(status_code=400, detail="Id must be provided")
        if not maintenance:
            raise HTTPException(status_code=404, detail="Maintenance not found.")

        if request.car_id is None or request.garage_id is None:
            raise HTTPException(status_code=400, detail="Car_id and Garage_id must be provided.")

        car = session.query(Car).where(Car.id == request.car_id).first()
        if not car:
            raise HTTPException(status_code=400, detail="Invalid car_id")

        garage = session.query(Garage).where(Garage.id == request.garage_id).first()
        if not garage:
            raise HTTPException(status_code=400, detail="Invalid garage_id")

        maintenance.car_id = request.car_id
        maintenance.service_type = request.service_type
        maintenance.scheduled_date = request.scheduled_date
        maintenance.garage_id = request.garage_id
        session.commit()
        session.refresh(maintenance)
        return map_maintenance_to_response(maintenance)


def delete_maintenance(id: int):
    with Session() as session, session.begin():
        maintenance = get_maintenance_by_id(id, session)
        if maintenance is None:
            raise HTTPException(status_code=404, detail="Maintenance is not found!")
        if id is None:
            raise HTTPException(status_code=400, detail="Id must be provided")
        session.delete(maintenance)
        session.commit()


def get_monthly_report_service(garage_id: int, start_month_str: str, end_month_str: str ) -> list[MonthlyRequestsReport]:
    with Session() as session:
        try:
            start_month = datetime.strptime(start_month_str, "%Y-%m")
            end_month = datetime.strptime(end_month_str, "%Y-%m")
        except ValueError:
            raise HTTPException(status_code=400, detail="The month must be in yyyy-mm format")
        if start_month > end_month:
            raise HTTPException(status_code=400, detail="Started month cannot be later than ended month.")
        if start_month_str is None:
            raise HTTPException(status_code=400, detail="Started month is required")
        if end_month_str is None:
            raise HTTPException(status_code=400, detail="Ended month is required")
        if garage_id is None:
            raise HTTPException(status_code=400, detail="Garage id is required")

        months_in_range = [
            start_month + relativedelta(months=i)
            for i in range((end_month.year - start_month.year) * 12 + end_month.month - start_month.month + 1)
        ]

        query = session.query(Maintenance)
        if garage_id:
            query = query.where(Maintenance.garage_id == garage_id)
        query = query.where(Maintenance.scheduled_date >= start_month, Maintenance.scheduled_date <= end_month)

        grouped_data = query.with_entities(
            extract('year', Maintenance.scheduled_date).label('year'),
            extract('month', Maintenance.scheduled_date).label('month'),
            func.count().label('count')
        ).group_by('year', 'month').all()

        report = [
            MonthlyRequestsReport(
                year_month=f"{int(data.year)}-{int(data.month):02}",
                requests=data.count
            )
            for data in grouped_data
        ]

        for month in months_in_range:
            if not any(r.year_month == month.strftime("%Y-%m") for r in report):
                report.append(MonthlyRequestsReport(year_month=month.strftime("%Y-%m"), requests=0))

        return sorted(report, key=lambda r: r.year_month)


def map_maintenance_to_response(maintenance: Maintenance) -> MaintenanceResponse:
    return MaintenanceResponse(
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
