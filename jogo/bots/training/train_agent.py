import random
import json
import os
from collections import defaultdict
import sys
import time

# Adiciona o diretório raiz do projeto ao path para importar corretamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from deck_loader import load_deck_from_json
from utils import stats, evaluate
from bots.rl_bot import RLBot
# Importa WeightedBot para usar como oponente
from bots.weighted_bot import WeightedBot 

# --- Ambiente de Jogo para Treinamento (CardGameEnv) ---

class CardGameEnv:
    """
    Ambiente do Jogo de Cartas para Reinforcement Learning.
    O agente (Bot) joga contra um oponente fixo (WeightedBot).
    """
    def __init__(self, full_deck):
        self.full_deck = full_deck
        self.stats = stats
        
        # Para garantir que as cartas tenham um ID único, mesmo que o JSON não tenha
        # Assumindo que load_deck_from_json já fez a limpeza e conversão.
        # Vamos garantir que todas as cartas tenham um 'id'.
        for i, card in enumerate(self.full_deck):
            if 'id' not in card:
                card['id'] = i + 1
        
        self.full_deck_map = {card['id']: card for card in self.full_deck}
        self.bot_deck = []
        self.opponent_deck = []
        self.opponent_bot = WeightedBot(deck=[]) # O deck será atualizado no reset

    def reset(self):
        """Reinicia o jogo para um novo episódio."""
        random.shuffle(self.full_deck)
        half = len(self.full_deck) // 2
        self.bot_deck = self.full_deck[:half]
        self.opponent_deck = self.full_deck[half:]
        
        # Atualiza o deck do oponente
        self.opponent_bot.deck = self.opponent_deck
        
        # O estado inicial é a mão do bot e o stat da primeira rodada (escolhido pelo oponente)
        initial_stat = self._opponent_choose_stat()
        
        return self._get_state(self.bot_deck), initial_stat

    def _get_state(self, deck):
        """Retorna o estado atual (tupla de IDs das cartas na mão do bot)."""
        return tuple(sorted([c['id'] for c in deck]))

    def _get_reward(self, result):
        """Calcula a recompensa para o Bot."""
        # result: 1 (Bot vence), -1 (Oponente vence), 0 (Empate)
        return result

    def _opponent_choose_stat(self):
        """Oponente escolhe o stat para a rodada (aleatório para simplificar o treinamento)."""
        return random.choice(self.stats)

    def step(self, bot_card_id, stat):
        """
        Executa um passo no ambiente.
        bot_card_id: ID da carta escolhida pelo Bot (ação)
        stat: Atributo escolhido pelo oponente
        """
        
        # 1. Ação do Bot
        bot_card = self.full_deck_map[bot_card_id]
        
        # Remove a carta da mão do Bot
        self.bot_deck = [c for c in self.bot_deck if c['id'] != bot_card_id]

        # 2. Ação do Oponente
        # O oponente usa a estratégia WeightedBot para escolher a carta
        opponent_card = self.opponent_bot.choose_card(self.bot_deck, stat)
        
        # Remove a carta da mão do Oponente
        self.opponent_deck = [c for c in self.opponent_deck if c['id'] != opponent_card['id']]
        self.opponent_bot.deck = self.opponent_deck # Atualiza o deck do oponente

        # 3. Determinar o vencedor da rodada
        # result: 1 (Bot vence), -1 (Oponente vence), 0 (Empate)
        result = evaluate(bot_card, opponent_card, stat)

        # 4. Calcular Recompensa
        reward = self._get_reward(result)

        # 5. Verificar se o jogo acabou
        done = not self.bot_deck or not self.opponent_deck
        
        # 6. Próximo estado e próximo stat
        new_state = self._get_state(self.bot_deck)
        
        if not done:
            # O oponente escolhe o stat para a próxima rodada
            next_stat = self._opponent_choose_stat()
        else:
            next_stat = None

        # 7. Retornar
        return new_state, reward, done, next_stat, {'bot_card': bot_card, 'opponent_card': opponent_card, 'result': result}

# --- Função de Treinamento ---

