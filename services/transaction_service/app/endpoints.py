# transaction_service.py

from fastapi import FastAPI, HTTPException, APIRouter
from models import ItineraryRequest
import database


app = FastAPI()

router = APIRouter(prefix="/travel", tags=["transaction"])




@router.get("/itinerary")
def get_itinerary(payload: ItineraryRequest):
    """
    Get Itinerary against the booking id
    :return:
    """
    conn, cursor = database.get_connection()

    # Check if the reservation exists
    cursor.execute("SELECT booking_id, details, booking_type FROM booking_details WHERE booking_id=?", (payload.booking_id,))
    row = cursor.fetchone()
    print(row)
    if row is None:
        database.close_connection(conn)
        raise HTTPException(status_code=404, detail="Reservation not found")

    return {"booking_id": payload.booking_id, "flight_details": row[1], "booking_type":row[2]}
