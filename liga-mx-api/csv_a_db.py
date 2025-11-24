import pandas as pd
import sqlite3
import os

# Nombre del archivo SQLite
DB_NAME = "liga_mx.db"

def create_connection():
    return sqlite3.connect(DB_NAME)


def load_fixtures_to_df():
    """
    Lee los CSVs de fixtures (2021, 2022, 2023)
    y combina todo en un solo DataFrame.
    """
    dfs = []
    for year in [2021, 2022, 2023]:
        filename = f"liga_mx_fixtures_{year}.csv"
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df["season"] = year
            dfs.append(df)
            print(f"✔️ Cargado {filename}")
        else:
            print(f"⚠️ No se encontró {filename}")

    full_df = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal de partidos combinados: {len(full_df)}")
    return full_df


def create_dim_teams(df, conn):
    """
    Crea la tabla dim_teams con IDs únicos de equipos.
    """
    teams_home = df[["teams.home.id", "teams.home.name"]].rename(
        columns={"teams.home.id": "team_id", "teams.home.name": "team_name"}
    )
    teams_away = df[["teams.away.id", "teams.away.name"]].rename(
        columns={"teams.away.id": "team_id", "teams.away.name": "team_name"}
    )

    teams = pd.concat([teams_home, teams_away], ignore_index=True).drop_duplicates()

    teams.to_sql("dim_teams", conn, if_exists="replace", index=False)
    print("🏟️ dim_teams creada correctamente")


def create_dim_venues(df, conn):
    """
    Crea la tabla dim_venues (estadios).
    """
    venues = df[["fixture.venue.id", "fixture.venue.name"]].rename(
        columns={"fixture.venue.id": "venue_id", "fixture.venue.name": "venue_name"}
    ).drop_duplicates()

    venues.to_sql("dim_venues", conn, if_exists="replace", index=False)
    print("🏟️ dim_venues creada correctamente")


def create_fact_matches(df, conn):
    """
    Crea fact_matches con métricas clave.
    """
    fact = df[[
        "fixture.id",
        "season",
        "fixture.date",
        "teams.home.id",
        "teams.away.id",
        "goals.home",
        "goals.away",
        "fixture.venue.id",
        "league.round",
        "fixture.status.long"
    ]].rename(columns={
        "fixture.id": "match_id",
        "teams.home.id": "home_team_id",
        "teams.away.id": "away_team_id",
        "goals.home": "home_goals",
        "goals.away": "away_goals",
        "fixture.venue.id": "venue_id",
        "fixture.status.long": "status"
    })

    fact.to_sql("fact_matches", conn, if_exists="replace", index=False)
    print("📊 fact_matches creada correctamente")


def build_database():
    conn = create_connection()
    df = load_fixtures_to_df()

    create_dim_teams(df, conn)
    create_dim_venues(df, conn)
    create_fact_matches(df, conn)

    conn.close()
    print("\n🎉 Base de datos creada: liga_mx.db")


if __name__ == "__main__":
    build_database()
