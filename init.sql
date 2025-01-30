CREATE TABLE partida (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(50) NOT NULL,
    pagamento BOOLEAN,
    data_inicio TIMESTAMP NOT NULL,
    data_fim TIMESTAMP,
    created_at TIMESTAMP DEFAULT current_timestamp
);

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

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO teste;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO teste;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO teste;