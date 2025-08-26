import json

def load_deck_from_json(file_path):
    with open(file_path, "r") as f:
        deck = json.load(f)
    # Converte 0-100 e top_speed para números
    for card in deck:
        card["0-100"] = float(str(card["0-100"]).replace("s", "").replace(",", "."))
        card["top_speed"] = float(str(card["top_speed"]).replace(" km/h", ""))
    return deck
