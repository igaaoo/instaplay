-- Criar extensão para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar tabela de partidas
CREATE TABLE partida (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quadra INT,
    codigo VARCHAR(50) NOT NULL,
    pagamento BOOLEAN,
    ativa BOOLEAN,
    data_inicio TIMESTAMP NOT NULL,
    data_fim TIMESTAMP,
    created_at TIMESTAMP DEFAULT current_timestamp
);

-- Criar tabela de vídeos das partidas
CREATE TABLE partida_videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    partida_id UUID NOT NULL,
    path VARCHAR(255) NOT NULL,
    thumbnail TEXT,
    pagamento BOOLEAN,
    created_at TIMESTAMP DEFAULT current_timestamp,
    CONSTRAINT fk_partida
        FOREIGN KEY (partida_id) 
        REFERENCES partida (id) 
        ON DELETE CASCADE
);
