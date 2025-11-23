# Guia de Treinamento e Avaliação do RL_Bot

Este documento fornece as instruções completas para treinar o `RL_Bot`, avaliar seu desempenho e gerar os gráficos de análise em sua máquina local.

## 1. Pré-requisitos

Antes de começar, certifique-se de que você tem o seguinte software instalado:

- **Python 3.9+**: Você pode baixar a versão mais recente em [python.org](https://www.python.org/downloads/).
- **pip**: Geralmente vem instalado com o Python. Você pode verificar executando `pip --version` no seu terminal.

## 2. Configuração do Ambiente

Siga estes passos para configurar o ambiente do projeto:

1.  **Navegue até a pasta do projeto**: Abra um terminal ou prompt de comando e navegue até o diretório raiz do seu projeto (`Projeto_IntegradorVI`).

2.  **Crie um Ambiente Virtual (Recomendado)**: Usar um ambiente virtual isola as dependências do seu projeto e evita conflitos com outros projetos Python.

    ```bash
    # No Windows
    python -m venv venv
    .\venv\Scripts\activate

    # No macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as Dependências**: O arquivo `requirements.txt` na pasta `backend` contém todas as bibliotecas Python necessárias. Instale-as com o seguinte comando:

    ```bash
    pip install -r backend/requirements.txt
    ```

## 3. Executando o Treinamento Otimizado

O script `train_optimized.py` foi criado para treinar o `RL_Bot` de forma eficiente, utilizando uma estratégia de múltiplos oponentes para melhorar a generalização e o desempenho.

1.  **Navegue até a pasta de treinamento**:

    ```bash
    cd backend/rl_training
    ```

2.  **Execute o script de treinamento**:

    ```bash
    python train_optimized.py
    ```

-   O treinamento executará **10.000 episódios** por padrão. O progresso será exibido no terminal, com avaliações periódicas da taxa de vitória.
-   Ao final, a Q-table treinada será salva como `backend/data/rl_q_table_optimized.json`.
-   Um arquivo de histórico, `backend/data/rl_q_table_optimized_history.json`, também será criado para visualização do progresso.

### Customizando o Treinamento

Você pode editar o arquivo `train_optimized.py` para ajustar os parâmetros. Na função `main()`, no final do arquivo, você pode alterar a linha:

```python
# Altere o número de episódios, intervalo de avaliação e de salvamento aqui
trainer.train(episodes=10000, eval_interval=500, save_interval=2000)
```

## 4. Avaliando o Desempenho e Gerando Gráficos

Após o treinamento, o script `evaluate_and_plot.py` pode ser usado para realizar uma avaliação completa e gerar os gráficos de desempenho (Heatmap, Radar e Barras).

1.  **Certifique-se de que você está na pasta `backend/rl_training`**.

2.  **Execute o script de avaliação**:

    ```bash
    python evaluate_and_plot.py
    ```

-   O script carregará a Q-table treinada (`rl_q_table_optimized.json`) e simulará 500 jogos contra cada oponente para obter estatísticas de desempenho robustas.
-   Os seguintes arquivos de imagem serão gerados e salvos na pasta `backend/data/`:
    -   `heatmap_winrate.png`: Heatmap de taxa de vitória entre todos os bots.
    -   `radar_performance.png`: Gráfico de radar comparando o desempenho do `RL_Bot` e do `Medio_Bot`.
    -   `bar_comparison.png`: Gráfico de barras comparando as taxas de vitória.
    -   `training_progress.png`: Gráfico mostrando a evolução da recompensa e da taxa de vitória durante o treinamento.

## 5. Arquivos Gerados

Ao final de todo o processo, os seguintes arquivos importantes estarão disponíveis na pasta `backend/data/`:

| Arquivo                               | Descrição                                                                                             |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `rl_q_table_optimized.json`           | **O modelo treinado**. Contém a Q-table com os valores de estado-ação aprendidos pelo `RL_Bot`.         |
| `rl_q_table_optimized_history.json`   | Dados brutos do histórico de treinamento, incluindo recompensas e taxas de vitória ao longo do tempo. |
| `evaluation_results.json`             | Resultados numéricos da avaliação final (taxas de vitória, derrota e empate).                        |
| `heatmap_winrate.png`                 | Gráfico de heatmap.                                                                                   |
| `radar_performance.png`               | Gráfico de radar.                                                                                     |
| `bar_comparison.png`                  | Gráfico de barras.                                                                                    |
| `training_progress.png`               | Gráfico de progresso do treinamento.                                                                  |


Com estes passos, você poderá replicar o treinamento e a avaliação do `RL_Bot` em seu próprio ambiente.
