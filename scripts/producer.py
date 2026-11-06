
import json
import time
from datetime import datetime, timezone

import requests
from confluent_kafka import Producer

API_URL = "https://api.open-meteo.com/v1/forecast"
TOPIC = "meteo-mesures"

VILLES = {
    "Paris": (48.8566, 2.3522),
    "Lille": (50.6292, 3.0573),
    "Lyon": (45.7640, 4.8357),
    "Marseille": (43.2965, 5.3698),
    "Nantes": (47.2184, -1.5536)
}

producer = Producer({
    "bootstrap.servers": "127.0.0.1:9092",
    "client.id": "meteo-producer"
})


def delivery_report(err, msg):
    if err is not None:
        print(f"Erreur Kafka : {err}")
    else:
        print(
            f"Message envoyé : "
            f"partition={msg.partition()}, "
            f"offset={msg.offset()}"
        )


def recuperer_meteo(ville, latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m"
        ],
        "timezone": "Europe/Paris"
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=15
    )
    response.raise_for_status()

    current = response.json()["current"]

    return {
        "ville": ville,
        "date_mesure": current["time"],
        "temperature": current["temperature_2m"],
        "humidite": current["relative_humidity_2m"],
        "vitesse_vent": current["wind_speed_10m"],
        "date_publication": datetime.now(
            timezone.utc
        ).isoformat()
    }


print("Démarrage du Producer multivilles...")

try:
    for ville, (latitude, longitude) in VILLES.items():
        mesure = recuperer_meteo(
            ville, latitude, longitude
        )

        producer.produce(
            topic=TOPIC,
            key=ville.encode("utf-8"),
            value=json.dumps(mesure).encode("utf-8"),
            callback=delivery_report
        )

        remaining = producer.flush(timeout=15)
        if remaining:
            raise RuntimeError(
                f"{remaining} message(s) non livré(s)"
            )

        print(f"{ville} : {mesure['temperature']} °C")

        time.sleep(2)

finally:
    producer.flush(timeout=5)

print("Publication multivilles terminée !")
