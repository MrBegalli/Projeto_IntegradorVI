/**
 * Módulo de comunicação com a API do backend.
 */

const API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://8000-i003phe7kjhw34lv8ctlm-51754cba.manusvm.computer';

/**
 * Cliente da API.
 */
class SuperTrunfoAPI {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    /**
     * Faz uma requisição HTTP.
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || error.error || 'Erro na requisição');
            }

            return await response.json();
        } catch (error) {
            console.error('Erro na API:', error);
            throw error;
        }
    }

    /**
     * Verifica saúde da API.
     */
    async health() {
        return this.request('/health');
    }

    /**
     * Obtém o baralho completo.
     */
    async getDeck() {
        return this.request('/deck');
    }

    /**
     * Inicia um novo jogo.
     * @param {string} difficulty - Dificuldade: 'fácil', 'médio' ou 'difícil'
     */
    async startGame(difficulty) {
        return this.request('/game/start', {
            method: 'POST',
            body: JSON.stringify({ difficulty })
        });
    }

    /**
     * Joga uma rodada.
     * @param {string} gameId - ID da sessão de jogo
     * @param {number} cardId - ID da carta a jogar
     * @param {string} attribute - Atributo escolhido
     */
    async playRound(gameId, cardId, attribute) {
        return this.request(`/game/${gameId}/play`, {
            method: 'POST',
            body: JSON.stringify({
                card_id: cardId,
                attribute: attribute
            })
        });
    }

    /**
     * Obtém status do jogo.
     * @param {string} gameId - ID da sessão de jogo
     */
    async getGameStatus(gameId) {
        return this.request(`/game/${gameId}/status`);
    }

    /**
     * Encerra um jogo.
     * @param {string} gameId - ID da sessão de jogo
     */
    async deleteGame(gameId) {
        return this.request(`/game/${gameId}`, {
            method: 'DELETE'
        });
    }
}

// Instância global da API
const api = new SuperTrunfoAPI();
