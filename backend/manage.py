#!/usr/bin/env python3
"""
Script de Gerenciamento do Super Trunfo
========================================

Facilita tarefas comuns como treinar o bot, executar o servidor, e avaliar modelos.

Uso:
    python manage.py [comando] [opções]

Comandos:
    train       - Treina o DQN Bot
    serve       - Inicia o servidor da API
    evaluate    - Avalia o desempenho do modelo treinado
    clean       - Limpa arquivos temporários e logs antigos
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path


def train_bot(args):
    """Executa o treinamento do DQN Bot."""
    print("🚀 Iniciando treinamento do DQN Bot...\n")
    
    cmd = [
        sys.executable,
        "rl_training/train_dqn.py",
        "--episodes", str(args.episodes),
        "--eval-interval", str(args.eval_interval),
        "--save-interval", str(args.save_interval)
    ]
    
    if args.model:
        cmd.extend(["--model", args.model])
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Treinamento concluído!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro durante o treinamento: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Treinamento interrompido pelo usuário")
        sys.exit(0)


def serve_api(args):
    """Inicia o servidor da API."""
    print("🌐 Iniciando servidor da API...\n")
    
    cmd = [
        sys.executable,
        "-m", "uvicorn",
        "app.main:app",
        "--host", args.host,
        "--port", str(args.port)
    ]
    
    if args.reload:
        cmd.append("--reload")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Servidor encerrado")
        sys.exit(0)


def evaluate_model(args):
    """Avalia o desempenho do modelo treinado."""
    print("📊 Avaliando modelo DQN...\n")
    
    # Importa módulos necessários
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        import json
        from app.utils import STATS
        from bots.rl_bot import RLBot
        from bots.weighted_bot import WeightedBot
        from bots.mcts_bot import MCTSBot
        import copy
        import random
        
        # Carrega cartas
        with open('data/carros.json', 'r', encoding='utf-8') as f:
            cards = json.load(f)
        
        # Normaliza valores
        for card in cards:
            if isinstance(card.get('0-100'), str):
                card['0-100'] = float(card['0-100'].replace('s', ''))
            if isinstance(card.get('top_speed'), str):
                card['top_speed'] = float(card['top_speed'].replace(' km/h', ''))
        
        # Carrega modelo
        model_path = args.model or 'data/dqn_model.pth'
        
        if not os.path.exists(model_path):
            print(f"❌ Modelo não encontrado: {model_path}")
            print("   Execute o treinamento primeiro: python manage.py train")
            sys.exit(1)
        
        dqn_bot = RLBot(deck=[], stats_list=STATS, qfile=model_path, epsilon=0.0)
        
        # Função para simular jogo
        def play_game(bot1, bot2, cards):
            shuffled = random.sample(cards, len(cards))
            deck1 = shuffled[:5]
            deck2 = shuffled[5:10]
            
            bot1.deck = copy.deepcopy(deck1)
            bot2.deck = copy.deepcopy(deck2)
            
            bot1_wins = 0
            bot2_wins = 0
            rounds = 0
            current_player = random.choice([1, 2])
            
            while bot1.deck and bot2.deck and rounds < 50:
                rounds += 1
                
                if current_player == 1:
                    card1, stat = bot1.choose_move(bot1.deck, STATS)
                    card2 = bot2.choose_card(bot2.deck, stat)
                else:
                    card2, stat = bot2.choose_move(bot2.deck, STATS)
                    card1 = bot1.choose_card(bot1.deck, stat)
                
                if card1 is None or card2 is None:
                    break
                
                from app.utils import evaluate
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
        
        # Avalia contra cada oponente
        opponents = {
            'Facil_Bot': WeightedBot(deck=[]),
            'Medio_Bot': MCTSBot(deck=[], simulations=50)
        }
        
        print(f"Modelo: {model_path}")
        print(f"Número de jogos por oponente: {args.games}\n")
        print("="*60)
        
        for opp_name, opp_bot in opponents.items():
            wins = 0
            draws = 0
            
            print(f"\nAvaliando contra {opp_name}...")
            
            for i in range(args.games):
                if (i + 1) % 10 == 0:
                    print(f"  Progresso: {i+1}/{args.games} jogos")
                
                result = play_game(dqn_bot, opp_bot, cards)
                if result == 1:
                    wins += 1
                elif result == 0:
                    draws += 1
            
            win_rate = wins / args.games
            draw_rate = draws / args.games
            loss_rate = 1 - win_rate - draw_rate
            
            print(f"\n  Resultados vs {opp_name}:")
            print(f"    Vitórias: {wins}/{args.games} ({win_rate*100:.1f}%)")
            print(f"    Empates:  {draws}/{args.games} ({draw_rate*100:.1f}%)")
            print(f"    Derrotas: {args.games - wins - draws}/{args.games} ({loss_rate*100:.1f}%)")
        
        print("\n" + "="*60)
        print("✅ Avaliação concluída!")
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("   Certifique-se de que todas as dependências estão instaladas")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro durante avaliação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def clean_files(args):
    """Limpa arquivos temporários e logs antigos."""
    print("🧹 Limpando arquivos temporários...\n")
    
    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.log" if args.logs else None,
    ]
    
    patterns = [p for p in patterns if p is not None]
    
    removed_count = 0
    
    for pattern in patterns:
        for path in Path(".").glob(pattern):
            if path.is_file():
                path.unlink()
                removed_count += 1
                print(f"  Removido: {path}")
            elif path.is_dir():
                import shutil
                shutil.rmtree(path)
                removed_count += 1
                print(f"  Removido: {path}/")
    
    print(f"\n✅ {removed_count} arquivo(s)/diretório(s) removido(s)")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Script de gerenciamento do Super Trunfo",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a executar')
    
    # Comando: train
    train_parser = subparsers.add_parser('train', help='Treina o DQN Bot')
    train_parser.add_argument('--episodes', type=int, default=50000, help='Número de episódios')
    train_parser.add_argument('--eval-interval', type=int, default=1000, help='Intervalo de avaliação')
    train_parser.add_argument('--save-interval', type=int, default=5000, help='Intervalo de salvamento')
    train_parser.add_argument('--model', type=str, help='Modelo pré-treinado para continuar')
    
    # Comando: serve
    serve_parser = subparsers.add_parser('serve', help='Inicia o servidor da API')
    serve_parser.add_argument('--host', type=str, default='0.0.0.0', help='Host do servidor')
    serve_parser.add_argument('--port', type=int, default=8000, help='Porta do servidor')
    serve_parser.add_argument('--reload', action='store_true', help='Auto-reload em desenvolvimento')
    
    # Comando: evaluate
    eval_parser = subparsers.add_parser('evaluate', help='Avalia o modelo treinado')
    eval_parser.add_argument('--model', type=str, help='Caminho do modelo (padrão: data/dqn_model.pth)')
    eval_parser.add_argument('--games', type=int, default=100, help='Número de jogos por oponente')
    
    # Comando: clean
    clean_parser = subparsers.add_parser('clean', help='Limpa arquivos temporários')
    clean_parser.add_argument('--logs', action='store_true', help='Remove também os logs')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Executa comando
    if args.command == 'train':
        train_bot(args)
    elif args.command == 'serve':
        serve_api(args)
    elif args.command == 'evaluate':
        evaluate_model(args)
    elif args.command == 'clean':
        clean_files(args)


if __name__ == "__main__":
    main()
