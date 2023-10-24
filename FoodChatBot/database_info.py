

import mysql.connector

global cnx

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345@deepak",
    database="deepak"
)

# Function to call the MySQL stored procedure and insert an order item
def insert_order_item(food_item, quantity, order_id):
    try:
        cursor = cnx.cursor()

        # Calling the stored procedure
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))

        # Committing the changes
        cnx.commit()

        # Closing the cursor
        cursor.close()

        print("Order item inserted successfully!")

        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")

        # Rollback changes if necessary
        cnx.rollback()

        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        # Rollback changes if necessary
        cnx.rollback()

        return -1

# Function to insert a record into the order_tracking table
def insert_order_tracking(order_id, status,session_id: str):
    cursor = cnx.cursor()

    # Inserting the record into the order_tracking table
    insert_query = "INSERT INTO order_tracking (order_id, status,session_id) VALUES (%s, %s,%s)"
    cursor.execute(insert_query, (order_id, status,session_id))

    # Committing the changes
    cnx.commit()

    # Closing the cursor
    cursor.close()

def get_order_id(session_id: str):
    cursor = cnx.cursor()

    # Executing the SQL query to get the total order price
    query = f"SELECT order_id FROM order_tracking WHERE session_id = %s"
    cursor.execute(query,(session_id,))

    # Fetching the result
    result = cursor.fetchone()

    # Closing the cursor
    cursor.close()

    return result
def get_total_order_price(order_id):
    cursor = cnx.cursor()

    # Executing the SQL query to get the total order price
    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    return result

# Function to get the next available order_id
def get_next_order_id():
    cursor = cnx.cursor()

    # Executing the SQL query to get the next available order_id
    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    # Returning the next available order_id
    if result is None:
        return 1
    else:
        return result + 1

# Function to fetch the order status from the order_tracking table
def get_order_status(order_id,session_id: str):
    cursor = cnx.cursor()

    # Executing the SQL query to fetch the order status
    query = f"SELECT status FROM order_tracking WHERE order_id = %s and session_id = %s"
    cursor.execute(query,(order_id,session_id))

    # Fetching the result
    result = cursor.fetchone()

    # Closing the cursor
    cursor.close()

    # Returning the order status
    if result:
        return result[0]
    else:
        return None
def order_exists(order_id):
    cursor = cnx.cursor()

    print(order_id)
    # Assuming you have a database connection established and a cursor created
    cursor.execute("SELECT COUNT(*) FROM order_tracking WHERE order_id = %s", (order_id,))
    result = cursor.fetchone()
    cursor.close()
    # Check if the result is greater than zero, indicating that the order exists
    return result[0] > 0

def change_order_status(order_id,status,session_id: str):

    cursor = cnx.cursor()

    # Update the status of the order
    update_query = f"UPDATE order_tracking SET status = %s WHERE order_id = %s and session_id = %s"
    cursor.execute(update_query, (status, order_id,session_id))

    # Commit the changes to the database
    cnx.commit()

    cursor.close()


#def is_present(session_id: str):
#    cursor = cnx.cursor()
#
#    # Update the status of the order
#    update_query = f"SELECT COUNT(*) FROM order_tracking WHERE session_id = %s"
#    cursor.execute(update_query, (session_id,))
#
#    result = cursor.fetchone()
#
#    cursor.close()
#
#    return result[0] > 0


if __name__ == "__main__":
    # print(get_total_order_price(56))
    # insert_order_item('Samosa', 3, 99)
    # insert_order_item('Pav Bhaji', 1, 99)
    # insert_order_tracking(99, "in progress")
    print(get_next_order_id())
