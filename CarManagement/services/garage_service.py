from sqlalchemy.orm import Session as ORMSession, Session
from model import Garage
from dtos import GarageResponse, CreateGarageRequest, UpdateGarageRequest
from fastapi import HTTPException


def get_garage_by_id(id: int, session: ORMSession):
    garage = session.get(Garage, id)
    if garage is None:
        raise HTTPException(status_code=404, detail="Garage not found")
    return garage


def get_garages(city: str | None = None) -> list[GarageResponse]:
    with Session() as session:
        if city is None:
            garages = session.query(Garage).all()
        else:
            search_city = f"%{city}%"
            garages = session.query().where(Garage.city.ilike(search_city)).all()

        return [map_garage_to_response(garage) for garage in garages]


def create_garage(request: CreateGarageRequest) -> GarageResponse:
    with Session() as session:
        if request.city is None or request.name is None or request.capacity is None or request.location is None:
            raise HTTPException(status_code=400, detail="Bad Request!")

        new_garage = map_request_to_garage(request)
        session.add(new_garage)
        session.commit()
        session.refresh(new_garage)
        return map_garage_to_response(new_garage)


def update_garage(id: int, request: UpdateGarageRequest) -> GarageResponse:
    with Session() as session:
        garage = session.query().where(Garage.id == id).first()

        if id is None:
            raise HTTPException(status_code=400, detail="Id must be provided")
        if garage is None:
            raise HTTPException(status_code=404, detail="Garage is not found.")
        if request.name is None:
            raise HTTPException(status_code=400, detail="Name is required.")
        if request.city is None:
            raise HTTPException(status_code=400, detail="City is required.")
        if request.capacity is None:
            raise HTTPException(status_code=400, detail="Capacity is required.")
        if request.location is None:
            raise HTTPException(status_code=400, detail="Location is required.")

        garage.name = request.name
        garage.city = request.city
        garage.capacity = request.capacity
        garage.location = request.location
        session.commit()
        session.refresh(garage)
        return map_garage_to_response(garage)


def map_garage_to_response(garage: Garage) -> GarageResponse:
    return GarageResponse(
        id=garage.id,
        name=garage.name,
        location=garage.location,
        city=garage.city,
        capacity=garage.capacity
    )


def map_request_to_garage(request: CreateGarageRequest) -> Garage:
    return Garage(
        name=request.name,
        location=request.location,
        city=request.city,
        capacity=request.capacity
    )
