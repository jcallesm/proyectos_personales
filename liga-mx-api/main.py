import os
import requests
from dotenv import load_dotenv

# ======================================================
# 1. Cargar la API key desde archivo .env
# ======================================================
load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")

BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-apisports-key": API_KEY
}


# ======================================================
# 2. Función para probar la conexión con la API
# ======================================================
def test_connection():
    url = f"{BASE_URL}/status"
    response = requests.get(url, headers=headers)

    print("Status code:", response.status_code)
    print("JSON:", response.json())


# ======================================================
# 3. Obtener información de la Liga MX + temporadas
# ======================================================
def get_liga_mx_league():
    url = f"{BASE_URL}/leagues"
    params = {"id": 262}  # ID de la Liga MX

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if response.status_code != 200 or data.get("results", 0) == 0:
        print("❌ Error al obtener la información de la liga")
        print(data)
        return

    league_info = data["response"][0]
    league_name = league_info["league"]["name"]
    country = league_info["country"]["name"]
    seasons = league_info["seasons"]

    print(f"\n🏆 Liga encontrada: {league_name} ({country})\n")
    print("📅 Temporadas disponibles:")
    for s in seasons:
        print(f"- {s['year']} | {s['start']} → {s['end']}")


# ======================================================
# 4. Código que se ejecuta al correr el script
# ======================================================
if __name__ == "__main__":
    # Primero validamos que la key funcione
    # test_connection()

    # Ahora obtenemos la info de la Liga MX
    get_liga_mx_league()

def get_liga_mx_fixtures(season):
    """
    Descarga todos los partidos (fixtures) de la Liga MX
    para una temporada específica.
    """
    url = f"{BASE_URL}/fixtures"
    params = {
        "league": 262,  # Liga MX
        "season": season
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if response.status_code != 200 or data.get("results", 0) == 0:
        print(f"❌ Error obteniendo fixtures de la temporada {season}")
        print(data)
        return None

    # Convertir JSON anidado a DataFrame
    import pandas as pd
    df = pd.json_normalize(data["response"])

    print(f"✔️ Temporada {season} descargada con {len(df)} partidos.")

    # Guardar CSV
    df.to_csv(f"liga_mx_fixtures_{season}.csv", index=False)
    print(f"💾 Guardado: liga_mx_fixtures_{season}.csv")

    return df
if __name__ == "__main__":
    # get_liga_mx_league()

    # Descarga una temporada específica
    get_liga_mx_fixtures(2024)
