#!/usr/bin/env python3
"""
Script de treinamento self-play para o RLBot (DQN).
O bot treina jogando contra uma cópia de si mesmo (target network).
"""

import sys
import os
import json
import random
import copy
import argparse
import torch

# Adiciona o backend ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils import STATS, evaluate
from bots.rl_bot import RLBot, QNetwork

# --- Configurações de Treinamento ---
INITIAL_EPSILON = 1.0 # Epsilon inicial para exploração
FINAL_EPSILON = 0.01 # Epsilon final para exploração
EPSILON_DECAY = 0.9995 # Fator de decaimento do epsilon por rodada
TARGET_UPDATE_FREQ = 100 # Atualiza a rede target a cada 100 jogos
SAVE_INTERVAL = 500 # Salva o modelo a cada 500 jogos
MAX_ROUNDS = 50 # Limite de rodadas por jogo

def load_cards():
    """Carrega e normaliza os dados das cartas."""
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'carros.json'), 'r', encoding='utf-8') as f:
            cards = json.load(f)
    except FileNotFoundError:
        print("Erro: Arquivo de cartas 'carros.json' não encontrado.")
        sys.exit(1)
        
    # Normaliza valores (necessário para o RLBot)
    for card in cards:
        if isinstance(card.get('0-100'), str):
            card['0-100'] = float(card['0-100'].replace('s', ''))
        if isinstance(card.get('top_speed'), str):
            card['top_speed'] = float(card['top_speed'].replace(' km/h', ''))
    
    return cards

def play_round(bot1, bot2, cards, current_player, stats_list):
    """Simula uma rodada e retorna o resultado e as transições para o RLBot."""
    
    # 1. Escolha de jogada
    if current_player == 1:
        # Bot 1 escolhe carta e atributo
        card1, stat = bot1.choose_move(bot2.deck, stats_list)
        if card1 is None or stat is None: return None, None, None, None, None
        # Bot 2 escolhe carta para o atributo
        card2 = bot2.choose_card(bot1.deck, stat)
        if card2 is None: return None, None, None, None, None
        
        # Estado inicial do Bot 1
        state1 = bot1.get_state_vector(bot1.deck, stat)
        # Ação do Bot 1 (índice da carta escolhida)
        action1 = bot1.deck.index(card1)
        
    else:
        # Bot 2 escolhe carta e atributo
        card2, stat = bot2.choose_move(bot1.deck, stats_list)
        if card2 is None or stat is None: return None, None, None, None, None
        # Bot 1 escolhe carta para o atributo
        card1 = bot1.choose_card(bot2.deck, stat)
        if card1 is None: return None, None, None, None, None
        
        # Estado inicial do Bot 2
        state2 = bot2.get_state_vector(bot2.deck, stat)
        # Ação do Bot 2 (índice da carta escolhida)
        action2 = bot2.deck.index(card2)

    # 2. Avaliação
    result = evaluate(card1, card2, stat)
    
    # 3. Recompensa
    reward1 = result # +1 se Bot 1 vence, -1 se Bot 2 vence, 0 se empate
    reward2 = -result # -1 se Bot 1 vence, +1 se Bot 2 vence, 0 se empate
    
    # 4. Atualiza decks
    bot1.deck = [c for c in bot1.deck if c['id'] != card1['id']]
    bot2.deck = [c for c in bot2.deck if c['id'] != card2['id']]
    
    # 5. Estado final (próximo estado)
    next_state1 = bot1.get_state_vector(bot1.deck, stat)
    next_state2 = bot2.get_state_vector(bot2.deck, stat)
    
    # 6. Transições
    if current_player == 1:
        transition = (state1, action1, reward1, next_state1, False)
        next_player = 1 if result == 1 else 2
    else:
        transition = (state2, action2, reward2, next_state2, False)
        next_player = 2 if result == -1 else 1
        
    return transition, card1, card2, next_player, result

