from typing import List

from database import database
from fastapi import FastAPI, HTTPException, APIRouter
from models.models import Flight

app = FastAPI()

router = APIRouter(prefix="/flights", tags=["flights"])
# Endpoint to search for flights based on origin and destination
@router.get("/search", response_model=List[Flight])
def search_flights(payload: dict):
    conn, cursor = database.get_connection()
    origin = payload.get('origin')
    destination = payload.get('destination')
    departure_time =  payload.get('departure_time')

    if not origin or not destination or not departure_time:
        raise HTTPException(status_code=400, detail="'origin', 'destination' and 'departure_time' must be provided in the payload")

    # Filter flights based on origin and destination
    cursor.execute("SELECT * FROM flights WHERE origin=? AND destination=? AND departure_time=?",
                   (origin, destination, departure_time))
    rows = cursor.fetchall()
    database.close_connection(conn)
    print(rows)
    filtered_flights = [Flight(id=row[0], origin=row[1], destination=row[2], departure_time=row[3], capacity=row[4], available_seats=row[5]) for row
            in rows]

    if not filtered_flights:
        raise HTTPException(status_code=404, detail="No flights found")

    return filtered_flights

# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)
