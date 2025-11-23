import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import random
from collections import deque
import os

# Ajuste conforme seu jogo: 12 cartas por jogador, 7 atributos por carta
STATS_COUNT = 7      # número de atributos por carta (ex: HP, torque, 0-100, top_speed, ...)
ACTION_SIZE = 12     # máximo de cartas na mão que a rede considera (e também número de ações)
STATE_SIZE = ACTION_SIZE * STATS_COUNT  # 12 * 7 = 84 (somente cartas)
STATE_INPUT_SIZE = STATE_SIZE + STATS_COUNT  # + one-hot do atributo = 84 + 7 = 91


class QNetwork(nn.Module):
    """
    Rede neural que recebe o vetor de estado e retorna Q-values para cada ação.
    state_size deve ser STATE_INPUT_SIZE (fixo).
    """
    def __init__(self, state_size=STATE_INPUT_SIZE, action_size=ACTION_SIZE):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_size)

    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


class RLBot:
    """
    Bot DQN para Super Trunfo com estado fixo baseado em ACTION_SIZE cartas.
    - Sempre constrói um vetor de tamanho fixo STATE_INPUT_SIZE (91 no seu caso)
    - step() armazena transições; learn() atualiza redes
    """
    def __init__(self, deck, stats_list, qfile=None, epsilon=1.0, alpha=0.0005, gamma=0.99):
        self.deck = deck or []
        self.stats_list = stats_list
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.action_size = ACTION_SIZE
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # checagem de consistência
        if len(self.stats_list) != STATS_COUNT:
            # não faz crash, apenas alerta; mas a rede foi definida para STATS_COUNT
            print(f"[RLBot] Atenção: stats_list length ({len(self.stats_list)}) != STATS_COUNT ({STATS_COUNT}).")

        # redes
        self.qnetwork_local = QNetwork(state_size=STATE_INPUT_SIZE, action_size=self.action_size).to(self.device)
        self.qnetwork_target = QNetwork(state_size=STATE_INPUT_SIZE, action_size=self.action_size).to(self.device)
        self.optimizer = optim.Adam(self.qnetwork_local.parameters(), lr=self.alpha)

        # carrega pesos se existir
        if qfile and os.path.exists(qfile):
            self.load_q(qfile)

        # inicializa target
        self.qnetwork_target.load_state_dict(self.qnetwork_local.state_dict())

        # replay buffer
        self.memory = deque(maxlen=20000)
        self.batch_size = 64
        self.update_every = 4  # passos entre updates
        self._step_count = 0

    def _get_card_features(self, card):
        """
        Converte carta -> vetor de features (ordem definida por self.stats_list).
        Deve sempre retornar STATS_COUNT floats.
        """
        features = []
        for stat in self.stats_list:
            val = card.get(stat, 0)
            try:
                val = float(val)
            except Exception:
                # se o valor for não-numérico, use 0
                val = 0.0

            # normalização especial para stats onde menor é melhor
            if stat in ["weight", "0-100"]:
                val = 1.0 / (val + 1e-6)

            features.append(val)
        # garante o tamanho
        if len(features) < STATS_COUNT:
            features += [0.0] * (STATS_COUNT - len(features))
        elif len(features) > STATS_COUNT:
            features = features[:STATS_COUNT]
        return features

    def get_state_vector(self, deck=None, stat=None):
        """
        Constrói o vetor de estado fixo com exatamente:
          ACTION_SIZE * STATS_COUNT (cartas) + STATS_COUNT (one-hot stat)
        - limita o deck às primeiras ACTION_SIZE cartas
        - completa com zeros caso haja menos cartas
        - retorna tensor float32 no device com shape (STATE_INPUT_SIZE,)
        """
        if deck is None:
            deck = self.deck or []

        # limita a ACTION_SIZE cartas (pega as primeiras)
        limited_deck = deck[:ACTION_SIZE]

        card_vectors = []
        for card in limited_deck:
            card_vectors.extend(self._get_card_features(card))

        # completa com zeros até ACTION_SIZE * STATS_COUNT
        expected_card_len = ACTION_SIZE * STATS_COUNT
        if len(card_vectors) < expected_card_len:
            card_vectors.extend([0.0] * (expected_card_len - len(card_vectors)))
        elif len(card_vectors) > expected_card_len:
            # corte por segurança (não deveria acontecer porque limitamos o deck)
            card_vectors = card_vectors[:expected_card_len]

        # one-hot para o stat (STATS_COUNT)
        stat_vector = [0.0] * STATS_COUNT
        if stat and stat in self.stats_list:
            idx = self.stats_list.index(stat)
            stat_vector[idx] = 1.0

        state_vector = np.array(card_vectors + stat_vector, dtype=np.float32)

        # segurança — garante tamanho esperado
        assert state_vector.shape[0] == STATE_INPUT_SIZE, \
            f"Estado tem tamanho {state_vector.shape[0]} mas esperado {STATE_INPUT_SIZE}"

        return torch.from_numpy(state_vector).to(self.device)

    def choose_action(self, stat):
        """
        Epsilon-greedy. Retorna (card_dict, action_index).
        Se a mão atual tiver menos de ACTION_SIZE cartas, action_index < len(deck).
        """
        if not self.deck:
            return None, -1

        state = self.get_state_vector(self.deck, stat).unsqueeze(0)  # shape (1, STATE_INPUT_SIZE)

        # exploração
        if random.random() < self.epsilon:
            idx = random.randrange(min(len(self.deck), ACTION_SIZE))
            return self.deck[idx], idx

        # explotação
        self.qnetwork_local.eval()
        with torch.no_grad():
            qvals = self.qnetwork_local(state).cpu().numpy().flatten()
        self.qnetwork_local.train()

        # máscara para ações inválidas (cartas que não existem na mão)
        valid = min(len(self.deck), ACTION_SIZE)
        masked = qvals.copy()
        for i in range(valid, ACTION_SIZE):
            masked[i] = -float("inf")

        action_index = int(np.argmax(masked))
        # se action_index >= len(deck) (por segurança), escolhe último válido
        if action_index >= len(self.deck):
            action_index = len(self.deck) - 1

        return self.deck[action_index], action_index

    def choose_card(self, player_deck, chosen_stat):
        card, _ = self.choose_action(chosen_stat)
        return card

    def choose_move(self, player_deck, stats_list):
        """
        Escolhe atributo (stat) e carta.
        Retorna (card_dict, stat).
        """
        if not self.deck:
            return None, None

        # escolha aleatória do stat com epsilon
        if random.random() < self.epsilon:
            stat = random.choice(stats_list)
            card, _ = self.choose_action(stat)
            return card, stat

        best_q = -float("inf")
        best_stat = None

        for stat in stats_list:
            state = self.get_state_vector(self.deck, stat).unsqueeze(0)
            with torch.no_grad():
                qvals = self.qnetwork_local(state).cpu().numpy().flatten()

            # máscara para cartas ausentes
            valid = min(len(self.deck), ACTION_SIZE)
            for i in range(valid, ACTION_SIZE):
                qvals[i] = -float("inf")

            qmax = float(np.max(qvals))
            if qmax > best_q:
                best_q = qmax
                best_stat = stat

        card, _ = self.choose_action(best_stat)
        return card, best_stat

    def step(self, state, action, reward, next_state, done):
        """
        Armazena transição e chama learn periodicamente.
        state/next_state devem ser tensores (produzidos por get_state_vector).
        action: índice inteiro da carta jogada.
        """
        # garante int
        try:
            action = int(action)
        except Exception:
            if isinstance(action, torch.Tensor):
                action = int(action.item())
            else:
                action = int(action)

        self.memory.append((state, action, float(reward), next_state, float(done)))
        self._step_count += 1

        # aprende a cada update_every passos se tiver batch suficiente
        if len(self.memory) >= self.batch_size and (self._step_count % self.update_every) == 0:
            return self.learn()
        return None

    def learn(self):
        """Amostra batch e atualiza redes."""
        if len(self.memory) < self.batch_size:
            return None

        batch = random.sample(self.memory, self.batch_size)

        states = torch.stack([e[0] for e in batch]).float().to(self.device)            # (B, STATE_INPUT_SIZE)
        actions = torch.tensor([e[1] for e in batch], dtype=torch.long).unsqueeze(1).to(self.device)  # (B,1)
        rewards = torch.tensor([e[2] for e in batch], dtype=torch.float32).unsqueeze(1).to(self.device) # (B,1)
        next_states = torch.stack([e[3] for e in batch]).float().to(self.device)       # (B, STATE_INPUT_SIZE)
        dones = torch.tensor([e[4] for e in batch], dtype=torch.float32).unsqueeze(1).to(self.device)   # (B,1)

        # Q-target
        with torch.no_grad():
            Q_next = self.qnetwork_target(next_states).max(1)[0].unsqueeze(1)

        Q_target = rewards + (self.gamma * Q_next * (1 - dones))

        # Q-expected
        Q_expected = self.qnetwork_local(states).gather(1, actions)

        loss = F.mse_loss(Q_expected, Q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # soft update
        self._soft_update(self.qnetwork_local, self.qnetwork_target, tau=1e-3)

        return loss.item()

    def _soft_update(self, local_model, target_model, tau):
        for target_param, local_param in zip(target_model.parameters(), local_model.parameters()):
            target_param.data.copy_(tau * local_param.data + (1.0 - tau) * target_param.data)

    def save_q(self, qfile):
        # garante diretório
        parent = os.path.dirname(qfile)
        if parent:
            os.makedirs(parent, exist_ok=True)
        torch.save(self.qnetwork_local.state_dict(), qfile)
        print(f"[RLBot] Pesos da rede salvos em {qfile}")

    def load_q(self, qfile):
        try:
            self.qnetwork_local.load_state_dict(torch.load(qfile, map_location=self.device))
            self.qnetwork_target.load_state_dict(self.qnetwork_local.state_dict())
            print(f"[RLBot] Pesos da rede carregados de {qfile}")
        except Exception as e:
            print(f"[RLBot] Erro ao carregar pesos de {qfile}: {e}")

    def update_epsilon(self, new_epsilon):
        self.epsilon = float(new_epsilon)

    def update_alpha(self, new_alpha):
        self.alpha = float(new_alpha)
        self.optimizer = optim.Adam(self.qnetwork_local.parameters(), lr=self.alpha)
