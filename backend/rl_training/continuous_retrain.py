"""
Script de treinamento contínuo do RL_Bot focado no Medio_Bot.
O treinamento será executado em um loop até o limite de tempo.
"""

import json
import random
import copy
import sys
import os
from collections import defaultdict
import time
import numpy as np

# Adiciona o caminho do backend
# O caminho é ajustado para ser executado a partir de rl_training/
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

    def play_game(self, bot1, bot2, bot1_name, bot2_name):
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
            return 1 # Bot1 vence
        elif bot2_wins > bot1_wins:
            return -1 # Bot2 vence
        else:
            return 0 # Empate


class ContinuousRLTrainer:
    """Treinador contínuo para o RL_Bot."""
    
    def __init__(self, cards, qfile_in, qfile_out, opponent_name="Medio_Bot"):
        self.cards = cards
        self.qfile_in = qfile_in
        self.qfile_out = qfile_out
        self.rl_bot = self._initialize_rl_bot()
        self.opponent_name = opponent_name
        self.opponent_bot = self._get_opponent_bot()
        self.simulator = GameSimulator(cards)
        self.training_history = []
        self.total_episodes = 0
        self.max_episodes = 10000000 # Limite de segurança
        self.max_time_s = 7200 # 2 horas
        
    def _initialize_rl_bot(self):
        """Inicializa o RL_Bot, carregando a Q-table massiva."""
        # O caminho é ajustado para ser executado a partir de rl_training/
        qfile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', self.qfile_in)
        
        rl_bot = RLBot(
            deck=[],
            epsilon=0.1,   # Começa com exploração moderada
            alpha=0.4,     # Taxa de aprendizado
            gamma=0.95,    # Fator de desconto
            qfile=qfile_path
        )
        print(f"[Trainer] RL_Bot inicializado. Estados carregados: {len(rl_bot.Q):,}")
        return rl_bot

    def _get_opponent_bot(self):
        """Retorna a instância do bot oponente."""
        if self.opponent_name == "Facil_Bot":
            return WeightedBot(deck=[])
        elif self.opponent_name == "Medio_Bot":
            return MCTSBot(deck=[], simulations=50)
        else:
            raise ValueError(f"Oponente desconhecido: {self.opponent_name}")

    def train_episode(self, rl_bot, opponent_bot):
        """Executa um único episódio de treinamento."""
        rl_deck, opp_deck = split_deck(self.cards)
        rl_bot.deck = copy.deepcopy(rl_deck)
        opponent_bot.deck = copy.deepcopy(opp_deck)
        
        episode_reward = 0
        rounds_played = 0
        history = []
        current_player = random.choice(['rl', 'opp'])
        
        while rl_bot.deck and opponent_bot.deck and rounds_played < 50:
            rounds_played += 1
            old_state = rl_bot.get_state()
            
            if current_player == 'rl':
                rl_card, stat = rl_bot.choose_move(opponent_bot.deck, STATS)
                opp_card = opponent_bot.choose_card(rl_bot.deck, stat)
            else:
                opp_card, stat = opponent_bot.choose_move(rl_bot.deck, STATS)
                rl_card = rl_bot.choose_card(opponent_bot.deck, stat)
            
            result = evaluate(rl_card, opp_card, stat)
            
            if result == 1:
                reward = 2.0
                current_player = 'rl'
            elif result == -1:
                reward = -1.5
                current_player = 'opp'
            else:
                reward = -0.5
            
            episode_reward += reward
            
            history.append({
                'old_state': old_state,
                'action': rl_card['id'],
                'stat': stat,
                'reward': reward
            })
            
            rl_bot.deck = [c for c in rl_bot.deck if c['id'] != rl_card['id']]
            opponent_bot.deck = [c for c in opponent_bot.deck if c['id'] != opp_card['id']]
        
        # Bônus/penalidade final
        final_reward = 0
        if episode_reward > 0:
            final_reward = 5.0
        elif episode_reward < 0:
            final_reward = -3.0
        
        # Atualiza Q-table
        for i, transition in enumerate(history):
            old_state = transition['old_state']
            action = transition['action']
            stat = transition['stat']
            reward = transition['reward']
            
            if i == len(history) - 1:
                reward += final_reward
            
            if i + 1 < len(history):
                next_stat = history[i + 1]['stat']
            else:
                next_stat = stat
            
            new_state = tuple(sorted([card_id for card_id in old_state if card_id != action]))
            
            old_state_stat = (old_state, stat)
            rl_bot.update_q(old_state_stat, action, reward, new_state, next_stat)
        
        return episode_reward

    def evaluate_win_rate(self, num_games=100):
        """Avalia a taxa de vitória do RL_Bot contra o oponente de treinamento."""
        wins = 0
        
        # Cria uma cópia do RL_Bot sem exploração para avaliação
        eval_rl_bot = copy.deepcopy(self.rl_bot)
        eval_rl_bot.epsilon = 0.0
        
        # Cria uma cópia do oponente
        eval_opponent = self._get_opponent_bot()
        
        for _ in range(num_games):
            # O RL_Bot é sempre o bot1 na avaliação
            result = self.simulator.play_game(eval_rl_bot, eval_opponent, "RL_Bot", self.opponent_name)
            if result == 1:
                wins += 1
        
        return wins / num_games

    def continuous_training(self):
        """Executa o treinamento em loop."""
        start_time = time.time()
        
        print(f"\n{'='*80}")
        print(f"TREINAMENTO CONTÍNUO DO RL_BOT")
        print(f"{'='*80}")
        print(f"Oponente de Treinamento: {self.opponent_name}")
        print(f"Tempo limite: {self.max_time_s/60:.0f} minutos")
        print(f"{'='*80}\n")
        
        episodes_in_batch = 2000
        
        while time.time() - start_time < self.max_time_s and self.total_episodes < self.max_episodes:
            batch_rewards = []
            batch_start_time = time.time()
            
            # Ajusta epsilon (decay)
            self.rl_bot.epsilon = max(0.05, 0.1 * (1 - self.total_episodes / self.max_episodes))
            
            for _ in range(episodes_in_batch):
                reward = self.train_episode(self.rl_bot, self.opponent_bot)
                batch_rewards.append(reward)
                self.total_episodes += 1
                
                if self.total_episodes >= self.max_episodes:
                    break
            
            batch_time = time.time() - batch_start_time
            avg_reward = np.mean(batch_rewards)
            
            # Avaliação de Win Rate a cada 1000 episódios
            win_rate = self.evaluate_win_rate(num_games=100)
            
            self.training_history.extend(batch_rewards)
            
            print(f"Episódios: {self.total_episodes:,} | Tempo: {batch_time:.1f}s | Epsilon: {self.rl_bot.epsilon:.3f}")
            print(f"  Recompensa Média: {avg_reward:.3f} | Win Rate vs {self.opponent_name}: {win_rate*100:.1f}%")
            print(f"  Estados: {len(self.rl_bot.Q):,}")
            
            # Salva checkpoint
            qfile_path_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', self.qfile_out)
            self.rl_bot.save_q(qfile_path_out)
            
        print(f"\n{'='*80}")
        print("TREINAMENTO INTERROMPIDO (Limite de tempo ou episódios atingido)")
        print(f"{'='*80}")
        print(f"Total de episódios: {self.total_episodes:,}")
        print(f"Tempo total: {(time.time() - start_time)/60:.1f} minutos")
        print(f"Estados finais: {len(self.rl_bot.Q):,}")
        print(f"{'='*80}\n")
        
        # Salva histórico final
        history_path = 'continuous_training_history_new.json'
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(self.training_history, f, indent=2)
        print(f"✓ Histórico de treinamento salvo em {history_path}")


def main():
    """Função principal."""
    # O arquivo de cartas é esperado em Projeto_IntegradorVI-main/backend/data/carros.json
    cards_path = '../data/carros.json'
    
    # Os arquivos de Q-table são esperados no diretório raiz da Manus
    qfile_in = 'rl_q_table_massive_v2.json'
    qfile_out = 'rl_q_table_massive_v2.json' # Sobrescreve o arquivo de entrada
    
    # === MUDAR O OPONENTE AQUI ===
    # Opções: "Facil_Bot" ou "Medio_Bot"
    opponent_to_train_against = "Medio_Bot"
    # =============================
    
    cards = load_cards(cards_path)
    
    trainer = ContinuousRLTrainer(cards, qfile_in, qfile_out, opponent_to_train_against)
    trainer.continuous_training()


if __name__ == "__main__":
    main()
