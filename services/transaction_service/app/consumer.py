import time

import pika
import json

import database

hostname = "rabbitmq"

username = "guest"
password = "guest"

queue_name = "bookings"


def update_database(data):
    # # Connect to the database


    # Connect to the database
    conn, cursor = database.get_connection()
    table_name = "booking_details"

    # Extract update information from the message data
    print(f"Received payload from producer : {data}")
    if data["request_type"] == "CANCEL":
        booking_id = data["booking_id"]
        upate_stmt = f"UPDATE {table_name} set overall_status = 'CANCELLED', remarks = 'User initiated cancellation' where booking_id = '{booking_id}'"
        cursor.execute(upate_stmt)
        rows_updated = cursor.rowcount
        if rows_updated > 0:
            print(f"{rows_updated} rows updated successfully.")
        else:
            print("No rows updated.")
    else:

        values = [
            data['booking_details']['booking_id'],
            str(data['booking_details']),
            "FLIGHT",
            data['user_id'],
            data['overall_status'],
            data['price'],
            data["remarks"],
        ]
        print("Check if record exists or not")
        booking_id = data['booking_details']['booking_id']
        print(f"Booking id : {booking_id}")

        # cursor.execute(f"SELECT booking_id FROM {table_name} WHERE booking_id=?", (f'{booking_id}'))
        cursor.execute(f"SELECT booking_id FROM {table_name} WHERE booking_id='{booking_id}'")
        row = cursor.fetchone()
        if row is not None:
            print(f"Data for booking id exist : {row}")
              # Assuming a list of values in the same order as columns

            upate_stmt = f"UPDATE {table_name} set details = ?, booking_type = ?, user_id = ?, overall_status = ?, price = ?, remarks = ? where booking_id = ?"
            values = [
                str(data['booking_details']),
                "FLIGHT",
                data['user_id'],
                data['overall_status'],
                data['price'],
                data["remarks"],
                data['booking_details']['booking_id'],
            ]
            cursor.execute(upate_stmt, values)
            rows_updated = cursor.rowcount
            if rows_updated > 0:
                print(f"{rows_updated} rows updated successfully.")
            else:
                print("No rows updated.")
        else:
            # Construct the INSERT statement
            insert_stmt = f"INSERT INTO {table_name} ('booking_id','details', 'booking_type', 'user_id', 'overall_status', 'price', 'remarks') values (?,?,?,?,?,?,?)"

            # Execute the update query
            cursor.execute(insert_stmt, values)

            # Check rowcount for successful updates
            rows_updated = cursor.rowcount
            if rows_updated > 0:
                print(f"{rows_updated} row inserted successfully.")
            else:
                print("No row inserted.")
    conn.commit()

    cursor.close()
    conn.close()



def on_message_received(channel, method, properties, body):
    # Convert JSON message to dictionary
    print(f"data recievied : {body}")
    data = json.loads(body.decode())
    print(f"data recievied : {data}")
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