import json

def save_to_json(data, filename="product.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)