# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update -y; \
    apt upgrade -y; \
    apt install -y sqlite3;



# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install project dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application code into the container

COPY ./database /app/database
COPY ./models /app/models
COPY ./flights.db /app/
COPY ./main.py /app/
COPY ./endpoints /app/endpoints

# Set the working directory in the container
WORKDIR /app

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