def train_rlbot(env, bot, num_episodes=50000, epsilon_decay=0.9999, min_epsilon=0.01):
    """Treina o RLBot no ambiente do jogo."""
    print(f"Iniciando treinamento por {num_episodes} episódios...")
    
    rewards_history = []
    
    for episode in range(num_episodes):
        # O reset retorna o estado inicial e o stat da primeira rodada (escolhido pelo oponente)
        state, stat = env.reset()
        done = False
        total_reward = 0
        
        # Reduzir epsilon para diminuir a exploração ao longo do tempo
        bot.epsilon = max(min_epsilon, bot.epsilon * epsilon_decay)
        
        # O RLBot precisa ter acesso ao deck atual para a função choose_action
        bot.deck = [env.full_deck_map[card_id] for card_id in state]
        
        while not done:
            old_state = state
            old_stat = stat
            
            # 1. Escolher ação (carta)
            chosen_card = bot.choose_action(old_stat)
            action = chosen_card['id']
            
            # 2. Executar ação e observar
            new_state, reward, done, next_stat, info = env.step(action, old_stat)
            
            # 3. Atualizar Q-table
            old_state_stat = (old_state, old_stat)
            bot.update_q(old_state_stat, action, reward, new_state, next_stat)
            
            # 4. Passar para o próximo estado/stat
            state = new_state
            stat = next_stat
            total_reward += reward
            
            # Atualiza o deck do bot para o próximo passo
            bot.deck = [env.full_deck_map[card_id] for card_id in state]
        
        rewards_history.append(total_reward)
        
        if (episode + 1) % 1000 == 0:
            avg_reward = sum(rewards_history[-1000:]) / 1000
            print(f"Episódio {episode + 1}/{num_episodes} | Epsilon: {bot.epsilon:.4f} | Recompensa Média (últimos 1000): {avg_reward:.2f}")
            
        # Salva a Q-table periodicamente
        if (episode + 1) % 10000 == 0:
            Q_FILE_TEMP = "rl_q_table_temp.json"
            bot.save_q(Q_FILE_TEMP)

    print("Treinamento concluído.")
    return rewards_history

# --- Função de Teste ---

def test_rlbot(env, bot, num_games=1000):
    """Testa a performance do RLBot (exploração desativada)."""
    print(f"Iniciando teste por {num_games} jogos...")
    
    original_epsilon = bot.epsilon
    bot.epsilon = 0.0 # Desativa exploração para o teste
    
    win_count = 0
    total_score = 0
    
    for game in range(num_games):
        state, stat = env.reset()
        done = False
        bot_score = 0
        opponent_score = 0
        
        # O RLBot precisa ter acesso ao deck atual para a função choose_action
        bot.deck = [env.full_deck_map[card_id] for card_id in state]
        
        while not done:
            # O bot precisa do deck atualizado para escolher a ação
            bot.deck = [env.full_deck_map[card_id] for card_id in state]
            
            # 1. Escolher ação (carta)
            chosen_card = bot.choose_action(stat)
            action = chosen_card['id']
            
            # 2. Executar ação e observar
            new_state, reward, done, next_stat, info = env.step(action, stat)
            
            state = new_state
            stat = next_stat
            
            if info['result'] == 1:
                bot_score += 1
            elif info['result'] == -1:
                opponent_score += 1
                
        if bot_score > opponent_score:
            win_count += 1
        total_score += bot_score - opponent_score

    win_rate = win_count / num_games
    avg_score_diff = total_score / num_games
    print(f"Teste concluído. Taxa de vitórias (Bot vs WeightedBot): {win_rate * 100:.2f}% ({win_count}/{num_games})")
    print(f"Diferença média de placar (Bot - Oponente): {avg_score_diff:.2f}")
    
    bot.epsilon = original_epsilon # Restaura epsilon
    return win_rate

# --- Execução Principal ---

if __name__ == '__main__':
    # O caminho para o deck.json deve ser fornecido pelo usuário.
    # O usuário precisará fornecer o caminho correto.
    print("--- Treinamento do RLBot (Q-Learning) ---")
    DECK_FILE_PATH = input("Informe o caminho COMPLETO do JSON do deck (ex: /home/ubuntu/jogo/deck.json): ")
    
    if not os.path.exists(DECK_FILE_PATH):
        print(f"Erro: Arquivo de deck não encontrado em {DECK_FILE_PATH}")
        sys.exit(1)
        
    start_time = time.time()
    
    # 1. Configuração
    FULL_DECK = load_deck_from_json(DECK_FILE_PATH)
    
    # Oponente fixo para o treinamento (WeightedBot)
    env = CardGameEnv(FULL_DECK)
    
    # 2. Inicialização do Bot
    # Parâmetros de RL:
    rl_bot = RLBot(deck=env.bot_deck, epsilon=0.9, alpha=0.1, gamma=0.9)
    
    # 3. Treinamento
    NUM_EPISODES = 50000 
    train_rlbot(env, rl_bot, num_episodes=NUM_EPISODES)
    
    # 4. Salvar Q-table
    Q_FILE = os.path.abspath("rl_q_table.json")
    rl_bot.save_q(Q_FILE)
    
    # 5. Teste
    test_rlbot(env, rl_bot, num_games=1000)
    
    end_time = time.time()
    print(f"\nTempo total de execução: {end_time - start_time:.2f} segundos")
    
    # 6. Instruções
    print(f"\nO modelo treinado (Q-table) foi salvo em: {Q_FILE}")
    print("Para usar o bot treinado no jogo principal (`jogo/main.py`), você precisará:")
    print("1. Certificar-se de que `jogo/bots/rl_bot.py` está atualizado.")
    print("2. Mudar a inicialização do RLBot em `jogo/main.py` para carregar a Q-table:")
    print(f"   bot = RLBot(bot_deck, qfile='{Q_FILE}', epsilon=0.0)")