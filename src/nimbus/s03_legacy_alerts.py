# mypy: ignore-errors
"""Bloc 2, partie B — script LEGACY d'alertes météo. NE PAS MODIFIER.

Il encode tout avec des valeurs magiques : -999 pour « pas de valeur », des
chaînes "HEATWAVE", "FROST"... pour le type d'alerte, et None pour « rien ».
Il produit aussi de fausses alertes : une température aberrante (999.9 °C,
-273 °C) est traitée comme une vraie mesure.

Réécrivez-le avec des algebraic data types dans `s03_algebraic_types.py`
(exercices 3.7 à 3.9).
"""

HEATWAVE_THRESHOLD = 25.0
FROST_THRESHOLD = 0.0
STORM_THRESHOLD = 28.0
FLOOD_THRESHOLD = 15.0


def _number(s):
    try:
        return float(s)
    except ValueError:
        return -999


def alert_code(t, wind, rain):
    code = None
    if wind != -999 and wind >= STORM_THRESHOLD:
        code = "STORM"
    elif rain != -999 and rain >= FLOOD_THRESHOLD:
        code = "FLOOD"
    elif t != -999 and t >= HEATWAVE_THRESHOLD:
        code = "HEATWAVE"
    elif t != -999 and t <= FROST_THRESHOLD:
        code = "FROST"
    return code


def alerts(text):
    output = []
    for line in text.splitlines()[1:]:
        c = line.split(",")
        if len(c) != 7:
            continue
        t, wind, rain = _number(c[2]), _number(c[5]), _number(c[6])
        code = alert_code(t, wind, rain)
        if code == "STORM":
            output.append(f"{c[0]} {c[1]} : tempête, vent {wind:.1f} km/h")
        elif code == "FLOOD":
            output.append(f"{c[0]} {c[1]} : risque d'inondation, {rain:.1f} mm")
        elif code == "HEATWAVE":
            output.append(f"{c[0]} {c[1]} : canicule, {t:.1f} °C")
        elif code == "FROST":
            output.append(f"{c[0]} {c[1]} : gel, {t:.1f} °C")
    return output
