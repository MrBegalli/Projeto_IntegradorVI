"""
Script de treinamento otimizado do RL_Bot contra todos os oponentes.
Maximiza o winrate através de treinamento multi-oponente e ajustes de hiperparâmetros.
"""

import json
import random
import copy
import sys
import os
from collections import defaultdict
import time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils import STATS, evaluate
from bots.weighted_bot import WeightedBot
from bots.mcts_bot import MCTSBot
from bots.rl_bot import RLBot


def load_cards(filepath):
    """Carrega as cartas do arquivo JSON e normaliza os valores."""
    with open(filepath, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    # Normaliza valores (remove unidades de medida)
    for card in cards:
        if isinstance(card.get('0-100'), str):
            card['0-100'] = float(card['0-100'].replace('s', ''))
        if isinstance(card.get('top_speed'), str):
            card['top_speed'] = float(card['top_speed'].replace(' km/h', ''))
    
    return cards


def split_deck(cards, num_cards_per_player=5):
    """Divide o baralho em dois decks aleatórios."""
    shuffled = random.sample(cards, len(cards))
    player1_deck = shuffled[:num_cards_per_player]
    player2_deck = shuffled[num_cards_per_player:num_cards_per_player*2]
    return player1_deck, player2_deck


class GameSimulator:
    """Simula jogos entre dois bots para avaliação."""
    
    def __init__(self, cards):
        self.cards = cards

    def play_game(self, bot1, bot2, verbose=False):
        """Simula um jogo completo entre dois bots."""
        deck1, deck2 = split_deck(self.cards)
        bot1.deck = copy.deepcopy(deck1)
        bot2.deck = copy.deepcopy(deck2)
        
        bot1_wins = 0
        bot2_wins = 0
        rounds_played = 0
        current_player = random.choice([1, 2])
        
        while bot1.deck and bot2.deck and rounds_played < 50:
            rounds_played += 1
            
            if current_player == 1:
                card1, stat = bot1.choose_move(bot2.deck, STATS)
                card2 = bot2.choose_card(bot1.deck, stat)
            else:
                card2, stat = bot2.choose_move(bot1.deck, STATS)
                card1 = bot1.choose_card(bot2.deck, stat)
            
            result = evaluate(card1, card2, stat)
            
            if result == 1:
                bot1_wins += 1
                current_player = 1
            elif result == -1:
                bot2_wins += 1
                current_player = 2
            
            bot1.deck = [c for c in bot1.deck if c['id'] != card1['id']]
            bot2.deck = [c for c in bot2.deck if c['id'] != card2['id']]
        
        if bot1_wins > bot2_wins:
            return 1  # Bot1 vence
        elif bot2_wins > bot1_wins:
            return -1  # Bot2 vence
        else:
            return 0  # Empate


class OptimizedRLTrainer:
    """Treinador otimizado para o RL_Bot com treinamento multi-oponente."""
    
    def __init__(self, cards, qfile_in=None, qfile_out="rl_q_table_optimized.json"):
        self.cards = cards
        self.qfile_out = qfile_out
        self.rl_bot = self._initialize_rl_bot(qfile_in)
        self.simulator = GameSimulator(cards)
        self.training_history = {
            'episodes': [],
            'rewards': [],
            'win_rates': {
                'Facil_Bot': [],
                'Medio_Bot': [],
                'RL_Bot_Mirror': []
            }
        }
        self.total_episodes = 0
        
    def _initialize_rl_bot(self, qfile_in):
        """Inicializa o RL_Bot, carregando Q-table se fornecida."""
        qfile_path = None
        if qfile_in and os.path.exists(qfile_in):
            qfile_path = qfile_in
        
        rl_bot = RLBot(
            deck=[],
            epsilon=0.3,    # Exploração inicial mais alta
            alpha=0.5,      # Taxa de aprendizado moderada
            gamma=0.95,     # Fator de desconto alto (valoriza futuro)
            qfile=qfile_path
        )
        
        if qfile_path:
            print(f"[Trainer] RL_Bot inicializado com Q-table. Estados: {len(rl_bot.Q):,}")
        else:
            print("[Trainer] RL_Bot inicializado sem Q-table (treinamento do zero)")
        
        return rl_bot

    def _get_opponent_bot(self, opponent_name):
        """Retorna a instância do bot oponente."""
        if opponent_name == "Facil_Bot":
            return WeightedBot(deck=[])
        elif opponent_name == "Medio_Bot":
            return MCTSBot(deck=[], simulations=50)
        elif opponent_name == "RL_Bot_Mirror":
            # Cria uma cópia do RL_Bot sem exploração para servir como oponente
            mirror_bot = copy.deepcopy(self.rl_bot)
            mirror_bot.epsilon = 0.0
            return mirror_bot
        else:
            raise ValueError(f"Oponente desconhecido: {opponent_name}")

    def train_episode(self, opponent_name):
        """Executa um único episódio de treinamento contra um oponente."""
        opponent_bot = self._get_opponent_bot(opponent_name)
        
        rl_deck, opp_deck = split_deck(self.cards)
        self.rl_bot.deck = copy.deepcopy(rl_deck)
        opponent_bot.deck = copy.deepcopy(opp_deck)
        
        episode_reward = 0
        rounds_played = 0
        history = []
        current_player = random.choice(['rl', 'opp'])
        
        while self.rl_bot.deck and opponent_bot.deck and rounds_played < 50:
            rounds_played += 1
            old_state = self.rl_bot.get_state()
            
            if current_player == 'rl':
                rl_card, stat = self.rl_bot.choose_move(opponent_bot.deck, STATS)
                opp_card = opponent_bot.choose_card(self.rl_bot.deck, stat)
            else:
                opp_card, stat = opponent_bot.choose_move(self.rl_bot.deck, STATS)
                rl_card = self.rl_bot.choose_card(opponent_bot.deck, stat)
            
            result = evaluate(rl_card, opp_card, stat)
            
            # Sistema de recompensas ajustado
            if result == 1:
                reward = 3.0  # Vitória na rodada
                current_player = 'rl'
            elif result == -1:
                reward = -2.0  # Derrota na rodada
                current_player = 'opp'
            else:
                reward = -0.5  # Empate (penalidade leve)
            
            episode_reward += reward
            
            history.append({
                'old_state': old_state,
                'action': rl_card['id'],
                'stat': stat,
                'reward': reward
            })
            
            self.rl_bot.deck = [c for c in self.rl_bot.deck if c['id'] != rl_card['id']]
            opponent_bot.deck = [c for c in opponent_bot.deck if c['id'] != opp_card['id']]
        
        # Bônus/penalidade final baseado no resultado do jogo
        final_reward = 0
        if episode_reward > 0:
            final_reward = 10.0  # Vitória no jogo
        elif episode_reward < 0:
            final_reward = -5.0  # Derrota no jogo
        
        # Atualiza Q-table com todas as transições
        for i, transition in enumerate(history):
            old_state = transition['old_state']
            action = transition['action']
            stat = transition['stat']
            reward = transition['reward']
            
            # Adiciona recompensa final na última transição
            if i == len(history) - 1:
                reward += final_reward
            
            # Determina o próximo estado
            if i + 1 < len(history):
                next_stat = history[i + 1]['stat']
            else:
                next_stat = stat
            
            new_state = tuple(sorted([card_id for card_id in old_state if card_id != action]))
            
            old_state_stat = (old_state, stat)
            self.rl_bot.update_q(old_state_stat, action, reward, new_state, next_stat)
        
        return episode_reward

    def evaluate_win_rate(self, opponent_name, num_games=100):
        """Avalia a taxa de vitória do RL_Bot contra um oponente específico."""
        wins = 0
        draws = 0
        
        # Cria uma cópia do RL_Bot sem exploração para avaliação
        eval_rl_bot = copy.deepcopy(self.rl_bot)
        eval_rl_bot.epsilon = 0.0
        
        # Cria o oponente
        eval_opponent = self._get_opponent_bot(opponent_name)
        
        for _ in range(num_games):
            result = self.simulator.play_game(eval_rl_bot, eval_opponent)
            if result == 1:
                wins += 1
            elif result == 0:
                draws += 1
        
        return wins / num_games, draws / num_games

    def train(self, episodes=5000, eval_interval=500, save_interval=1000):
        """Executa o treinamento completo com avaliação periódica."""
        start_time = time.time()
        
        print(f"\n{'='*80}")
        print(f"TREINAMENTO OTIMIZADO DO RL_BOT")
        print(f"{'='*80}")
        print(f"Total de episódios: {episodes:,}")
        print(f"Avaliação a cada: {eval_interval} episódios")
        print(f"{'='*80}\n")
        
        # Define a distribuição de oponentes para treinamento
        # 40% Facil, 40% Medio, 20% Mirror (auto-jogo)
        opponent_pool = (
            ["Facil_Bot"] * 40 +
            ["Medio_Bot"] * 40 +
            ["RL_Bot_Mirror"] * 20
        )
        
        for episode in range(episodes):
            self.total_episodes += 1
            
            # Decay do epsilon (exploração -> explotação)
            self.rl_bot.epsilon = max(0.05, 0.3 * (1 - episode / episodes))
            
            # Escolhe oponente aleatório da pool
            opponent = random.choice(opponent_pool)
            
            # Treina um episódio
            reward = self.train_episode(opponent)
            self.training_history['episodes'].append(self.total_episodes)
            self.training_history['rewards'].append(reward)
            
            # Avaliação periódica
            if (episode + 1) % eval_interval == 0:
                print(f"\n[Episódio {episode + 1:,}/{episodes:,}]")
                print(f"  Epsilon: {self.rl_bot.epsilon:.3f}")
                print(f"  Estados na Q-table: {len(self.rl_bot.Q):,}")
                print(f"  Recompensa média (últimos {eval_interval}): {np.mean(self.training_history['rewards'][-eval_interval:]):.2f}")
                
                # Avalia contra todos os oponentes
                print(f"\n  Avaliando Win Rate ({100} jogos por oponente)...")
                for opp_name in ['Facil_Bot', 'Medio_Bot', 'RL_Bot_Mirror']:
                    win_rate, draw_rate = self.evaluate_win_rate(opp_name, num_games=100)
                    self.training_history['win_rates'][opp_name].append(win_rate)
                    print(f"    vs {opp_name:15s}: {win_rate*100:5.1f}% vitórias | {draw_rate*100:5.1f}% empates")
            
            # Salvamento periódico
            if (episode + 1) % save_interval == 0:
                self.save_checkpoint()
        
        # Salvamento final
        self.save_checkpoint()
        
        elapsed_time = time.time() - start_time
        print(f"\n{'='*80}")
        print("TREINAMENTO CONCLUÍDO")
        print(f"{'='*80}")
        print(f"Total de episódios: {self.total_episodes:,}")
        print(f"Tempo total: {elapsed_time/60:.1f} minutos")
        print(f"Estados finais: {len(self.rl_bot.Q):,}")
        print(f"{'='*80}\n")
        
        return self.training_history

    def save_checkpoint(self):
        """Salva checkpoint do treinamento."""
        # Salva Q-table
        self.rl_bot.save_q(self.qfile_out)
        
        # Salva histórico de treinamento
        history_file = self.qfile_out.replace('.json', '_history.json')
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.training_history, f, indent=2)
        
        print(f"  ✓ Checkpoint salvo: {self.qfile_out}")


def main():
    """Função principal."""
    # Caminhos dos arquivos
    cards_path = '../data/carros.json'
    qfile_in = '../data/rl_q_table.json'  # Q-table existente (opcional)
    qfile_out = '../data/rl_q_table_optimized.json'
    
    # Carrega as cartas
    cards = load_cards(cards_path)
    print(f"[Setup] Carregadas {len(cards)} cartas do deck")
    
    # Inicializa o treinador
    trainer = OptimizedRLTrainer(cards, qfile_in=qfile_in, qfile_out=qfile_out)
    
    # Executa o treinamento
    # Ajuste o número de episódios conforme necessário
    # 5000 episódios = ~10-15 minutos
    # 10000 episódios = ~20-30 minutos
    trainer.train(episodes=10000, eval_interval=500, save_interval=2000)


if __name__ == "__main__":
    main()
