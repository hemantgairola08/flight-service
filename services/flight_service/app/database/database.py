import sqlite3

# Function to create a SQLite connection and cursor
def get_connection():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    return conn, cursor

# Function to close SQLite connection
def close_connection(conn):
    conn.close()

# Function to initialize the database (create tables if they don't exist)
def initialize_database():
    conn, cursor = get_connection()

    # Create flights table
    cursor.execute('''CREATE TABLE IF NOT EXISTS flights
                      (id INTEGER PRIMARY KEY,
                      origin TEXT,
                      destination TEXT,
                      departure_time TEXT,
                      capacity INTEGER,
                      available_seats INTEGER)''')

    # Create reservations table
    cursor.execute('''CREATE TABLE IF NOT EXISTS reservations
                      (booking_id INTEGER PRIMARY KEY,
                      flight_id INTEGER,
                      user_id INTEGER,
                      FOREIGN KEY (flight_id) REFERENCES flights(id))''')

    conn.commit()
    close_connection(conn)