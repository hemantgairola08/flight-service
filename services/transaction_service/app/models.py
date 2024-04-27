from typing import Optional

from pydantic import BaseModel

class BookingRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    booking_id: str

class ItineraryRequest(BaseModel):
    booking_id: str

class ItineraryRequestByUserId(BaseModel):
    user_id: str

