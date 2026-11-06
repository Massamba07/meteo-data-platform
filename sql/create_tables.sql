
CREATE TABLE IF NOT EXISTS mesures_meteo (
    id BIGSERIAL PRIMARY KEY,
    ville VARCHAR(100) NOT NULL,
    date_mesure TIMESTAMP NOT NULL,
    temperature DOUBLE PRECISION,
    humidite INTEGER,
    vitesse_vent DOUBLE PRECISION,
    date_ingestion TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (ville, date_mesure)
);
