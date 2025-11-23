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

# Arquivo auxiliar para constantes e funções de rede neural
import torch
import torch.nn as nn
import torch.nn.functional as F

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