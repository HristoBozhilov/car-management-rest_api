from sqlalchemy import Table, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


car_garage_association = Table(
    "car_garage_association",
    Base.metadata,
    Column("car_id", Integer, ForeignKey("cars.id"), primary_key=True),
    Column("garage_id", Integer, ForeignKey("garages.id"), primary_key=True),
)


class Car(Base):
    __tablename__ = 'cars'
    id = Column(Integer, primary_key=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    production_year = Column(Integer, nullable=False)
    licence_plate = Column(String, nullable=False)
    garages = relationship("Garage", secondary=car_garage_association, back_populates="cars")
    maintenances = relationship("Maintenance", back_populates="car")


class Garage(Base):
    __tablename__ = 'garages'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    city = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    cars = relationship("Car", secondary=car_garage_association, back_populates="garages")
    maintenances = relationship("Maintenance", back_populates="garage")


class Maintenance(Base):
    __tablename__ = 'maintenances'
    id = Column(Integer, primary_key=True)
    service_type = Column(String, nullable=False)
    scheduled_date = Column(Date, nullable=False)
    garage_id = Column(Integer, ForeignKey("garages.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)

    car = relationship("Car", back_populates="maintenances")
    garage = relationship("Garage", back_populates="maintenances")


class GarageDailyAvailabilityReport(Base):
    __tablename__ = 'garage_report'
    date = Column(String)
    requests = Column(Integer)
    available_capacity = Column(Integer)


class MonthlyRequestsReport(Base):
    __tablename__ = 'requests_report'
    year_month = Column(String)
    requests = Column(Integer)