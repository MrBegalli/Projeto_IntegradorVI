CREATE TABLE carros (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    pais VARCHAR(50),
    velocidade INT,
    resistencia INT,
    motor INT,
    preco INT
);
INSERT INTO carros (nome, pais, velocidade, resistencia, motor, preco) VALUES
('Falcon GT', 'EUA', 320, 78, 480, 420000),
('Veloce S', 'Itália', 330, 70, 520, 690000),
('Strasse RS', 'Alemanha', 305, 85, 450, 510000),
('Thunder R', 'Japão', 300, 88, 430, 290000),
('Aurora X', 'Suécia', 310, 92, 470, 580000),
('Roadmaster V8', 'EUA', 280, 90, 400, 220000),
('Corsa GTi', 'Brasil', 240, 72, 220, 120000),
('Tourer Hybrid', 'Japão', 230, 95, 200, 160000),
('Riviera LX', 'França', 260, 80, 260, 240000),
('Monaco V12', 'Itália', 340, 68, 700, 1500000);
