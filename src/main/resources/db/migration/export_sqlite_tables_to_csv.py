import sqlite3

def export_table_to_csv(db_path, table_name, csv_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(csv_path, 'wb') as f:
        for row in cursor.execute(f"SELECT * FROM {table_name}"):
            # Export chaque colonne en bytes si possible, sinon en str encodé
            line = b';'.join([
                col if isinstance(col, bytes) else str(col).encode('utf-8', errors='ignore')
                for col in row
            ])
            f.write(line + b'\n')
    conn.close()
    print(f"Table {table_name} exportée vers {csv_path}")

if __name__ == "__main__":
    db_path = 'loto.db'  # adapte le chemin si besoin
    tables = ['users', 'tickets', 'ticket_gains']  # ajoute ici toutes tes tables à exporter
    for table in tables:
        export_table_to_csv(db_path, table, f"{table}_export.csv")
