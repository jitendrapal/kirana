from datetime import datetime
from firebase_config import db
import re

# -----------------------------
# AI Logic for StockBuddy
# -----------------------------
def parse_command(command_text):
    """
    Parses the user's command to extract action, item, quantity, and unit.
    """
    command_text = command_text.lower().strip()
    
    # Define patterns for different commands
    patterns = {
        "add": r"(add|add kar)\s+(?P<qty>\d+)\s*(?P<unit>\w+)?\s+of\s+(?P<item>[\w\s]+)",
        "sell": r"(sell|bech)\s+(?P<qty>\d+)\s*(?P<unit>\w+)?\s+of\s+(?P<item>[\w\s]+)",
        "show_stock": r"stock of\s+(?P<item>[\w\s]+)",
        "daily_report": r"daily report|aaj ka report",
    }

    for action, pattern in patterns.items():
        match = re.search(pattern, command_text)
        if match:
            command = {"action": action}
            command.update(match.groupdict())
            # Clean up the item name
            if 'item' in command:
                command['item'] = command['item'].strip()
            return command

    # Fallback for simple commands
    if "stock" in command_text:
        return {"action": "show_stock"}
    elif "report" in command_text:
        return {"action": "daily_report"}

    return {"action": "unknown"}


def execute_command(parsed):
    """
    Executes the parsed command and returns a response.
    """
    action = parsed.get("action")
    item = parsed.get("item")
    qty = parsed.get("qty")
    unit = parsed.get("unit")

    if qty:
        try:
            qty = int(qty)
        except (ValueError, TypeError):
            return "Invalid quantity. Please provide a number."

    if action == "add" and item and qty:
        item_ref = db.collection('items').document(item)
        doc = item_ref.get()
        if doc.exists:
            current_stock = doc.to_dict().get("stock", 0)
            new_stock = current_stock + qty
            item_ref.update({"stock": new_stock})
            item_unit = doc.to_dict().get('unit', 'units')
            return f"Added {qty} {unit or item_unit} of {item.capitalize()}. New stock: {new_stock} {item_unit}."
        else:
            # If item doesn't exist, create it
            item_ref.set({"stock": qty, "unit": unit or "units", "reorder_level": 10})
            return f"Added {item.capitalize()} to the inventory with {qty} {unit or 'units'}."

    elif action == "sell" and item and qty:
        item_ref = db.collection('items').document(item)
        doc = item_ref.get()
        if doc.exists:
            current_stock = doc.to_dict().get("stock", 0)
            if current_stock < qty:
                return f"Not enough stock of {item.capitalize()} to sell. Only {current_stock} left."
            
            new_stock = current_stock - qty
            item_ref.update({"stock": new_stock})
            db.collection('sales').add({"item": item, "qty": qty, "date": datetime.now().strftime("%Y-%m-%d")})
            
            item_unit = doc.to_dict().get('unit', 'units')
            response = f"Sold {qty} {unit or item_unit} of {item.capitalize()}. New stock: {new_stock} {item_unit}."
            
            reorder_level = doc.to_dict().get("reorder_level", 0)
            if new_stock < reorder_level:
                response += f"\nALERT: Stock for {item.capitalize()} is low. Please reorder."
            return response
        else:
            return f"{item.capitalize()} is not in your inventory."

    elif action == "show_stock":
        if item:
            item_ref = db.collection('items').document(item)
            doc = item_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return f"Stock of {item.capitalize()}: {data.get('stock', 0)} {data.get('unit', 'units')}."
            else:
                return f"{item.capitalize()} is not in your inventory."
        else:
            items_ref = db.collection('items').stream()
            response = "Current stock:\n"
            for doc in items_ref:
                data = doc.to_dict()
                response += f"- {doc.id.capitalize()}: {data.get('stock', 0)} {data.get('unit', 'units')}\n"
            return response if response != "Current stock:\n" else "No items in inventory."

    elif action == "daily_report":
        sales_ref = db.collection('sales').where("date", "==", datetime.now().strftime("%Y-%m-%d")).stream()
        total_units_sold = 0
        sales_by_item = {}
        for sale in sales_ref:
            data = sale.to_dict()
            total_units_sold += data.get('qty', 0)
            sales_by_item[data['item']] = sales_by_item.get(data['item'], 0) + data.get('qty', 0)
        
        top_item = max(sales_by_item, key=sales_by_item.get) if sales_by_item else "None"

        items_ref = db.collection('items').stream()
        low_stock_items = [
            doc.id.capitalize() for doc in items_ref 
            if doc.to_dict().get("stock", 0) < doc.to_dict().get("reorder_level", 0)
        ]

        response = f"Daily Sales Report ({datetime.now().strftime('%Y-%m-%d')}):\n"
        response += f"Total Units Sold: {total_units_sold}\n"
        response += f"Top-Selling Item: {top_item.capitalize() if top_item != 'None' else 'None'}\n"
        if low_stock_items:
            response += "Low Stock Items: " + ", ".join(low_stock_items)
        else:
            response += "No items are currently low on stock."
        return response

    else:
        return "Sorry, I didn't understand that command. Please try again. You can say things like:\n" \
               "- Add 10 kg of Sugar\n" \
               "- Sell 2 boxes of Apples\n" \
               "- Stock of Mangoes\n" \
               "- Daily report"
