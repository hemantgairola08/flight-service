from typing import Optional

from pydantic import BaseModel

class ReservationRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    user_id: int

class ReservationModificationRequest(BaseModel):
    booking_id: int
    reservation_id: int
    new_flight_id: int

class ReservationCancelRequest(BaseModel):
    reservation_id: int

class ReservationStatusRequest(BaseModel):
    booking_id: str

class Reservation(BaseModel):
    id: int
    booking_id: int
    flight_id: int
    user_id: int

class Flight(BaseModel):
    id: int
    origin: str
    destination: str
    departure_time: str
    capacity: int
    available_seats: int
    price: float