def train_self_play(episodes, model_path):
    """Loop principal de treinamento self-play."""
    
    cards = load_cards()
    
    # Bot local (aprende)
    local_bot = RLBot(deck=[], stats_list=STATS, qfile=model_path, epsilon=INITIAL_EPSILON)
    # Bot target (oponente estável)
    target_bot = RLBot(deck=[], stats_list=STATS, qfile=model_path, epsilon=0.0) # Epsilon 0 para explotação pura
    
    # Copia pesos da rede local para a target
    target_bot.qnetwork_target.load_state_dict(local_bot.qnetwork_local.state_dict())
    
    print(f"🚀 Iniciando treinamento self-play por {episodes} episódios...")
    print(f"   Modelo: {model_path}")
    print(f"   Epsilon inicial: {local_bot.epsilon:.4f}, Epsilon final: {FINAL_EPSILON:.4f}, Decay: {EPSILON_DECAY}")
    
    win_history = []
    
    for episode in range(1, episodes + 1):
        # Reinicia o jogo
        shuffled = random.sample(cards, len(cards))
        deck1 = shuffled[:5]
        deck2 = shuffled[5:10]
        
        local_bot.deck = copy.deepcopy(deck1)
        target_bot.deck = copy.deepcopy(deck2)
        
        bot1_wins = 0
        bot2_wins = 0
        current_player = random.choice([1, 2])
        
        for round_num in range(MAX_ROUNDS):
            # O bot que escolhe o atributo é sempre o "local_bot" ou "target_bot"
            # O outro bot apenas escolhe a melhor carta para o atributo
            
            if current_player == 1:
                # Local Bot joga como Player 1 (escolhe atributo)
                transition, card1, card2, next_player, result = play_round(local_bot, target_bot, cards, 1, STATS)
            else:
                # Target Bot joga como Player 2 (escolhe atributo)
                transition, card1, card2, next_player, result = play_round(local_bot, target_bot, cards, 2, STATS)
            
            if transition is None:
                break
            
            # Armazena transição no replay buffer do Local Bot
            state, action, reward, next_state, done = transition
            local_bot.step(state, action, reward, next_state, done)
            
            # Aprende (se o buffer estiver cheio e for o momento)
            local_bot.learn()
            
            # Atualiza contagem de vitórias
            if result == 1:
                bot1_wins += 1
            elif result == -1:
                bot2_wins += 1
            
            # Próximo jogador
            current_player = next_player
            
            # Checa se o jogo acabou
            if not local_bot.deck or not target_bot.deck:
                break
        
        # Fim do jogo: recompensa final (simplificada)
        if bot1_wins > bot2_wins:
            winner = 1 # Local Bot venceu
        elif bot2_wins > bot1_wins:
            winner = 2 # Target Bot venceu
        else:
            winner = 0 # Empate
            
        win_history.append(winner)
        
        # Epsilon decay
        if local_bot.epsilon > FINAL_EPSILON:
            local_bot.epsilon *= EPSILON_DECAY
        
        # Atualiza Target Network
        if episode % TARGET_UPDATE_FREQ == 0:
            target_bot.qnetwork_target.load_state_dict(local_bot.qnetwork_local.state_dict())
            
        # Salva modelo
        if episode % SAVE_INTERVAL == 0:
            local_bot.save_q(model_path)
            
        # Log de progresso
        if episode % 100 == 0:
            win_rate_100 = win_history[-100:].count(1) / 100.0
            print(f"Episódio {episode}/{episodes} | Win Rate (últimos 100): {win_rate_100:.2f} | Epsilon: {local_bot.epsilon:.4f}")
            
    # Salva o modelo final
    local_bot.save_q(model_path)
    print("\n✅ Treinamento self-play concluído!")
    
    return win_history

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Treinamento Self-Play do RLBot (DQN)")
    parser.add_argument('--episodes', type=int, default=1000, help='Número de episódios de treinamento')
    parser.add_argument('--model', type=str, default='data/dqn_self_play.pth', help='Caminho para salvar o modelo')
    
    args = parser.parse_args()
    
    # Ajusta o caminho do modelo para ser relativo ao diretório backend
    model_path = os.path.join(os.path.dirname(__file__), '..', args.model)
    
    train_self_play(args.episodes, model_path)
