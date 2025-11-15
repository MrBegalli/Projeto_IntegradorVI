"""
Carregador de baralho a partir de arquivo JSON.
"""

import json
import random
import re
from typing import List, Dict, Any


def load_deck_from_json(file_path: str, shuffle_deck: bool = True) -> List[Dict[str, Any]]:
    """
    Carrega o baralho de cartas a partir de um arquivo JSON.
    
    Args:
        file_path: Caminho para o arquivo JSON
        shuffle_deck: Se True, embaralha o deck após carregar
    
    Returns:
        Lista de cartas (dicionários)
    
    Raises:
        FileNotFoundError: Se o arquivo não existir
        json.JSONDecodeError: Se o JSON for inválido
        ValueError: Se os dados do baralho forem inválidos
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            deck = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de baralho não encontrado: {file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Erro ao decodificar JSON: {e}", e.doc, e.pos)
    
    if not isinstance(deck, list):
        raise ValueError("O arquivo JSON deve conter uma lista de cartas")
    
    if len(deck) == 0:
        raise ValueError("O baralho está vazio")
    
    # Processa e valida cada carta
    processed_deck = []
    for i, card in enumerate(deck):
        if not isinstance(card, dict):
            raise ValueError(f"Carta {i} não é um dicionário válido")
        
        # Cria uma cópia para não modificar o original
        processed_card = card.copy()
        
        # Converte atributos numéricos com strings para float
        if "0-100" in processed_card:
            processed_card["0-100"] = parse_numeric_value(
                processed_card["0-100"], 
                remove_patterns=["s", "seg", "seconds"]
            )
        
        if "top_speed" in processed_card:
            processed_card["top_speed"] = parse_numeric_value(
                processed_card["top_speed"],
                remove_patterns=["km/h", "kmh", "km", "mph"]
            )
        
        # Garante que HP, torque e weight sejam numéricos
        for attr in ["HP", "torque", "weight"]:
            if attr in processed_card:
                processed_card[attr] = parse_numeric_value(processed_card[attr])
        
        # Valida que a carta tem ID e nome
        if "id" not in processed_card:
            raise ValueError(f"Carta {i} não possui campo 'id'")
        if "name" not in processed_card:
            raise ValueError(f"Carta {i} não possui campo 'name'")
        
        processed_deck.append(processed_card)
    
    # Embaralha se solicitado
    if shuffle_deck:
        random.shuffle(processed_deck)
    
    return processed_deck


def parse_numeric_value(value: Any, remove_patterns: List[str] = None) -> float:
    """
    Converte um valor para float, removendo padrões de texto.
    
    Args:
        value: Valor a ser convertido (pode ser str, int, float)
        remove_patterns: Lista de padrões de texto a serem removidos
    
    Returns:
        Valor numérico (float)
    
    Raises:
        ValueError: Se não for possível converter para número
    """
    if isinstance(value, (int, float)):
        return float(value)
    
    if not isinstance(value, str):
        raise ValueError(f"Valor inválido: {value} (tipo: {type(value)})")
    
    # Remove espaços e converte para lowercase
    cleaned = value.strip().lower()
    
    # Remove padrões especificados
    if remove_patterns:
        for pattern in remove_patterns:
            cleaned = cleaned.replace(pattern.lower(), "")
    
    # Remove espaços extras
    cleaned = cleaned.strip()
    
    # Substitui vírgula por ponto (formato brasileiro)
    cleaned = cleaned.replace(",", ".")
    
    # Remove caracteres não numéricos (exceto ponto e sinal negativo)
    cleaned = re.sub(r'[^\d.-]', '', cleaned)
    
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(f"Não foi possível converter '{value}' para número")


def validate_deck(deck: List[Dict[str, Any]]) -> bool:
    """
    Valida se um baralho possui todas as cartas com atributos necessários.
    
    Args:
        deck: Lista de cartas
    
    Returns:
        True se válido
    
    Raises:
        ValueError: Se o baralho for inválido
    """
    required_fields = ["id", "name"]
    recommended_fields = ["HP", "torque", "weight", "0-100", "top_speed"]
    
    for i, card in enumerate(deck):
        # Verifica campos obrigatórios
        for field in required_fields:
            if field not in card:
                raise ValueError(f"Carta {i} ({card.get('name', 'sem nome')}) não possui campo obrigatório: {field}")
        
        # Avisa sobre campos recomendados faltantes
        missing_recommended = [f for f in recommended_fields if f not in card]
        if missing_recommended:
            print(f"Aviso: Carta {card['name']} não possui campos: {', '.join(missing_recommended)}")
    
    return True
