import pika

# Replace with your RabbitMQ container's hostname or IP address
hostname = "localhost"

# Credentials (if any, remove username and password lines if not needed)
username = "guest"
password = "guest"

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=hostname, credentials=pika.PlainCredentials(username, password))
)

channel = connection.channel()

# Replace with the queue name you want to interact with
queue_name = "bookings"

channel.queue_declare(queue=queue_name)

# Example message to send (replace with your actual message)
message = "Hello, RabbitMQ!"

channel.basic_publish(exchange="", routing_key=queue_name, body=message.encode())

print(f"Sent message: {message}")

connection.close()
