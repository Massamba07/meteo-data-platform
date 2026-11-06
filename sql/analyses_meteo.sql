-- 1. Nombre d'observations par ville
SELECT ville, COUNT(*) AS nb_observations
FROM mesures_meteo
GROUP BY ville
ORDER BY ville;


-- 2. Température moyenne par ville
SELECT
    ville,
    ROUND(AVG(temperature)::numeric, 2) AS temperature_moyenne
FROM mesures_meteo
GROUP BY ville
ORDER BY temperature_moyenne DESC;


-- 3. Évolution horaire des températures
SELECT
    ville,
    date_mesure,
    temperature
FROM mesures_meteo
ORDER BY ville, date_mesure;


-- 4. Ville la plus chaude sur la période
SELECT
    ville,
    MAX(temperature) AS temperature_max
FROM mesures_meteo
GROUP BY ville
ORDER BY temperature_max DESC
LIMIT 1;


-- 5. Amplitude thermique par ville
SELECT
    ville,
    ROUND(
        (MAX(temperature) - MIN(temperature))::numeric,
        2
    ) AS amplitude_thermique
FROM mesures_meteo
GROUP BY ville
ORDER BY amplitude_thermique DESC;