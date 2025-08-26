from deck_loader import load_deck_from_json
from bots import WeightedBot, MCTSBot, RLBot
from utils import stats, evaluate

def play_game(bot, bot_deck, player_deck):
    bot_score, player_score = 0, 0
    round_num = 1

    while bot_deck and player_deck:
        print(f"\n--- Rodada {round_num} ---")
        bot_card, bot_stat = bot.choose_move(player_deck, stats)
        print(f"Bot escolheu: {bot_card['name']} | Estatística: {bot_stat}")

        # Jogador escolhe carta
        print("Suas cartas disponíveis:")
        for i, c in enumerate(player_deck):
            print(f"{i}: {c['name']}")
        player_index = int(input("Escolha o índice da carta: "))
        player_card = player_deck[player_index]

        # Jogador escolhe estatística
        print("Estatísticas disponíveis:", stats)
        player_stat = input("Escolha a estatística: ")

        # Resultado
        result = evaluate(bot_card, player_card, bot_stat)
        if result == 1:
            print(f"Bot vence a rodada! {bot_card['name']} > {player_card['name']}")
            bot_score += 1
        elif result == -1:
            print(f"Você vence a rodada! {player_card['name']} > {bot_card['name']}")
            player_score += 1
        else:
            print(f"Empate! {bot_card['name']} = {player_card['name']}")

        bot_deck.remove(bot_card)
        player_deck.remove(player_card)
        round_num += 1

    print("\n=== Placar Final ===")
    print(f"Bot: {bot_score} | Você: {player_score}")
    if bot_score > player_score:
        print("Bot venceu o jogo!")
    elif player_score > bot_score:
        print("Você venceu o jogo!")
    else:
        print("Empate!")

if __name__ == "__main__":
    file_path = input("Informe o caminho do JSON do deck: ")
    deck = load_deck_from_json(file_path)
    half = len(deck)//2
    bot_deck = deck[:half]
    player_deck = deck[half:]

    print("Escolha a dificuldade do bot:")
    print("1 - Fácil")
    print("2 - Médio")
    print("3 - Difícil")
    choice = input("Digite o número: ")

    if choice == "1":
        bot = WeightedBot(bot_deck)
    elif choice == "2":
        bot = MCTSBot(bot_deck)
    else:
        bot = RLBot(bot_deck)

    play_game(bot, bot_deck, player_deck)
