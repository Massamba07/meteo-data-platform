
import json
from pathlib import Path

import requests

# Coordonnées géographiques de Paris
LATITUDE = 48.8566
LONGITUDE = 2.3522

# API Open-Meteo
URL = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m"
    ],
    "timezone": "Europe/Paris"
}

# 1. EXTRACTION : appel à l'API
response = requests.get(URL, params=params, timeout=15)
response.raise_for_status()

# 2. LECTURE : conversion JSON vers dictionnaire Python
data = response.json()

# 3. AFFICHAGE des données
print("Données météo de Paris :")
print(json.dumps(data["current"], indent=4, ensure_ascii=False))

# 4. STOCKAGE local au format JSON
project_root = Path(__file__).resolve().parent.parent
output_dir = project_root / "data"
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "meteo_paris.json"

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

print(f"\nDonnées enregistrées dans : {output_file}")
