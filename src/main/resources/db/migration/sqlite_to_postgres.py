# -*- coding: utf-8 -*-
import sqlite3
import psycopg2

# Fonction utilitaire pour décoder chaque colonne
def safe_decode(val):
    if isinstance(val, bytes):
        # Ignore all errors, always return a string (may lose some chars)
        return val.decode('utf-8', errors='ignore')
    return val
from psycopg2 import Error
import sys
import codecs

# Forcer l'encodage UTF-8 pour la sortie
# sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
# sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def migrate_data():
    sqlite_conn = None
    postgres_conn = None

    try:
        print("=== Migration des donnees ===")

        # Connexion à SQLite
        print("Connection SQLite...")
        sqlite_conn = sqlite3.connect('loto.db')
        # Correction encodage : forcer la récupération brute des données
        # sqlite_conn.text_factory = bytes  # On laisse SQLite gérer le type natif
        sqlite_cursor = sqlite_conn.cursor()

        # Connexion à PostgreSQL
        print("Connection PostgreSQL...")
        postgres_conn = psycopg2.connect(
            database="lotodb",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        postgres_cursor = postgres_conn.cursor()

        # Migration de la table users
        print("Migration users...")
        sqlite_cursor.execute("SELECT * FROM users")
        try:
            users = sqlite_cursor.fetchall()
        except Exception as e:
            print(f"[DEBUG] Erreur lors du fetchall users: {e}")
            users = []

        for user in users:
            try:
                user_decoded = []
                for idx, col in enumerate(user):
                    print(f"[DEBUG] Valeur brute colonne {idx} user: {col!r}")
                    print(f"[DEBUG] Valeur brute colonne {idx} ticket: {col!r}")
                    print(f"[DEBUG] Décodage colonne {idx} valeur: {col!r}")
                    try:
                        user_decoded.append(safe_decode(col))
                    except Exception as e_col:
                        print(f"Erreur de décodage colonne {idx} sur user: {user!r} -> {e_col}")
                        user_decoded.append('')  # ou None
                user_decoded = tuple(user_decoded)
            except Exception as e:
                print(f"Erreur de décodage sur user: {user!r} -> {e}")
                continue
            try:
                postgres_cursor.execute(
                    """
                    INSERT INTO users (id, first_name, last_name, email, password, is_admin)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    user_decoded
                )
            except Exception as e:
                print(f"Erreur insertion user: {str(e)}")

        # Migration de la table tickets
        print("Migration tickets...")
        sqlite_cursor.execute("SELECT * FROM tickets")
        try:
            tickets = sqlite_cursor.fetchall()
        except Exception as e:
            print(f"[DEBUG] Erreur lors du fetchall tickets: {e}")
            tickets = []

        for ticket in tickets:
            try:
                ticket_decoded = []
                for idx, col in enumerate(ticket):
                    print(f"[DEBUG] Décodage colonne {idx} valeur: {col!r}")
                    try:
                        ticket_decoded.append(safe_decode(col))
                    except Exception as e_col:
                        print(f"Erreur de décodage colonne {idx} sur ticket: {ticket!r} -> {e_col}")
                        ticket_decoded.append('')  # ou None
                ticket_decoded = tuple(ticket_decoded)
            except Exception as e:
                print(f"Erreur de décodage sur ticket: {ticket!r} -> {e}")
                continue
            try:
                postgres_cursor.execute(
                    """
                    INSERT INTO tickets (id, user_id, numbers, lucky_number, draw_date, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    ticket_decoded
                )
            except Exception as e:
                print(f"Erreur insertion ticket: {str(e)}")

        # Commit des changements
        postgres_conn.commit()
        print("Migration reussie")

    except Exception as error:
        print("Erreur:", str(error))

    finally:
        if sqlite_conn:
            sqlite_cursor.close()
            sqlite_conn.close()
        if postgres_conn:
            postgres_cursor.close()
            postgres_conn.close()

if __name__ == "__main__":
    try:
        print("Debut migration")
        migrate_data()
        print("Fin migration")
    except Exception as e:
        print("Erreur principale:", str(e))
