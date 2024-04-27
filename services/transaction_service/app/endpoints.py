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
    cursor.execute("SELECT booking_id, details, booking_type, overall_status FROM booking_details WHERE booking_id=?", (payload.booking_id,))
    row = cursor.fetchone()
    print(row)
    if row is None:
        database.close_connection(conn)
        raise HTTPException(status_code=404, detail="Reservation not found")

    return {"booking_id": payload.booking_id, "details": row[1], "booking_type":row[2], "overall_status":row[3]}

@router.get("/itinerary/{user_id}")
def get_itinerary(user_id: int):
    """
    Get Itinerary against the booking id
    :return:
    """
    conn, cursor = database.get_connection()

    # Check if the reservation exists
    cursor.execute("SELECT booking_id, details, booking_type, price, overall_status FROM booking_details WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    print(row)
    if row is None:
        database.close_connection(conn)
        raise HTTPException(status_code=404, detail="Reservation not found")

    return {"booking_id": row[0], "details": row[1], "booking_type":row[2], "price":row[3], "overall_status":row[4]}
