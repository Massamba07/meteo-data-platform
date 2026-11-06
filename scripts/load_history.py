
import requests
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

VILLES = {
    "Paris": (48.8566, 2.3522),
    "Lille": (50.6292, 3.0573),
    "Lyon": (45.7640, 4.8357),
    "Marseille": (43.2965, 5.3698),
    "Nantes": (47.2184, -1.5536)
}

conn = psycopg2.connect(
    host="localhost",
    port=os.getenv("POSTGRES_PORT", "5433"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

try:
    with conn.cursor() as cursor:
        for ville, (latitude, longitude) in VILLES.items():
            response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "hourly": (
                        "temperature_2m,"
                        "relative_humidity_2m,"
                        "wind_speed_10m"
                    ),
                    "past_days": 1,
                    "forecast_days": 0,
                    "timezone": "Europe/Paris"
                },
                timeout=20
            )
            response.raise_for_status()
            hourly = response.json()["hourly"]

            for i, date_mesure in enumerate(hourly["time"]):
                cursor.execute(
                    """
                    INSERT INTO mesures_meteo
                    (ville, date_mesure, temperature,
                     humidite, vitesse_vent)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (ville, date_mesure)
                    DO UPDATE SET
                        temperature = EXCLUDED.temperature,
                        humidite = EXCLUDED.humidite,
                        vitesse_vent = EXCLUDED.vitesse_vent
                    """,
                    (
                        ville,
                        date_mesure,
                        hourly["temperature_2m"][i],
                        hourly["relative_humidity_2m"][i],
                        hourly["wind_speed_10m"][i]
                    )
                )

            print(
                f"{ville} : {len(hourly['time'])} "
                "observations horaires traitées"
            )

    conn.commit()
    print("Chargement historique terminé !")

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()
