"""
Funções auxiliares para o jogo Super Trunfo.
"""

# Estatísticas disponíveis no baralho
STATS = ["HP", "torque", "weight", "0-100", "top_speed"]

# Mapeamento de nomes amigáveis para exibição
STATS_DISPLAY = {
    "HP": "Potência (HP)",
    "torque": "Torque (Nm)",
    "weight": "Peso (kg)",
    "0-100": "0-100 km/h (s)",
    "top_speed": "Velocidade Máxima (km/h)"
}


def evaluate(card1, card2, stat):
    """
    Compara duas cartas em um atributo específico.
    
    Args:
        card1: Primeira carta (dict)
        card2: Segunda carta (dict)
        stat: Atributo a ser comparado (str)
    
    Returns:
        1 se card1 vence, -1 se card2 vence, 0 se empate
    """
    value1 = card1.get(stat, 0)
    value2 = card2.get(stat, 0)
    
    # Para peso e aceleração, menor é melhor
    # Evita divisão por zero
    if stat in ["weight", "0-100"]:
        if value1 == 0 and value2 == 0:
            return 0
        elif value1 == 0:
            return -1  # card1 tem valor inválido, card2 vence
        elif value2 == 0:
            return 1   # card2 tem valor inválido, card1 vence
        
        # Inverte a comparação (menor é melhor)
        value1 = 1 / value1
        value2 = 1 / value2
    
    if value1 > value2:
        return 1
    elif value1 < value2:
        return -1
    else:
        return 0


def calculate_card_score(card):
    """
    Calcula um score geral para uma carta baseado em todos os atributos.
    Usado para ordenação e heurísticas.
    
    Args:
        card: Carta (dict)
    
    Returns:
        Score numérico (float)
    """
    score = 0
    for stat in STATS:
        value = card.get(stat, 0)
        if value == 0:
            continue
            
        # Para peso e aceleração, menor é melhor
        if stat in ["weight", "0-100"]:
            value = 1 / value
        
        score += value
    
    return score / len(STATS) if STATS else 0


def get_best_attribute_for_card(card, opponent_card=None):
    """
    Determina o melhor atributo para jogar com uma carta específica.
    Se opponent_card for fornecido, considera a comparação.
    
    Args:
        card: Carta do jogador (dict)
        opponent_card: Carta do oponente (dict, opcional)
    
    Returns:
        Nome do melhor atributo (str)
    """
    if opponent_card:
        # Encontra o atributo onde a diferença é maior
        best_stat = None
        best_advantage = -float('inf')
        
        for stat in STATS:
            result = evaluate(card, opponent_card, stat)
            if result > best_advantage:
                best_advantage = result
                best_stat = stat
        
        return best_stat if best_stat else STATS[0]
    else:
        # Retorna o atributo com maior valor normalizado
        best_stat = None
        best_value = -float('inf')
        
        for stat in STATS:
            value = card.get(stat, 0)
            if value == 0:
                continue
                
            # Normaliza valores
            if stat in ["weight", "0-100"]:
                value = 1 / value
            
            if value > best_value:
                best_value = value
                best_stat = stat
        
        return best_stat if best_stat else STATS[0]
