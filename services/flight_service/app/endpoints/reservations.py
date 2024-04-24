import json
import random
import string
import time

import pika
from database import database
from fastapi import FastAPI, HTTPException, APIRouter
from models.models import ReservationModificationRequest
from models.models import ReservationRequest
from models.models import ReservationCancelRequest
from models.models import Reservation
from models.models import ReservationStatusRequest
from models.models import Flight

app = FastAPI()

router = APIRouter(prefix="/flights/booking", tags=["flights"])


hostname = "rabbitmq"

# Credentials (if any, remove username and password lines if not needed)
username = "guest"
password = "guest"

connection_parameters = pika.ConnectionParameters(host=hostname,credentials=pika.PlainCredentials(username, password), retry_delay=5)

def connect_rabbitmq():
  try:
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()
    # Use the channel and connection for communication
    return connection, channel
  except pika.exceptions.AMQPConnectionError:
    print("Connection failed, retrying...")
    time.sleep(5)  # Adjust retry delay as needed
    return connect_rabbitmq()  # Retry connection

connection, channel = connect_rabbitmq()
channel.queue_declare(queue='flight_status_booking_queue')



def send_message_to_queue(message):
    # Send message to RabbitMQ for flight or hotel booking
    channel.basic_publish(exchange='', routing_key='flight_status_booking_queue', body=json.dumps(message))

# Endpoint to reserve a flight
@router.post("/")
def reserve_flight(payload: ReservationRequest):
    print(f"Payload for flight reservation: {payload.json()}")
    conn, cursor = database.get_connection()

    origin = payload.origin
    destination = payload.destination
    departure_time = payload.departure_date
    booking_id = "".join(random.choices(string.ascii_letters.upper(), k=5) + random.choices(string.digits, k=5))

    # Create default response
    booking_details = {
        "booking_id": booking_id,
        "origin": payload.origin,
        "destination": payload.destination,
        "departure_date": payload.departure_date
    }

    overall_booking_details = {
        "booking_details": booking_details,
        "overall_status": "BOOKED",
        "remarks": "",
        "price": 0
    }


    if not origin or not destination or not departure_time:
        detail = "'origin', 'destination' and 'departure_time' must be provided in the payload"
        overall_booking_details["overall_status"] = "FAILED"
        overall_booking_details["remarks"] = detail
        update_transaction_service(booking_details, overall_booking_details)
        raise HTTPException(status_code=400,
                            detail="'origin', 'destination' and 'departure_time' must be provided in the payload")

    # Filter flights based on origin and destination
    cursor.execute("SELECT * FROM flights WHERE origin=? AND destination=? AND departure_time=?",
                   (origin, destination, departure_time))
    rows = cursor.fetchall()

    print(f"Rows details : {rows}")
    filtered_flights = [Flight(id=row[0], origin=row[1], destination=row[2], departure_time=row[3], capacity=row[4],
                               available_seats=row[5], price=row[6]) for row
                        in rows]
    print(filtered_flights)

    if len(rows) == 0:
        database.close_connection(conn)
        detail = "Flight not found for given details"
        overall_booking_details["overall_status"] = "FAILED"
        overall_booking_details["remarks"] = detail
        update_transaction_service(booking_details, overall_booking_details)
        raise HTTPException(status_code=404, detail="Flight not found")

    # booking_id = payload.booking_id
    flight_id = filtered_flights[0].id


    cursor.execute("SELECT available_seats FROM flights WHERE id=?", (flight_id,))
    row = cursor.fetchone()
    print(row)
    if row is None:
        database.close_connection(conn)
        detail = "Seats not available"
        overall_booking_details["overall_status"] = "FAILED"
        overall_booking_details["remarks"] = detail
        update_transaction_service(booking_details, overall_booking_details)
        raise HTTPException(status_code=404, detail="Seats not available")

    # Check if there are available seats
    available_seats = row[0]
    print(available_seats)
    if available_seats <= 0:
        database.close_connection(conn)
        detail="No available seats for this flight"
        overall_booking_details["overall_status"] = "FAILED"
        overall_booking_details["remarks"] = detail
        update_transaction_service(booking_details, overall_booking_details)
        raise HTTPException(status_code=400, detail="No available seats for this flight")

    price = filtered_flights[0].price
    overall_booking_details["price"] = price
    user_id = payload.user_id
    overall_booking_details["user_id"] = user_id

    # Insert reservation into the database
    cursor.execute("INSERT INTO reservations (booking_id, flight_id, user_id) VALUES (?, ?, ?)",
                   (booking_id, flight_id, user_id))
    conn.commit()

    reservation_id = cursor.lastrowid
    print(reservation_id)

    cursor.execute("UPDATE flights SET available_seats = ? WHERE id = ?",
                   (available_seats - 1, flight_id))

    conn.commit()
    database.close_connection(conn)

    print(f"Flight has been booking against booking id : {booking_details}")
    print(f"Sending message to transaction service : {booking_details}")

    send_message_to_queue(overall_booking_details)
    print(f"Sent message: {overall_booking_details}")

    return overall_booking_details


