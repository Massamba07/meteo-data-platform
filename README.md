# 🌤️ Météo Data Platform

Projet pédagogique de Data Engineering permettant de construire une plateforme de collecte, de traitement, de stockage et de visualisation de données météorologiques.

## 1. Objectifs

- Consommer une API REST avec Python.
- Manipuler des données au format JSON.
- Développer un pipeline ETL batch.
- Mettre en place un pipeline streaming avec Apache Kafka.
- Stocker les observations dans PostgreSQL.
- Charger un historique météorologique.
- Analyser les données avec SQL.
- Créer un dashboard interactif avec Streamlit.

## 2. Architecture

**Pipeline batch :**

Open-Meteo API → Python → PostgreSQL

**Pipeline streaming :**

Open-Meteo API → Python Producer → Apache Kafka → Python Consumer → PostgreSQL

**Visualisation :**

PostgreSQL → Streamlit → Dashboard interactif

## 3. Technologies utilisées

| Technologie | Rôle |
|---|---|
| Python | Extraction et transformation |
| Open-Meteo | Source des données météo |
| Apache Kafka | Transport des événements |
| PostgreSQL 16 | Stockage des données |
| Docker Compose | Exécution des services |
| Pandas | Manipulation des données |
| Plotly | Graphiques interactifs |
| Streamlit | Dashboard web |

## 4. Prérequis

- Python 3.11 ou compatible
- Docker Desktop avec Docker Compose
- Git
- VS Code ou un autre éditeur

## 5. Installation

Cloner le projet :

```powershell
git clone <URL_DU_DEPOT>
cd meteo-data-platform
```

Créer et activer l'environnement virtuel :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Installer les dépendances :

```powershell
python -m pip install -r requirements.txt
```

Créer le fichier de configuration :

```powershell
Copy-Item .env.example .env
```

Modifier `.env` pour définir un mot de passe PostgreSQL personnel.

## 6. Démarrer l'infrastructure

```powershell
docker compose up -d
docker compose ps
```

Les services sont accessibles localement :

- PostgreSQL : `127.0.0.1:5433`
- Kafka : `127.0.0.1:9092`

Créer le topic Kafka :

```powershell
docker exec meteo-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server 127.0.0.1:9092 --create --if-not-exists --topic meteo-mesures --partitions 1 --replication-factor 1
```

## 7. Initialiser PostgreSQL

```powershell
Get-Content .\sql\create_tables.sql | docker exec -i meteo-postgres psql -U meteo -d meteo_db
```

## 8. Exécuter le pipeline batch

```powershell
python scripts/batch_pipeline.py
```

Charger les observations horaires historiques :

```powershell
python scripts/load_history.py
```

## 9. Exécuter le pipeline streaming

Dans un premier terminal :

```powershell
python scripts/consumer.py
```

Dans un deuxième terminal :

```powershell
python scripts/producer.py
```

Le Producer publie les mesures des cinq villes dans Kafka. Le Consumer reçoit les messages et les enregistre dans PostgreSQL.

## 10. Analyser les données

```powershell
Get-Content .\sql\analyses_meteo.sql | docker exec -i meteo-postgres psql -U meteo -d meteo_db
```

## 11. Lancer le dashboard

```powershell
python -m streamlit run dashboard/app.py
```

Ouvrir : http://localhost:8501

Le dashboard permet de comparer les températures, de suivre leur évolution et de consulter les observations.

## 📊 Aperçu du dashboard Streamlit

### 1. Vue générale du dashboard

![Vue générale du dashboard](assets/Page%201.png)

### 2. Comparaison des températures

![Comparaison des températures](assets/Page%202.png)

### 3. Données météorologiques

![Données PostgreSQL](assets/Page%203.png)


## 12. Arrêter les services

```powershell
docker compose down
```

Cette commande arrête et supprime les conteneurs sans supprimer les volumes Docker nommés.

**Attention :** la configuration actuelle ne définit pas de volume persistant pour Kafka. La recréation de son conteneur peut entraîner la perte des messages.

Ne pas utiliser `docker compose down -v` sauf si la suppression des données PostgreSQL est volontaire.

## 13. Sécurité

- Les identifiants PostgreSQL sont stockés dans `.env`.
- Le fichier `.env` est exclu de Git.
- `.env.example` sert de modèle sans véritable secret.
- Les ports des services Docker sont exposés uniquement en local.

## 14. Perspectives

- Automatiser la collecte périodique.
- Ajouter des tests unitaires.
- Mettre en place une intégration continue GitHub Actions.
- Améliorer la persistance et la supervision Kafka.
- Déployer le dashboard dans un environnement cloud.

---

**Projet pédagogique : Data Engineering, ETL/ELT, API REST, Batch & Streaming.**