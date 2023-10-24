from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import HelperCode
import database_info

app = FastAPI()

inprogress_orders = {}

Updated_orders = {}



@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    intent_handler_dict = {
        'Order.add - context: Ongoing-order': add_to_order,
        'Order.remove - Context: Ongoing-order': remove_from_order,
        'order.complete - context: ongoing-order': complete_order,
        'Track.Order - Context : Ongoing-Tracking': track_order,
        'Order.Cancel - context: Order-cancel-Confirmation': cancel_the_order,
        'List.order - Context : Ongoing-order': list_out_items,
        'Order.delivery - context: Order-delivered': delivered
    }
    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = HelperCode.extract_session_id(output_contexts[1]["name"])

    return intent_handler_dict[intent](parameters, session_id)

def list_out_items(parameters: dict, session_id: str):

    if session_id in Updated_orders:
        current_list_items = Updated_orders[session_id]
        list_i = ""
        i = 0
        for key,val in current_list_items.items():
            i += 1
            list_i += f"{i}. {key} : {val}" + "\n"
        fulfillment_text = f"ya sure here is the updated list of items you ordered Until now.{list_i} Would you like to add anything else to list."
    elif session_id in inprogress_orders.keys():
        current_list_items = inprogress_orders[session_id]
        list_i = ""
        i = 0
        for key, val in current_list_items.items():
            i += 1
            list_i += f"{i}. {key} : {val}" + "\n"
        fulfillment_text = f"ya sure here is the updated list of items you ordered Until now.{list_i} Would you like to add anything else to list."
    else:
        fulfillment_text = "Sorry! you didn't ordered anything. Can you place a new order please? or try adding items to your order." + "\n try 'New order' "

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def delivered(parameters: dict,session_id: str):
    print(Updated_orders)
    if session_id in Updated_orders:
        del Updated_orders[session_id]
    print(Updated_orders)
    order_id = database_info.get_order_id(session_id)
    print(order_id)
    if database_info.order_exists(order_id):
        print("Yes")
        database_info.change_order_status(order_id, status = "delivered", session_id = session_id)
        fulfillment_text = f"Your Order with order_ID: #{order_id}, has been successfully delivered.\nEnjoy your Meal 😊😊😊"
    else:
        fulfillment_text = "No order found with the provided order ID."

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def save_to_db(order: dict,session_id: str):
    next_order_id = database_info.get_next_order_id()

    # Insert individual items along with quantity in orders table
    for food_item, quantity in order.items():
        rcode = database_info.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )

        if rcode == -1:
            return -1
    # Now insert order tracking status
    database_info.insert_order_tracking(next_order_id, "in progress", session_id)

    return next_order_id


def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order,session_id)
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                               "Please place a new order again"
        else:
            order_total = database_info.get_total_order_price(order_id)

            fulfillment_text = f"Awesome. We have placed your order. " \
                               f"Here is your order id # {order_id}. " \
                               f"Your order total is {order_total} which you can pay at the time of delivery!"
        Updated_orders[session_id] = inprogress_orders[session_id]
        del inprogress_orders[session_id]

        print(inprogress_orders)
        print(Updated_orders)

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def add_to_order(parameters: dict, session_id: str):
    response_text = ""
    food_items = parameters["food-Item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        new_food_dict = dict(zip(food_items, quantities))

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            for key, val in new_food_dict.items():
                if key in current_food_dict:
                    current_food_dict[key] += val
                else:
                    current_food_dict[key] = val
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        #order_str = HelperCode.get_str_food_dict(inprogress_orders[session_id]) So far you have: {order_str}.
        response_text = "ordered items updated!!!"+ HelperCode.added_response(new_food_dict)
        fulfillment_text = response_text
    print(inprogress_orders)
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def remove_from_order(parameters: dict, session_id: str):
    fulfillment_text = ""
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having a trouble finding your order.Sorry! Can you place Your order again."
        })

    food_items = parameters["food-Item"]
    numbers = list(parameters["number"])

    items_to_remove = dict(zip(food_items, numbers))
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item, val in zip(food_items, numbers):
        if item not in current_order:
            no_such_items.append(item)
        elif item in current_order:
            removed_items.append(item)
            if current_order[item] >= 0:
                current_order[item] -= val
            if current_order[item] <= 0:
                del current_order[item]

    if len(removed_items) > 0:
        random_response = HelperCode.removed_str_response(items_to_remove)
        fulfillment_text = random_response

    if len(no_such_items) > 0:
        fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        random_response = HelperCode.ordered_str_response(current_order)
        fulfillment_text += random_response

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def track_order(parameters: dict, session_id: str):
    order_id = int(parameters['number'])
    order_status = database_info.get_order_status(order_id, session_id)
    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def cancel_the_order(parameters: dict, session_id: str):

    order_id = parameters.get("orderID")  # Assuming you get the order ID from parameters
    print(order_id)
    # Check if the order exists in the database and update its status to "canceled"
    if database_info.order_exists(order_id):
        database_info.change_order_status(order_id, status = "canceled", session_id = session_id)
        fulfillment_text = f"Order {order_id} has been successfully canceled."
    else:
        fulfillment_text = "No order found with the provided order ID."

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })



