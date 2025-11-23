import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import random
from collections import deque
import os

# Constantes
STATE_SIZE = 5 * 7  # 5 cartas * 7 atributos por carta (ex: HP, 0-100, etc.)
ACTION_SIZE = 5     # 5 cartas possíveis para jogar
STATS_COUNT = 7     # Número de atributos possíveis

class QNetwork(nn.Module):
    """
    Rede Neural para o Q-Learning (DQN).
    Recebe o estado (cartas na mão + atributo da rodada) e retorna Q-valores para cada ação (carta).
    """
    def __init__(self, state_size=STATE_SIZE + STATS_COUNT, action_size=ACTION_SIZE):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_size)

    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

class RLBotDQN:
    """
    Bot de Reinforcement Learning baseado em Deep Q-Network (DQN).
    Substitui o Q-Learning baseado em tabela.
    """
    def __init__(self, deck, stats_list, qfile=None, epsilon=1.0, alpha=0.0005, gamma=0.99):
        self.deck = deck
        self.stats_list = stats_list
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.action_size = ACTION_SIZE
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Rede Principal e Rede Alvo
        self.qnetwork_local = QNetwork().to(self.device)
        self.qnetwork_target = QNetwork().to(self.device)
        self.optimizer = optim.Adam(self.qnetwork_local.parameters(), lr=self.alpha)
        
        # Carrega pesos se qfile for fornecido
        if qfile and os.path.exists(qfile):
            self.load_q(qfile)
        
        # Sincroniza pesos
        self.qnetwork_target.load_state_dict(self.qnetwork_local.state_dict())
        
        # Buffer de Replay (para treinamento estável)
        self.memory = deque(maxlen=10000)
        self.batch_size = 64
        self.update_every = 4 # Atualiza a rede alvo a cada 4 passos

    def _get_card_features(self, card):
        """Converte uma carta em um vetor de atributos numéricos."""
        features = []
        for stat in self.stats_list:
            # Normalização simples (assumindo que os valores são positivos)
            val = card.get(stat, 0)
            if stat in ["weight", "0-100"]:
                # Para stats onde menor é melhor, inverte o valor
                val = 1.0 / (val + 1e-6)
            features.append(val)
        return features

    def get_state_vector(self, deck=None, stat=None):
        """
        Converte o estado (deck na mão + atributo da rodada) em um vetor de entrada para a rede.
        O estado é um vetor concatenado de 5 cartas (7 atributos cada) + 7 one-hot para o stat.
        """
        if deck is None:
            deck = self.deck
        
        # 1. Vetor de Cartas (5 * 7)
        card_vectors = []
        for card in deck:
            card_vectors.extend(self._get_card_features(card))
        
        # Preenche com zeros se houver menos de 5 cartas
        while len(card_vectors) < 5 * STATS_COUNT:
            card_vectors.append(0.0)
            
        # 2. Vetor One-Hot do Atributo (7)
        stat_vector = [0.0] * STATS_COUNT
        if stat and stat in self.stats_list:
            stat_index = self.stats_list.index(stat)
            stat_vector[stat_index] = 1.0
            
        state_vector = card_vectors + stat_vector
        return torch.from_numpy(np.array(state_vector, dtype=np.float32)).to(self.device)

    def choose_action(self, stat):
        """
        Escolhe uma carta usando política epsilon-greedy.
        Retorna a carta escolhida (dict) e o índice da ação (0-4).
        """
        if not self.deck:
            return None, -1
        
        state = self.get_state_vector(self.deck, stat).unsqueeze(0)
        
        # Exploração: escolhe carta aleatória
        if random.random() < self.epsilon:
            action_index = random.randrange(len(self.deck))
            chosen_card = self.deck[action_index]
            return chosen_card, action_index
        
        # Explotação: escolhe carta com maior Q-valor
        self.qnetwork_local.eval()
        with torch.no_grad():
            action_values = self.qnetwork_local(state).cpu().data.numpy().flatten()
        self.qnetwork_local.train()
        
        # Máscara para ações inválidas (cartas que não estão na mão)
        valid_indices = list(range(len(self.deck)))
        
        # Define Q-valores de ações inválidas para -infinito
        masked_action_values = action_values.copy()
        invalid_indices = [i for i in range(self.action_size) if i not in valid_indices]
        masked_action_values[invalid_indices] = -float('inf')
        
        action_index = np.argmax(masked_action_values)
        chosen_card = self.deck[action_index]
        
        return chosen_card, action_index

    def choose_card(self, player_deck, chosen_stat):
        """Interface compatível com outros bots."""
        card, _ = self.choose_action(chosen_stat)
        return card
    
    def choose_move(self, player_deck, stats_list):
        """
        Escolhe a melhor carta e atributo para jogar.
        """
        if not self.deck:
            return None, None
        
        best_card = None
        best_stat = None
        best_q = -float('inf')
        
        # Exploração para a escolha do atributo
        if random.random() < self.epsilon:
            best_stat = random.choice(stats_list)
            best_card, _ = self.choose_action(best_stat)
            return best_card, best_stat
        
        # Explotação
        for stat in stats_list:
            state = self.get_state_vector(self.deck, stat).unsqueeze(0)
            self.qnetwork_local.eval()
            with torch.no_grad():
                action_values = self.qnetwork_local(state).cpu().data.numpy().flatten()
            self.qnetwork_local.train()
            
            valid_indices = list(range(len(self.deck)))
            masked_action_values = action_values.copy()
            invalid_indices = [i for i in range(self.action_size) if i not in valid_indices]
            masked_action_values[invalid_indices] = -float('inf')
            
            max_q_for_stat = np.max(masked_action_values)
            
            if max_q_for_stat > best_q:
                best_q = max_q_for_stat
                best_stat = stat
        
        # Escolhe a melhor carta para o melhor atributo encontrado
        best_card, _ = self.choose_action(best_stat)
        
        return best_card, best_stat

    def step(self, state, action, reward, next_state, done):
        """Salva a experiência no buffer de replay."""
        self.memory.append((state, action, reward, next_state, done))
        
        # Aprende a cada `update_every` passos
        if len(self.memory) > self.batch_size and len(self.memory) % self.update_every == 0:
            return self.learn()
        return None

    def learn(self):
        """Aprende usando um lote de experiências do buffer de replay."""
        experiences = random.sample(self.memory, k=self.batch_size)
        
        # Converte para tensores
        states = torch.stack([e[0] for e in experiences]).to(self.device)
        actions = torch.from_numpy(np.vstack([e[1] for e in experiences])).to(self.device)
        rewards = torch.from_numpy(np.vstack([e[2] for e in experiences])).float().to(self.device)
        next_states = torch.stack([e[3] for e in experiences]).to(self.device)
        dones = torch.from_numpy(np.vstack([e[4] for e in experiences]).astype(np.uint8)).float().to(self.device)

        # 1. Calcula Q-targets (valor esperado)
        # Q-valores do próximo estado usando a rede alvo
        Q_targets_next = self.qnetwork_target(next_states).detach().max(1)[0].unsqueeze(1)
        # Q-targets = R + gamma * max(Q(s', a')) * (1 - done)
        Q_targets = rewards + (self.gamma * Q_targets_next * (1 - dones))

        # 2. Calcula Q-values (valor atual)
        # Q-valores do estado atual usando a rede local
        Q_expected = self.qnetwork_local(states).gather(1, actions)

        # 3. Calcula a perda (Loss)
        loss = F.mse_loss(Q_expected, Q_targets)

        # 4. Otimiza
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # 5. Atualiza a rede alvo (soft update)
        self._soft_update(self.qnetwork_local, self.qnetwork_target, tau=1e-3)
        
        return loss.item()

    def _soft_update(self, local_model, target_model, tau):
        """Soft update model parameters.
        θ_target = τ*θ_local + (1 - τ)*θ_target
        """
        for target_param, local_param in zip(target_model.parameters(), local_model.parameters()):
            target_param.data.copy_(tau*local_param.data + (1.0-tau)*target_param.data)

    def save_q(self, qfile):
        """Salva os pesos da rede neural."""
        torch.save(self.qnetwork_local.state_dict(), qfile)
        print(f"[RLBotDQN] Pesos da rede salvos em {qfile}")

    def load_q(self, qfile):
        """Carrega os pesos da rede neural."""
        try:
            self.qnetwork_local.load_state_dict(torch.load(qfile, map_location=self.device))
            self.qnetwork_target.load_state_dict(self.qnetwork_local.state_dict())
            print(f"[RLBotDQN] Pesos da rede carregados de {qfile}")
        except Exception as e:
            print(f"[RLBotDQN] Erro ao carregar pesos de {qfile}: {e}")
            
    def update_epsilon(self, new_epsilon):
        """Atualiza a taxa de exploração."""
        self.epsilon = new_epsilon
        
    def update_alpha(self, new_alpha):
        """Atualiza a taxa de aprendizado."""
        self.alpha = new_alpha
        self.optimizer = optim.Adam(self.qnetwork_local.parameters(), lr=self.alpha)
