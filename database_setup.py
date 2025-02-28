import sqlite3
import pandas as pd

def initialize_database():
    conn = sqlite3.connect('radiology_reports.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            report_date TEXT,
            modality TEXT,
            findings TEXT,
            impression TEXT
        )
    ''')
    conn.commit()
    return conn

def load_data_to_db(conn, csv_path='data/cxr_reports.csv'):
    df = pd.read_csv(csv_path)
    df.to_sql('reports', conn, if_exists='replace', index=False)
    print("Data loaded successfully.")

if __name__ == "__main__":
    conn = initialize_database()
    load_data_to_db(conn)
