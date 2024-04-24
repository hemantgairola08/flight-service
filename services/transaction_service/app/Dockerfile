# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update -y; \
    apt upgrade -y; \
    apt-get update -y; \
    apt-get upgrade -y; \
    apt install -y vim; \
    apt install -y sqlite3;



# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install project dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install supervisor and its dependencies
RUN apt install supervisor -y
RUN apt-get install procps -y

# Copy the rest of the application code into the container


COPY ./* /app/
COPY ./start.sh /

# Set the working directory in the container
WORKDIR /app

# Start consumer
# Command to run the FastAPI application
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

RUN ["chmod", "+x", "/app/start.sh"]
CMD ["/app/start.sh"]


