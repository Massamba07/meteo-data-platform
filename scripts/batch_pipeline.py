
import os
from pathlib import Path
from datetime import datetime

import requests
import psycopg2
from dotenv import load_dotenv

# Charger la configuration privée
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# ÉTAPE 1 : EXTRACT
print("1. Extraction des données météo...")

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 48.8566,
    "longitude": 2.3522,
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m"
    ],
    "timezone": "Europe/Paris"
}

response = requests.get(url, params=params, timeout=15)
response.raise_for_status()
data = response.json()

# ÉTAPE 2 : TRANSFORM
print("2. Transformation des données...")

current = data["current"]

mesure = {
    "ville": "Paris",
    "date_mesure": datetime.fromisoformat(current["time"]),
    "temperature": current["temperature_2m"],
    "humidite": current["relative_humidity_2m"],
    "vitesse_vent": current["wind_speed_10m"]
}

print("Mesure transformée :", mesure)

# ÉTAPE 3 : LOAD
print("3. Chargement dans PostgreSQL...")

conn = psycopg2.connect(
    host="localhost",
    port=int(os.getenv("POSTGRES_PORT", "5433")),
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"]
)

try:
    with conn:
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
finally:
    conn.close()

print("ETL terminé avec succès !")
