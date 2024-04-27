import sqlite3

# Function to create a SQLite connection and cursor
def get_connection():
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    return conn, cursor

# Function to close SQLite connection
def close_connection(conn):
    conn.close()

# Function to initialize the database (create tables if they don't exist)
def initialize_database():
    conn, cursor = get_connection()
    # Create booking_details table
    cursor.execute('''CREATE TABLE IF NOT EXISTS booking_details
                      (booking_id TEXT PRIMARY KEY,
                      details TEXT,
                      booking_type TEXT NOT NULL CHECK(booking_type IN ('FLIGHT', 'HOTEL')),
                      user_id INTEGER,
                      overall_status TEXT NOT NULL CHECK(overall_status IN ('CREATED', 'FAILED', 'BOOKED', 'CANCELLED')),
                      price DOUBLE,
                      remarks TEXT)''')

    conn.commit()
    close_connection(conn)