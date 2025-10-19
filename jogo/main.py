import os
from deck_loader import load_deck_from_json
from bots import WeightedBot, MCTSBot, RLBot
from utils import stats, evaluate

def play_game(bot, bot_deck, player_deck):
    bot_score, player_score = 0, 0
    round_num = 1

    # cria um mapa de estatísticas em lowercase -> original
    valid_stats = {s.lower(): s for s in stats}

    while bot_deck and player_deck:
        print(f"\n--- Rodada {round_num} ---")

        # Jogador escolhe o atributo da rodada
        print("Estatísticas disponíveis:", stats)
        chosen_input = input("Escolha a estatística para esta rodada: ").strip().lower()

        # valida a escolha do player
        if chosen_input not in valid_stats:
            print("Estatística inválida, tente novamente.")
            continue

        # converte para o formato correto do deck (ex: "hp" -> "HP")
        chosen_stat = valid_stats[chosen_input]

        # Bot escolhe carta com base nesse atributo
        bot_card = bot.choose_card(player_deck, chosen_stat)
        print(f"Bot escolheu a carta: {bot_card['name']}")

        # Jogador escolhe carta
        print("Suas cartas disponíveis:")
        for i, c in enumerate(player_deck):
            print(f"{i}: {c['name']} | {chosen_stat}: {c[chosen_stat]}")

        try:
            player_index = int(input("Escolha o índice da carta: "))
            player_card = player_deck[player_index]
        except (ValueError, IndexError):
            print("Índice inválido, tente novamente.")
            continue

        # Comparar valores
        result = evaluate(bot_card, player_card, chosen_stat)
        if result == 1:
            print(f"Bot vence a rodada! {bot_card['name']} ({bot_card[chosen_stat]}) > {player_card['name']} ({player_card[chosen_stat]})")
            bot_score += 1
        elif result == -1:
            print(f"Você vence a rodada! {player_card['name']} ({player_card[chosen_stat]}) > {bot_card['name']} ({bot_card[chosen_stat]})")
            player_score += 1
        else:
            print(f"Empate! {bot_card['name']} ({bot_card[chosen_stat]}) = {player_card['name']} ({player_card[chosen_stat]})")

        bot_deck.remove(bot_card)
        player_deck.remove(player_card)
        round_num += 1

    # Resultado final
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
    elif choice == "3":
        # Carrega o RLBot treinado
        # O caminho para a Q-table deve ser ajustado se o arquivo for movido
        Q_FILE_PATH = "./rl_q_table.json"
        bot = RLBot(bot_deck, qfile=Q_FILE_PATH, epsilon=0.0) # epsilon=0.0 para explotação
    else:
        print("Escolha inválida. Usando Bot Padrão (WeightedBot).")
        bot = WeightedBot(bot_deck)

    play_game(bot, bot_deck, player_deck)