def update_transaction_service(booking_details, overall_booking_details):
    print(f"Flight Booking has been failed against booking id : {booking_details}")
    print(f"Sending message to transaction service : {booking_details}")
    send_message_to_queue(overall_booking_details)


# Endpoint to modify an existing flight reservation
@router.put("/modify", response_model=Reservation)
def modify_reservation(payload: ReservationModificationRequest):
    conn, cursor = database.get_connection()

    # Check if the reservation exists
    cursor.execute("SELECT * FROM reservations WHERE id=?", (payload.reservation_id,))
    row = cursor.fetchone()
    print(row)
    if row is None:
        database.close_connection(conn)
        raise HTTPException(status_code=404, detail="Reservation not found")

    old_flight_id = row[1]
    user_id = row[2]

    # Update reservation details
    cursor.execute("UPDATE reservations SET flight_id=? WHERE id=?",
                   (payload.booking_id,
                    payload.new_flight_id,
                    payload.reservation_id))

    # Check if the flight has changed
    if old_flight_id != payload.new_flight_id:
        # Increase available seats for old flight
        cursor.execute("UPDATE flights SET available_seats = available_seats + 1 WHERE id = ?", (old_flight_id,))
        # Decrease available seats for new flight
        cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE id = ?",
                       (payload.new_flight_id,))

    conn.commit()
    database.close_connection(conn)
    return {"id": payload.reservation_id, "booking_id": payload.booking_id, "flight_id": payload.new_flight_id, "user_id": user_id}


# Endpoint to cancel an existing flight reservation
@router.delete("/cancel")
def cancel_reservation(payload: ReservationCancelRequest):
    conn, cursor = database.get_connection()

    # Check if the reservation exists
    cursor.execute("SELECT flight_id FROM reservations WHERE id=?", (payload.reservation_id,))
    row = cursor.fetchone()
    print(row)
    if row is None:
        database.close_connection(conn)
        raise HTTPException(status_code=404, detail="Reservation not found")

    flight_id = row[0]

    # Delete the reservation from the database
    cursor.execute("DELETE FROM reservations WHERE id=?", (payload.reservation_id,))

    # Increase available seats for the canceled flight
    cursor.execute("UPDATE flights SET available_seats = available_seats + 1 WHERE id = ?", (flight_id,))

    conn.commit()
    database.close_connection(conn)

    return {"message": "Reservation canceled successfully"}

# Endpoint to status an existing flight reservation
@router.get("/status")
def reservation_status(payload: ReservationStatusRequest):
    conn, cursor = database.get_connection()

    # Check if the reservation exists
    cursor.execute("SELECT flight_id, booking_id FROM reservations WHERE booking_id=?", (payload.booking_id,))
    row = cursor.fetchone()
    print(row)
    if row is None:
        database.close_connection(conn)
        raise HTTPException(status_code=404, detail="Reservation not found")

    flight_id = row[0]
    booking_id = row[1]
    print(f"Flight id: {flight_id} and Booking_id : {booking_id}")

    cursor.execute(f"SELECT * FROM flights WHERE id={flight_id}")
    rows = cursor.fetchall()
    print(rows)

    database.close_connection(conn)
    origin = rows[0][1]
    destination = rows[0][2]
    departure_date = rows[0][3]

    return {"booking_id": booking_id, "origin": origin, "destination":destination,"departure_date":departure_date}