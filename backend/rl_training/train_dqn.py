"""
Script de Treinamento DQN (Deep Q-Network) para Super Trunfo
=============================================================

Este é o script unificado para treinar o RL_Bot usando Deep Q-Network (DQN).
Substitui os antigos scripts de Q-Learning baseados em tabela.

Características:
- Treinamento progressivo contra múltiplos oponentes
- Ajuste dinâmico de epsilon (exploração vs explotação)
- Avaliação periódica de desempenho
- Sistema de logs estruturado
- Salvamento automático de checkpoints

Uso:
    python train_dqn.py [--episodes EPISODES] [--eval-interval INTERVAL]
"""

import json
import random
import copy
import sys
import os
import argparse
import time
from datetime import datetime
import numpy as np
import torch

# Adiciona o caminho do backend ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils import STATS, evaluate
from bots.rl_bot import RLBot
from bots.weighted_bot import WeightedBot
from bots.mcts_bot import MCTSBot


class TrainingLogger:
    """Sistema de logs estruturado para o treinamento."""
    
    def __init__(self, log_dir="../logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"training_dqn_{timestamp}.log")
        
        self.log("="*80)
        self.log("TREINAMENTO DQN - Super Trunfo RL Bot")
        self.log(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("="*80)
    
    def log(self, message):
        """Registra mensagem no arquivo de log e imprime no console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def log_metrics(self, episode, metrics):
        """Registra métricas de treinamento."""
        self.log(f"\n--- Episódio {episode:,} ---")
        for key, value in metrics.items():
            if isinstance(value, float):
                self.log(f"  {key}: {value:.4f}")
            else:
                self.log(f"  {key}: {value}")


class GameSimulator:
    """Simula jogos entre dois bots para treinamento e avaliação."""
    
    def __init__(self, cards):
        self.cards = cards
    
    def split_deck(self, num_cards_per_player=5):
        """Divide o baralho em dois decks aleatórios."""
        shuffled = random.sample(self.cards, len(self.cards))
        deck1 = shuffled[:num_cards_per_player]
        deck2 = shuffled[num_cards_per_player:num_cards_per_player*2]
        return deck1, deck2
    
    def play_game(self, bot1, bot2):
        """
        Simula um jogo completo entre dois bots.
        
        Returns:
            1 se bot1 vence, -1 se bot2 vence, 0 em caso de empate
        """
        deck1, deck2 = self.split_deck()
        bot1.deck = copy.deepcopy(deck1)
        bot2.deck = copy.deepcopy(deck2)
        
        bot1_wins = 0
        bot2_wins = 0
        rounds_played = 0
        current_player = random.choice([1, 2])
        
        while bot1.deck and bot2.deck and rounds_played < 50:
            rounds_played += 1
            
            if current_player == 1:
                card1, stat = bot1.choose_move(bot1.deck, STATS)
                card2 = bot2.choose_card(bot2.deck, stat)
            else:
                card2, stat = bot2.choose_move(bot2.deck, STATS)
                card1 = bot1.choose_card(bot1.deck, stat)
            
            if card1 is None or card2 is None:
                break
            
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
            return 1
        elif bot2_wins > bot1_wins:
            return -1
        else:
            return 0


class DQNTrainer:
    """Treinador principal para o DQN Bot."""
    
    def __init__(self, cards, model_path=None, logger=None):
        self.cards = cards
        self.logger = logger or TrainingLogger()
        self.simulator = GameSimulator(cards)
        
        # Inicializa o DQN Bot
        self.dqn_bot = RLBot(
            deck=[],
            stats_list=STATS,
            qfile=model_path,
            epsilon=1.0,      # Começa com exploração máxima
            alpha=0.0005,     # Taxa de aprendizado
            gamma=0.99        # Fator de desconto
        )
        
        self.logger.log(f"DQN Bot inicializado")
        self.logger.log(f"  Device: {self.dqn_bot.device}")
        self.logger.log(f"  Epsilon inicial: {self.dqn_bot.epsilon}")
        self.logger.log(f"  Alpha (learning rate): {self.dqn_bot.alpha}")
        self.logger.log(f"  Gamma (discount): {self.dqn_bot.gamma}")
        
        # Histórico de treinamento
        self.training_history = {
            'episodes': [],
            'avg_rewards': [],
            'epsilon_values': [],
            'win_rates': {
                'Facil_Bot': [],
                'Medio_Bot': []
            }
        }
        
        self.total_episodes = 0
        self.best_win_rate_medio = 0.0
    
    def get_opponent_bot(self, opponent_name):
        """Retorna uma instância do bot oponente."""
        if opponent_name == "Facil_Bot":
            return WeightedBot(deck=[])
        elif opponent_name == "Medio_Bot":
            return MCTSBot(deck=[], simulations=50)
        else:
            raise ValueError(f"Oponente desconhecido: {opponent_name}")
    
    def train_episode(self, opponent_name):
        """
        Executa um episódio de treinamento contra um oponente.
        
        Returns:
            episode_reward: Recompensa total do episódio
        """
        opponent_bot = self.get_opponent_bot(opponent_name)
        
        # Divide o deck
        rl_deck, opp_deck = self.simulator.split_deck()
        self.dqn_bot.deck = copy.deepcopy(rl_deck)
        opponent_bot.deck = copy.deepcopy(opp_deck)
        
        episode_reward = 0
        rounds_played = 0
        current_player = random.choice(['rl', 'opp'])
        
        # Histórico de transições para atualização
        transitions = []
        
        while self.dqn_bot.deck and opponent_bot.deck and rounds_played < 50:
            rounds_played += 1
            
            # Estado atual
            if current_player == 'rl':
                rl_card, stat = self.dqn_bot.choose_move(self.dqn_bot.deck, STATS)
                opp_card = opponent_bot.choose_card(opponent_bot.deck, stat)
            else:
                opp_card, stat = opponent_bot.choose_move(opponent_bot.deck, STATS)
                rl_card = self.dqn_bot.choose_card(self.dqn_bot.deck, stat)
            
            if rl_card is None or opp_card is None:
                break
            
            # Avalia o resultado
            result = evaluate(rl_card, opp_card, stat)
            
            # Sistema de recompensas
            if result == 1:
                reward = 3.0 if opponent_name == "Facil_Bot" else 5.0
                current_player = 'rl'
            elif result == -1:
                reward = -2.0 if opponent_name == "Facil_Bot" else -3.0
                current_player = 'opp'
            else:
                reward = -0.5
            
            episode_reward += reward
            
            # Salva estado antes da ação
            old_state = self.dqn_bot.get_state_vector(self.dqn_bot.deck, stat)
            action_index = next(i for i, c in enumerate(self.dqn_bot.deck) if c['id'] == rl_card['id'])
            
            # Remove cartas jogadas
            self.dqn_bot.deck = [c for c in self.dqn_bot.deck if c['id'] != rl_card['id']]
            opponent_bot.deck = [c for c in opponent_bot.deck if c['id'] != opp_card['id']]
            
            # Novo estado
            new_state = self.dqn_bot.get_state_vector(self.dqn_bot.deck, stat)
            done = len(self.dqn_bot.deck) == 0 or len(opponent_bot.deck) == 0
            
            # Armazena transição
            transitions.append((old_state, action_index, reward, new_state, done))
        
        # Bônus/penalidade final
        if episode_reward > 0:
            final_reward = 10.0 if opponent_name == "Facil_Bot" else 15.0
        elif episode_reward < 0:
            final_reward = -5.0 if opponent_name == "Facil_Bot" else -8.0
        else:
            final_reward = 0.0
        
        # Adiciona recompensa final à última transição
        if transitions:
            last_transition = list(transitions[-1])
            last_transition[2] += final_reward
            transitions[-1] = tuple(last_transition)
        
        # Atualiza a rede neural com as transições
        for transition in transitions:
            self.dqn_bot.step(*transition)
        
        return episode_reward
    
    def evaluate_performance(self, num_games=100):
        """
        Avalia o desempenho do DQN Bot contra todos os oponentes.
        
        Returns:
            dict: Taxa de vitória contra cada oponente
        """
        results = {}
        
        # Cria uma cópia do bot com epsilon=0 (sem exploração)
        eval_bot = copy.deepcopy(self.dqn_bot)
        eval_bot.epsilon = 0.0
        
        for opponent_name in ['Facil_Bot', 'Medio_Bot']:
            wins = 0
            draws = 0
            
            opponent_bot = self.get_opponent_bot(opponent_name)
            
            for _ in range(num_games):
                result = self.simulator.play_game(eval_bot, opponent_bot)
                if result == 1:
                    wins += 1
                elif result == 0:
                    draws += 1
            
            win_rate = wins / num_games
            draw_rate = draws / num_games
            
            results[opponent_name] = {
                'win_rate': win_rate,
                'draw_rate': draw_rate
            }
        
        return results
    
    def train(self, episodes=50000, eval_interval=1000, save_interval=5000):
        """
        Executa o treinamento completo do DQN Bot.
        
        Args:
            episodes: Número total de episódios de treinamento
            eval_interval: Intervalo para avaliação de desempenho
            save_interval: Intervalo para salvamento de checkpoints
        """
        start_time = time.time()
        
        self.logger.log(f"\nIniciando treinamento:")
        self.logger.log(f"  Total de episódios: {episodes:,}")
        self.logger.log(f"  Avaliação a cada: {eval_interval:,} episódios")
        self.logger.log(f"  Salvamento a cada: {save_interval:,} episódios")
        self.logger.log("")
        
        recent_rewards = []
        
        for episode in range(episodes):
            self.total_episodes += 1
            
            # Decay do epsilon (exploração -> explotação)
            # Decai de 1.0 para 0.05 ao longo do treinamento
            self.dqn_bot.epsilon = max(0.05, 1.0 - (episode / episodes) * 0.95)
            
            # Distribuição progressiva de oponentes
            # Fase inicial: mais contra Facil_Bot
            # Fase final: mais contra Medio_Bot
            if episode < episodes * 0.3:
                opponent_pool = ["Facil_Bot"] * 70 + ["Medio_Bot"] * 30
            elif episode < episodes * 0.6:
                opponent_pool = ["Facil_Bot"] * 50 + ["Medio_Bot"] * 50
            else:
                opponent_pool = ["Facil_Bot"] * 30 + ["Medio_Bot"] * 70
            
            opponent = random.choice(opponent_pool)
            
            # Treina um episódio
            reward = self.train_episode(opponent)
            recent_rewards.append(reward)
            
            # Mantém apenas as últimas 100 recompensas
            if len(recent_rewards) > 100:
                recent_rewards.pop(0)
            
            # Avaliação periódica
            if (episode + 1) % eval_interval == 0:
                avg_reward = np.mean(recent_rewards)
                
                self.logger.log(f"\n{'='*80}")
                self.logger.log(f"Episódio {episode + 1:,}/{episodes:,}")
                self.logger.log(f"  Epsilon: {self.dqn_bot.epsilon:.4f}")
                self.logger.log(f"  Recompensa média (últimos 100): {avg_reward:.2f}")
                self.logger.log(f"  Tamanho do buffer: {len(self.dqn_bot.memory):,}")
                
                # Avalia desempenho
                self.logger.log(f"\n  Avaliando desempenho (100 jogos por oponente)...")
                eval_results = self.evaluate_performance(num_games=100)
                
                for opp_name, metrics in eval_results.items():
                    win_rate = metrics['win_rate']
                    draw_rate = metrics['draw_rate']
                    
                    self.training_history['win_rates'][opp_name].append(win_rate)
                    
                    # Marca novo recorde contra Medio_Bot
                    marker = ""
                    if opp_name == "Medio_Bot" and win_rate > self.best_win_rate_medio:
                        self.best_win_rate_medio = win_rate
                        marker = " 🔥 NOVO RECORDE!"
                    
                    self.logger.log(f"    vs {opp_name:12s}: {win_rate*100:5.1f}% vitórias | {draw_rate*100:5.1f}% empates{marker}")
                
                self.training_history['episodes'].append(self.total_episodes)
                self.training_history['avg_rewards'].append(avg_reward)
                self.training_history['epsilon_values'].append(self.dqn_bot.epsilon)
                
                self.logger.log(f"{'='*80}\n")
            
            # Salvamento periódico
            if (episode + 1) % save_interval == 0:
                self.save_checkpoint()
        
        # Salvamento final
        self.save_checkpoint()
        
        elapsed_time = time.time() - start_time
        
        self.logger.log(f"\n{'='*80}")
        self.logger.log("TREINAMENTO CONCLUÍDO")
        self.logger.log(f"{'='*80}")
        self.logger.log(f"Total de episódios: {self.total_episodes:,}")
        self.logger.log(f"Tempo total: {elapsed_time/60:.1f} minutos")
        self.logger.log(f"Melhor Win Rate vs Medio_Bot: {self.best_win_rate_medio*100:.1f}%")
        self.logger.log(f"{'='*80}\n")
    
    def save_checkpoint(self):
        """Salva checkpoint do modelo e histórico de treinamento."""
        # Salva pesos da rede neural
        model_path = "data/dqn_model.pth"
        self.dqn_bot.save_q(model_path)
        
        # Salva histórico de treinamento
        history_path = "data/dqn_training_history.json"
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(self.training_history, f, indent=2)
        
        self.logger.log(f"  ✓ Checkpoint salvo:")
        self.logger.log(f"    - Modelo: {model_path}")
        self.logger.log(f"    - Histórico: {history_path}")


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


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Treinamento DQN para Super Trunfo RL Bot')
    parser.add_argument('--episodes', type=int, default=50000, help='Número de episódios de treinamento')
    parser.add_argument('--eval-interval', type=int, default=1000, help='Intervalo de avaliação')
    parser.add_argument('--save-interval', type=int, default=5000, help='Intervalo de salvamento')
    parser.add_argument('--model', type=str, default=None, help='Caminho para modelo pré-treinado')
    
    args = parser.parse_args()
    
    # Carrega as cartas
    cards_path = 'data/carros.json'
    cards = load_cards(cards_path)
    print(f"[Setup] Carregadas {len(cards)} cartas do deck\n")
    
    # Inicializa o treinador
    logger = TrainingLogger()
    trainer = DQNTrainer(cards, model_path=args.model, logger=logger)
    
    # Executa o treinamento
    trainer.train(
        episodes=args.episodes,
        eval_interval=args.eval_interval,
        save_interval=args.save_interval
    )


if __name__ == "__main__":
    main()
