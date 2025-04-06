from flask import Flask, render_template
import sqlite3
import pandas as pd

app = Flask(__name__)
DB_FILE = "structures.db"

@app.route("/")
def index():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("""
        SELECT * FROM structures
        WHERE STRUCTURE_TYPE = 'WASHROOM'
        AND centroid_lat IS NOT NULL AND centroid_lon IS NOT NULL
    """, conn)
    conn.close()

    return render_template("index.html", data=df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
