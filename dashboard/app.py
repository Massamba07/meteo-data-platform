
import os

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Météo Data Platform",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Météo Data Platform")
st.caption("Dashboard météo alimenté par PostgreSQL")


@st.cache_data(ttl=30)
def charger_donnees():
    conn = psycopg2.connect(
        host="localhost",
        port=os.getenv("POSTGRES_PORT", "5433"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

    try:
        query = """
            SELECT
                ville,
                date_mesure,
                temperature,
                humidite,
                vitesse_vent
            FROM mesures_meteo
            ORDER BY date_mesure
        """

        with conn.cursor() as cursor:
            cursor.execute(query)
            colonnes = [desc[0] for desc in cursor.description]
            lignes = cursor.fetchall()

        df = pd.DataFrame(lignes, columns=colonnes)
        df["date_mesure"] = pd.to_datetime(df["date_mesure"])
        return df

    finally:
        conn.close()


try:
    df = charger_donnees()
except Exception as erreur:
    st.error(f"Erreur de connexion PostgreSQL : {erreur}")
    st.stop()

if df.empty:
    st.warning("Aucune donnée météo disponible.")
    st.stop()

# Filtre par ville
villes = sorted(df["ville"].unique())
selection = st.multiselect(
    "Sélectionner les villes",
    options=villes,
    default=villes
)

df_filtre = df[df["ville"].isin(selection)]

if df_filtre.empty:
    st.info("Sélectionne au moins une ville.")
    st.stop()

# Indicateurs
col1, col2, col3 = st.columns(3)

col1.metric(
    "Nombre de villes",
    df_filtre["ville"].nunique()
)

col2.metric(
    "Observations",
    len(df_filtre)
)

col3.metric(
    "Température moyenne",
    f"{df_filtre['temperature'].mean():.1f} °C"
)

st.divider()

# Évolution temporelle
st.subheader("📈 Évolution des températures")

fig = px.line(
    df_filtre,
    x="date_mesure",
    y="temperature",
    color="ville",
    markers=True,
    labels={
        "date_mesure": "Date et heure",
        "temperature": "Température (°C)",
        "ville": "Ville"
    }
)

st.plotly_chart(fig, use_container_width=True)

# Comparaison des températures moyennes
st.subheader("🌡️ Température moyenne par ville")

moyennes = (
    df_filtre.groupby("ville", as_index=False)["temperature"]
    .mean()
)

fig_bar = px.bar(
    moyennes,
    x="ville",
    y="temperature",
    color="ville",
    labels={
        "ville": "Ville",
        "temperature": "Température moyenne (°C)"
    }
)

st.plotly_chart(fig_bar, use_container_width=True)

# Données brutes
st.subheader("📋 Données météorologiques")

st.dataframe(
    df_filtre.sort_values("date_mesure", ascending=False),
    use_container_width=True,
    hide_index=True
)

if st.button("Actualiser les données"):
    charger_donnees.clear()
    st.rerun()
