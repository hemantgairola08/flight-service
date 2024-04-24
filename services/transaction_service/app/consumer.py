import time

import pika
import json

import database

hostname = "rabbitmq"
username = "guest"
password = "guest"

queue_name = "flight_status_booking_queue"


def update_database(data):
    # Connect to the database
    conn, cursor = database.get_connection()

    # Extract update information from the message data

    table_name = "booking_details"
    columns = ["flight_details", "overall_status","user_id", "price", "remarks"]  # Assuming a list of column names
    values = [
        data['booking_details']['booking_id'],
        str(data['booking_details']),
        "FLIGHT",
        data['user_id'],
        data['overall_status'],
        data['price'],
        data["remarks"],
    ]  # Assuming a list of values in the same order as columns

    # Construct the INSERT statement
    insert_stmt = f"INSERT INTO {table_name} ('booking_id','details', 'booking_type', 'user_id', 'overall_status', 'price', 'remarks') values (?,?,?,?,?,?,?)"

    # Execute the update query
    cursor.execute(insert_stmt, values)

    # Check rowcount for successful updates
    rows_updated = cursor.rowcount
    if rows_updated > 0:
        print(f"{rows_updated} rows updated successfully.")
    else:
        print("No rows updated.")

    conn.commit()

    cursor.close()
    conn.close()


def on_message_received(channel, method, properties, body):
    # Convert JSON message to dictionary
    data = json.loads(body.decode())
    update_database(data)

    # Acknowledge the message (optional, uncomment if needed)
    # channel.basic_ack(delivery_tag=method.delivery_tag)

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

connection_parameters = pika.ConnectionParameters(host=hostname,
                                                      credentials=pika.PlainCredentials(username, password),
                                                      retry_delay=5)

def main():
    # Connect to RabbitMQ

    connection, channel = connect_rabbitmq()

    channel = connection.channel()

    # Declare the queue (optional, can be done from producer service)
    channel.queue_declare(queue=queue_name)

    # Consume messages from the queue
    channel.basic_consume(queue=queue_name, on_message_callback=on_message_received)

    print("Waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    main()