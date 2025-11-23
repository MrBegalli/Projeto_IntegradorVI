# Treinamento DQN - Super Trunfo RL Bot

Este diretório contém o script de treinamento para o RL Bot usando Deep Q-Network (DQN).

## 📁 Arquivos

- `train_dqn.py` - Script único de treinamento DQN

## 🚀 Como Usar

### Treinamento Básico

```bash
python train_dqn.py
```

Isso executará o treinamento com os parâmetros padrão:
- 50.000 episódios
- Avaliação a cada 1.000 episódios
- Salvamento a cada 5.000 episódios

### Treinamento Personalizado

```bash
python train_dqn.py --episodes 100000 --eval-interval 2000 --save-interval 10000
```

### Continuar Treinamento de Modelo Existente

```bash
python train_dqn.py --model ../data/dqn_model.pth --episodes 20000
```

## 🎯 Parâmetros

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--episodes` | Número total de episódios de treinamento | 50000 |
| `--eval-interval` | Intervalo entre avaliações de desempenho | 1000 |
| `--save-interval` | Intervalo entre salvamentos de checkpoint | 5000 |
| `--model` | Caminho para modelo pré-treinado (continuar treinamento) | None |

## 📊 Processo de Treinamento

### Fases do Treinamento

O treinamento é dividido em 3 fases progressivas:

1. **Fase Inicial (0-30% dos episódios)**
   - 70% dos jogos contra Facil_Bot
   - 30% dos jogos contra Medio_Bot
   - Foco em aprender estratégias básicas

2. **Fase Intermediária (30-60% dos episódios)**
   - 50% dos jogos contra Facil_Bot
   - 50% dos jogos contra Medio_Bot
   - Balanceamento entre aprendizado básico e avançado

3. **Fase Final (60-100% dos episódios)**
   - 30% dos jogos contra Facil_Bot
   - 70% dos jogos contra Medio_Bot
   - Foco em superar oponentes mais fortes

### Epsilon Decay

O parâmetro epsilon controla a exploração vs explotação:

- **Início:** ε = 1.0 (exploração máxima)
- **Fim:** ε = 0.05 (explotação máxima)
- **Decay:** Linear ao longo dos episódios

### Sistema de Recompensas

| Evento | Recompensa (Facil_Bot) | Recompensa (Medio_Bot) |
|--------|------------------------|------------------------|
| Vitória na rodada | +3.0 | +5.0 |
| Derrota na rodada | -2.0 | -3.0 |
| Empate na rodada | -0.5 | -0.5 |
| Vitória no jogo | +10.0 | +15.0 |
| Derrota no jogo | -5.0 | -8.0 |

## 📈 Monitoramento

### Logs

Os logs são salvos em `../logs/training_dqn_YYYYMMDD_HHMMSS.log`

Exemplo de saída:
```
[2024-11-23 14:30:00] ================================================================================
[2024-11-23 14:30:00] Episódio 1,000/50,000
[2024-11-23 14:30:00]   Epsilon: 0.9800
[2024-11-23 14:30:00]   Recompensa média (últimos 100): 12.45
[2024-11-23 14:30:00]   Tamanho do buffer: 5000
[2024-11-23 14:30:00] 
[2024-11-23 14:30:00]   Avaliando desempenho (100 jogos por oponente)...
[2024-11-23 14:30:05]     vs Facil_Bot   :  85.0% vitórias |  5.0% empates
[2024-11-23 14:30:10]     vs Medio_Bot   :  45.0% vitórias | 10.0% empates 🔥 NOVO RECORDE!
[2024-11-23 14:30:10] ================================================================================
```

### Métricas Avaliadas

A cada `eval-interval` episódios, o script avalia:

1. **Recompensa Média:** Média das últimas 100 recompensas
2. **Taxa de Vitória:** Percentual de vitórias contra cada oponente
3. **Taxa de Empate:** Percentual de empates
4. **Epsilon Atual:** Nível de exploração vs explotação
5. **Tamanho do Buffer:** Quantidade de experiências armazenadas

### Arquivos Gerados

1. **Modelo Treinado:** `../data/dqn_model.pth`
   - Pesos da rede neural
   - Pode ser carregado para continuar treinamento ou inferência

2. **Histórico de Treinamento:** `../data/dqn_training_history.json`
   - Episódios executados
   - Recompensas médias
   - Valores de epsilon
   - Taxas de vitória ao longo do tempo

Exemplo de histórico:
```json
{
  "episodes": [1000, 2000, 3000, ...],
  "avg_rewards": [12.45, 15.30, 18.20, ...],
  "epsilon_values": [0.98, 0.96, 0.94, ...],
  "win_rates": {
    "Facil_Bot": [0.85, 0.88, 0.90, ...],
    "Medio_Bot": [0.45, 0.48, 0.52, ...]
  }
}
```

## 🎯 Metas de Desempenho

### Objetivos

| Oponente | Meta de Vitória | Excelente |
|----------|----------------|-----------|
| Facil_Bot | > 80% | > 90% |
| Medio_Bot | > 50% | > 60% |

### Tempo Estimado

- **50.000 episódios:** ~2-4 horas (dependendo do hardware)
- **100.000 episódios:** ~4-8 horas

## 🔧 Troubleshooting

### Problema: Treinamento muito lento

**Solução:**
- Verifique se PyTorch está usando GPU: `torch.cuda.is_available()`
- Reduza o número de simulações do MCTS Bot (edite `train_dqn.py`)
- Use menos episódios de avaliação

### Problema: Taxa de vitória não melhora

**Solução:**
- Aumente o número de episódios
- Ajuste os hiperparâmetros (epsilon, alpha, gamma)
- Verifique se o sistema de recompensas está adequado

### Problema: Memória insuficiente

**Solução:**
- Reduza o tamanho do buffer de replay (edite `rl_model.py`)
- Use batch size menor
- Feche outros programas

## 📚 Referências

- [Playing Atari with Deep Reinforcement Learning (Mnih et al., 2013)](https://arxiv.org/abs/1312.5602)
- [Human-level control through deep reinforcement learning (Mnih et al., 2015)](https://www.nature.com/articles/nature14236)

## 💡 Dicas

1. **Comece com poucos episódios** para testar se tudo está funcionando
2. **Monitore os logs** para identificar problemas cedo
3. **Salve checkpoints frequentemente** para não perder progresso
4. **Experimente diferentes hiperparâmetros** para melhorar o desempenho
5. **Use GPU** se disponível para acelerar o treinamento

---

**Boa sorte com o treinamento! 🚀**
