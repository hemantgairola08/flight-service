# Implement FastAPI endpoints for booking and itinerary requests
# Connect to RabbitMQ for messaging

from fastapi import FastAPI
from database import initialize_database
from endpoints import router as transaction_router

print("Hemant")

app = FastAPI()

# Initialize the database
initialize_database()

# Include endpoint routers
app.include_router(transaction_router)
# app.include_router(reservations.router, prefix="/reservations", tags=["reservations"])

if __name__ == "__main__":
    import uvicorn
    print("Transaction services !!!")
    uvicorn.run(app, host="0.0.0.0", port=8000)