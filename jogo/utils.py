stats = ["HP", "torque", "weight", "0-100", "top_speed"]

def evaluate(bot_card, player_card, stat):
    bot_value = bot_card[stat]
    player_value = player_card[stat]
    if stat in ["weight", "0-100"]:
        bot_value = 1 / bot_value
        player_value = 1 / player_value
    if bot_value > player_value:
        return 1
    elif bot_value < player_value:
        return -1
    else:
        return 0

def expected_score(deck):
    if not deck:
        return 0
    score = 0
    for card in deck:
        for stat in stats:
            value = card[stat]
            if stat in ["weight", "0-100"]:
                value = 1 / value
            score += value
    return score / len(deck)
