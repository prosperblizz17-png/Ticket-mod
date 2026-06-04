import os
import json

CONFIG_PATH = "data/config.json"
TICKETS_PATH = "data/tickets.json"

def initialize_files(utils):
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump({}, f, indent=4)
    if not os.path.exists(TICKETS_PATH):
        with open(TICKETS_PATH, "w") as f:
            json.dump({"total_tickets": 0, "claimed_tickets": 0, "staff_stats": {}, "active_tickets": {}}, f, indent=4)

def load_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
