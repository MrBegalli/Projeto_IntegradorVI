"""
Script de avaliação completa do RL_Bot e geração de gráficos de desempenho.
Gera: Heatmap, Radar Chart e Gráfico de Barras.
"""

import json
import random
import copy
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils import STATS, evaluate
from bots.weighted_bot import WeightedBot
from bots.mcts_bot import MCTSBot
from bots.rl_bot import RLBot


def load_cards(filepath):
    """Carrega as cartas do arquivo JSON e normaliza os valores."""
    with open(filepath, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
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

    def play_game(self, bot1, bot2):
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


class BotEvaluator:
    """Avaliador completo de desempenho dos bots."""
    
    def __init__(self, cards, qfile):
        self.cards = cards
        self.simulator = GameSimulator(cards)
        self.qfile = qfile
        
        # Inicializa os bots
        self.rl_bot = RLBot(deck=[], epsilon=0.0, qfile=qfile)
        self.weighted_bot = WeightedBot(deck=[])
        self.mcts_bot = MCTSBot(deck=[], simulations=50)
        
        print(f"[Evaluator] RL_Bot carregado com {len(self.rl_bot.Q):,} estados")
    
    def evaluate_matchup(self, bot1, bot1_name, bot2, bot2_name, num_games=500):
        """Avalia um confronto específico entre dois bots."""
        results = {'wins': 0, 'losses': 0, 'draws': 0}
        
        for _ in range(num_games):
            result = self.simulator.play_game(bot1, bot2)
            if result == 1:
                results['wins'] += 1
            elif result == -1:
                results['losses'] += 1
            else:
                results['draws'] += 1
        
        win_rate = results['wins'] / num_games
        loss_rate = results['losses'] / num_games
        draw_rate = results['draws'] / num_games
        
        print(f"  {bot1_name} vs {bot2_name}: {win_rate*100:.1f}% vitórias | {draw_rate*100:.1f}% empates | {loss_rate*100:.1f}% derrotas")
        
        return {
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'draw_rate': draw_rate
        }
    
    def full_evaluation(self, num_games=500):
        """Avaliação completa de todos os confrontos."""
        print(f"\n{'='*80}")
        print(f"AVALIAÇÃO COMPLETA - {num_games} jogos por confronto")
        print(f"{'='*80}\n")
        
        results = {}
        
        # RL_Bot vs todos
        print("[RL_Bot]")
        results['RL_vs_Facil'] = self.evaluate_matchup(
            copy.deepcopy(self.rl_bot), "RL_Bot",
            copy.deepcopy(self.weighted_bot), "Facil_Bot",
            num_games
        )
        
        results['RL_vs_Medio'] = self.evaluate_matchup(
            copy.deepcopy(self.rl_bot), "RL_Bot",
            copy.deepcopy(self.mcts_bot), "Medio_Bot",
            num_games
        )
        
        # Medio_Bot vs Facil_Bot (referência)
        print("\n[Referência]")
        results['Medio_vs_Facil'] = self.evaluate_matchup(
            copy.deepcopy(self.mcts_bot), "Medio_Bot",
            copy.deepcopy(self.weighted_bot), "Facil_Bot",
            num_games
        )
        
        print(f"\n{'='*80}\n")
        
        return results
    
    def generate_heatmap(self, results, output_path='heatmap_winrate.png'):
        """Gera heatmap de taxa de vitória."""
        # Matriz de confrontos (linhas atacam, colunas defendem)
        bots = ['RL_Bot', 'Medio_Bot', 'Facil_Bot']
        matrix = np.zeros((3, 3))
        
        # Preenche a matriz
        matrix[0, 1] = results['RL_vs_Medio']['win_rate'] * 100  # RL vs Medio
        matrix[0, 2] = results['RL_vs_Facil']['win_rate'] * 100  # RL vs Facil
        matrix[1, 0] = results['RL_vs_Medio']['loss_rate'] * 100  # Medio vs RL
        matrix[1, 2] = results['Medio_vs_Facil']['win_rate'] * 100  # Medio vs Facil
        matrix[2, 0] = results['RL_vs_Facil']['loss_rate'] * 100  # Facil vs RL
        matrix[2, 1] = results['Medio_vs_Facil']['loss_rate'] * 100  # Facil vs Medio
        
        # Diagonal (auto-confronto) = 50%
        np.fill_diagonal(matrix, 50)
        
        # Cria o heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            matrix,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            xticklabels=bots,
            yticklabels=bots,
            vmin=0,
            vmax=100,
            cbar_kws={'label': 'Taxa de Vitória (%)'}
        )
        plt.title('Heatmap de Taxa de Vitória\n(Linha ataca, Coluna defende)', fontsize=14, fontweight='bold')
        plt.xlabel('Oponente', fontsize=12)
        plt.ylabel('Bot', fontsize=12)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Heatmap salvo em: {output_path}")
        plt.close()
    
    def generate_radar_chart(self, results, output_path='radar_performance.png'):
        """Gera gráfico radar de desempenho."""
        categories = ['vs Facil_Bot\n(Vitórias)', 'vs Medio_Bot\n(Vitórias)', 
                      'vs Facil_Bot\n(Empates)', 'vs Medio_Bot\n(Empates)',
                      'Consistência\nGeral']
        
        # Dados do RL_Bot
        rl_data = [
            results['RL_vs_Facil']['win_rate'] * 100,
            results['RL_vs_Medio']['win_rate'] * 100,
            results['RL_vs_Facil']['draw_rate'] * 100,
            results['RL_vs_Medio']['draw_rate'] * 100,
            ((results['RL_vs_Facil']['win_rate'] + results['RL_vs_Medio']['win_rate']) / 2) * 100
        ]
        
        # Dados do Medio_Bot (referência)
        medio_data = [
            results['Medio_vs_Facil']['win_rate'] * 100,
            results['RL_vs_Medio']['loss_rate'] * 100,  # Medio vs RL
            results['Medio_vs_Facil']['draw_rate'] * 100,
            results['RL_vs_Medio']['draw_rate'] * 100,
            ((results['Medio_vs_Facil']['win_rate'] + results['RL_vs_Medio']['loss_rate']) / 2) * 100
        ]
        
        # Configuração do radar
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        rl_data += rl_data[:1]
        medio_data += medio_data[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Plota os dados
        ax.plot(angles, rl_data, 'o-', linewidth=2, label='RL_Bot', color='#2E86AB')
        ax.fill(angles, rl_data, alpha=0.25, color='#2E86AB')
        
        ax.plot(angles, medio_data, 'o-', linewidth=2, label='Medio_Bot (Ref)', color='#A23B72')
        ax.fill(angles, medio_data, alpha=0.25, color='#A23B72')
        
        # Configurações
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
        ax.grid(True)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
        
        plt.title('Radar de Desempenho dos Bots', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Radar Chart salvo em: {output_path}")
        plt.close()
    
    def generate_bar_chart(self, results, output_path='bar_comparison.png'):
        """Gera gráfico de barras comparativo."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Gráfico 1: Taxa de Vitória
        bots = ['RL_Bot', 'Medio_Bot']
        vs_facil = [
            results['RL_vs_Facil']['win_rate'] * 100,
            results['Medio_vs_Facil']['win_rate'] * 100
        ]
        vs_medio = [
            results['RL_vs_Medio']['win_rate'] * 100,
            results['RL_vs_Medio']['loss_rate'] * 100  # Medio vs RL
        ]
        
        x = np.arange(len(bots))
        width = 0.35
        
        bars1 = axes[0].bar(x - width/2, vs_facil, width, label='vs Facil_Bot', color='#06D6A0')
        bars2 = axes[0].bar(x + width/2, vs_medio, width, label='vs Medio_Bot', color='#EF476F')
        
        axes[0].set_ylabel('Taxa de Vitória (%)', fontsize=12)
        axes[0].set_title('Comparação de Taxa de Vitória', fontsize=13, fontweight='bold')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(bots)
        axes[0].legend()
        axes[0].set_ylim(0, 100)
        axes[0].grid(axis='y', alpha=0.3)
        
        # Adiciona valores nas barras
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                axes[0].text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
        
        # Gráfico 2: Distribuição de Resultados (RL_Bot)
        categories = ['vs Facil_Bot', 'vs Medio_Bot']
        wins = [
            results['RL_vs_Facil']['win_rate'] * 100,
            results['RL_vs_Medio']['win_rate'] * 100
        ]
        draws = [
            results['RL_vs_Facil']['draw_rate'] * 100,
            results['RL_vs_Medio']['draw_rate'] * 100
        ]
        losses = [
            results['RL_vs_Facil']['loss_rate'] * 100,
            results['RL_vs_Medio']['loss_rate'] * 100
        ]
        
        x2 = np.arange(len(categories))
        
        bars1 = axes[1].bar(x2, wins, width*1.5, label='Vitórias', color='#06D6A0')
        bars2 = axes[1].bar(x2, draws, width*1.5, bottom=wins, label='Empates', color='#FFD166')
        bars3 = axes[1].bar(x2, losses, width*1.5, 
                           bottom=np.array(wins)+np.array(draws), 
                           label='Derrotas', color='#EF476F')
        
        axes[1].set_ylabel('Distribuição (%)', fontsize=12)
        axes[1].set_title('Distribuição de Resultados (RL_Bot)', fontsize=13, fontweight='bold')
        axes[1].set_xticks(x2)
        axes[1].set_xticklabels(categories)
        axes[1].legend()
        axes[1].set_ylim(0, 100)
        axes[1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico de Barras salvo em: {output_path}")
        plt.close()
    
    def generate_training_progress(self, history_file, output_path='training_progress.png'):
        """Gera gráfico de progresso do treinamento."""
        if not os.path.exists(history_file):
            print(f"⚠ Arquivo de histórico não encontrado: {history_file}")
            return
        
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # Gráfico 1: Recompensa ao longo do tempo
        episodes = history['episodes']
        rewards = history['rewards']
        
        # Média móvel
        window = 100
        if len(rewards) >= window:
            moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
            axes[0].plot(episodes[:len(moving_avg)], moving_avg, linewidth=2, color='#2E86AB')
        else:
            axes[0].plot(episodes, rewards, linewidth=1, alpha=0.5, color='#2E86AB')
        
        axes[0].set_xlabel('Episódio', fontsize=12)
        axes[0].set_ylabel('Recompensa Média', fontsize=12)
        axes[0].set_title('Progresso do Treinamento - Recompensa', fontsize=13, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # Gráfico 2: Win Rate ao longo do tempo
        win_rates = history['win_rates']
        
        for bot_name, rates in win_rates.items():
            if rates:
                eval_points = np.linspace(0, len(episodes), len(rates))
                axes[1].plot(eval_points, np.array(rates)*100, marker='o', linewidth=2, label=bot_name)
        
        axes[1].set_xlabel('Episódio', fontsize=12)
        axes[1].set_ylabel('Taxa de Vitória (%)', fontsize=12)
        axes[1].set_title('Progresso do Treinamento - Win Rate', fontsize=13, fontweight='bold')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        axes[1].set_ylim(0, 100)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico de Progresso salvo em: {output_path}")
        plt.close()


def main():
    """Função principal."""
    # Caminhos dos arquivos
    cards_path = '../data/carros.json'
    qfile = '../data/rl_q_table_optimized.json'
    history_file = '../data/rl_q_table_optimized_history.json'
    
    # Carrega as cartas
    cards = load_cards(cards_path)
    
    # Verifica se a Q-table existe
    if not os.path.exists(qfile):
        print(f"[ERRO] Q-table não encontrada: {qfile}")
        print("Execute primeiro o script de treinamento: train_optimized.py")
        return
    
    # Inicializa o avaliador
    evaluator = BotEvaluator(cards, qfile)
    
    # Executa avaliação completa
    results = evaluator.full_evaluation(num_games=500)
    
    # Gera os gráficos
    print(f"\n{'='*80}")
    print("GERANDO GRÁFICOS")
    print(f"{'='*80}\n")
    
    output_dir = '../data/'
    
    evaluator.generate_heatmap(results, os.path.join(output_dir, 'heatmap_winrate.png'))
    evaluator.generate_radar_chart(results, os.path.join(output_dir, 'radar_performance.png'))
    evaluator.generate_bar_chart(results, os.path.join(output_dir, 'bar_comparison.png'))
    evaluator.generate_training_progress(history_file, os.path.join(output_dir, 'training_progress.png'))
    
    # Salva resultados em JSON
    results_file = os.path.join(output_dir, 'evaluation_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Resultados salvos em: {results_file}")
    
    print(f"\n{'='*80}")
    print("AVALIAÇÃO CONCLUÍDA")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
