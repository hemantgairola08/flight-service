from fastapi import FastAPI
from database.database import initialize_database
from endpoints.flights import router as flight_router
from endpoints.reservations import router as reservation_router

print("Hemant")

app = FastAPI()

# Initialize the database
initialize_database()

# Include endpoint routers
app.include_router(flight_router)
app.include_router(reservation_router)
# app.include_router(reservations.router, prefix="/reservations", tags=["reservations"])

if __name__ == "__main__":
    import uvicorn
    print("Hemant !!!")
    uvicorn.run(app, host="0.0.0.0", port=8000)