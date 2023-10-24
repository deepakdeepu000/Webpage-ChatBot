import re
from random import choice

def get_str_food_dict(food_dict: dict):
    result = ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])
    return result
def added_response(added_items):
    ordered_str = get_str_food_dict(added_items)
    responses = [f"Added {ordered_str} as you wished ,Anything else?",
                 f"{ordered_str} successfully added, Do you want to add any other items?",
                 f"{ordered_str} added, Are you like to add more items or wanna place order?",
                 f"successfully added {ordered_str} .These are some famous items from menu?Would you like to add anythingelse",
                 f"you successfuly added {ordered_str} to your order.anything else?"]
    return choice(responses)
def removed_str_response(items_to_remove):
    removed_str = get_str_food_dict(items_to_remove)
    responses = [f"You successfully removed the item {removed_str} , and",
                 f"{removed_str} removed successfully and ",
                 f"Removed the item('s) {removed_str}, and",
                 f"This are the items you wanted to be removed: {removed_str} \n"]
    return choice(responses)

def ordered_str_response(current_order):
    order_str = get_str_food_dict(current_order)
    responses = [f"Here is what is left in your order: {order_str},do you wanna add something else or place order",
                 f"Here is what is left in your order: {order_str},Anything else?",
                 f"Here is what is left in your order: {order_str},Anything else that i can do for you?",
                 f"Here is what is left in your order: {order_str},like to try anything else?"]
    return choice(responses)

def extract_session_id(session_str: str):
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string

    return ""
