import random
from jogo import Jogo
from bots import MCTSBot, WeightedBot, RLBot

class Treinador:
    def __init__(self, agente_principal):
        self.agente_principal = agente_principal
        # Inicializar bots com deck do RL
        self.mcts = MCTSBot(deck=agente_principal.deck)
        self.weighted = WeightedBot(deck=agente_principal.deck)

    def escolher_adversario(self, modo):
        if modo == "humano":
            return None
        elif modo == "mcts":
            return self.mcts
        elif modo == "weighted":
            return self.weighted
        elif modo == "dois":
            return random.choice([self.mcts, self.weighted])
        else:
            raise ValueError("Modo inválido: humano, mcts, weighted, dois")

    def treinar(self, episodios=100, modo="dois"):
        for ep in range(episodios):
            adversario = self.escolher_adversario(modo)
            jogo = Jogo(deck_jogador1=self.agente_principal.deck,
                        deck_jogador2=adversario.deck if adversario else None)

            while not jogo.terminou():
                # Jogada do RL
                if jogo.jogador_atual == 1:
                    acao, stat = self.agente_principal.choose_move(
                        jogo.deck2 if jogo.deck2 else [], ["HP","torque","weight","0-100","top_speed"]
                    )
                    idx = jogo.deck1.index(acao)
                    jogo.jogar(idx)
                else:
                    if adversario is None:
                        jogo.render()
                        idx = int(input("Sua jogada: "))
                        jogo.jogar(idx)
                    else:
                        card, stat = adversario.choose_move(jogo.deck1, ["HP","torque","weight","0-100","top_speed"])
                        idx = adversario.deck.index(card)
                        jogo.jogar(idx)

            # Atualiza aprendizado
            if isinstance(self.agente_principal, RLBot):
                self.agente_principal.update_q_after_game(jogo)

            print(f"Episódio {ep+1}/{episodios} finalizado. Vencedor: {jogo.vencedor}")
