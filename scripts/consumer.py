
import json
import os
from pathlib import Path

import psycopg2
from confluent_kafka import Consumer, KafkaException
from dotenv import load_dotenv

# Charger les variables d'environnement
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

TOPIC = "meteo-mesures"

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="127.0.0.1",
    port=int(os.getenv("POSTGRES_PORT", "5433")),
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"]
)

# Configuration Kafka
consumer = Consumer({
    "bootstrap.servers": "127.0.0.1:9092",
    "group.id": "meteo-postgres-consumer",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False
})

consumer.subscribe([TOPIC])

print("Consumer démarré. En attente des messages...", flush=True)

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            raise KafkaException(msg.error())

        # 1. Lire le message JSON
        mesure = json.loads(msg.value().decode("utf-8"))

        print("Message reçu :", mesure, flush=True)

        # 2. Insérer dans PostgreSQL
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO mesures_meteo (
                        ville,
                        date_mesure,
                        temperature,
                        humidite,
                        vitesse_vent
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (ville, date_mesure)
                    DO UPDATE SET
                        temperature = EXCLUDED.temperature,
                        humidite = EXCLUDED.humidite,
                        vitesse_vent = EXCLUDED.vitesse_vent
                    """,
                    (
                        mesure["ville"],
                        mesure["date_mesure"],
                        mesure["temperature"],
                        mesure["humidite"],
                        mesure["vitesse_vent"]
                    )
                )

            conn.commit()

            # Confirmer la lecture après insertion en base
            consumer.commit(message=msg, asynchronous=False)

            print("Mesure enregistrée dans PostgreSQL !", flush=True)

        except Exception:
            conn.rollback()
            raise

except KeyboardInterrupt:
    print("\nArrêt du Consumer demandé.")

finally:
    consumer.close()
    conn.close()
    print("Connexions fermées.")
