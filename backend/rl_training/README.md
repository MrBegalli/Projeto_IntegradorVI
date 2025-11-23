# Treinamento Contínuo do RL_Bot (Q-Learning)

Este diretório contém os arquivos necessários para continuar o treinamento do bot de Reinforcement Learning (RL_Bot) na sua máquina local.

## 1. Versão Atual do Bot

A Q-table fornecida (`rl_q_table_massive_v2.json`) representa a versão mais eficiente do bot, treinada com mais de **876.000 episódios**, alcançando **57.9% de vitórias** gerais e **51.7% de vitórias** contra o forte Medio_Bot (MCTS).

## 2. Arquivos Essenciais

| Arquivo | Descrição |
|---|---|
| `continuous_retrain.py` | Script Python para executar o treinamento contínuo. |
| `rl_q_table_massive_v2.json` | A Q-table mais atualizada e eficiente. |

## 3. Como Continuar o Treinamento

O treinamento é focado em refinar a estratégia do RL_Bot contra o Medio_Bot.

### Pré-requisitos

1.  **Python 3.x** instalado.
2.  **Bibliotecas:** `numpy` (geralmente já instalada).

### Passos para Execução

1.  **Navegue até o Diretório:**
    ```bash
    cd /caminho/para/Projeto_IntegradorVI-main/backend/rl_training
    ```

2.  **Execute o Script de Treinamento:**
    ```bash
    python3.11 continuous_retrain.py
    ```
    *Nota: Se o seu Python for apenas `python`, use `python continuous_retrain.py`.*

### Detalhes do Script

O script `continuous_retrain.py` está configurado para:
- **Carregar** a Q-table de `rl_q_table_massive_v2.json`.
- **Treinar** contra o `Medio_Bot` (MCTSBot).
- **Salvar** a Q-table atualizada no mesmo arquivo (`rl_q_table_massive_v2.json`) a cada 1.000 episódios.
- **Parar** automaticamente após 30 minutos (ou você pode interromper manualmente com `Ctrl+C`).

### Parâmetros de Treinamento

| Parâmetro | Valor | Descrição |
|---|---|---|
| `qfile_in` / `qfile_out` | `rl_q_table_massive_v2.json` | Arquivo de Q-table. |
| `epsilon` | `0.1` (com decay) | Taxa de exploração (diminui com o tempo). |
| `alpha` | `0.4` | Taxa de aprendizado (quão rápido o bot aceita novas informações). |
| `gamma` | `0.95` | Fator de desconto (importância das recompensas futuras). |

### Dicas para Treinamento Prolongado

- **Aumentar o Tempo:** Para sessões mais longas, edite a linha `self.max_time_s = 1800` no `continuous_retrain.py` para um valor maior em segundos (ex: `3600` para 1 hora).
- **Ajustar Epsilon:** Se o bot parar de aprender, aumente o `epsilon` para forçar mais exploração. Se o desempenho estiver instável, diminua o `epsilon` para focar na exploração.

---
**Atenção:** A Q-table é atualizada continuamente. Certifique-se de fazer um backup do arquivo `rl_q_table_massive_v2.json` antes de iniciar um novo treinamento, caso queira reverter para a versão atual.
