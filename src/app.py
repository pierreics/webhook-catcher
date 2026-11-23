import os
import psycopg
from flask import Flask, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db
from auth import auth_bp
from endpoints import endpoints_bp
from catcher import catcher_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "weakSecret")
app.register_blueprint(auth_bp)
app.register_blueprint(endpoints_bp)
app.register_blueprint(catcher_bp)

@app.route("/health", methods=["GET"])
def health():
  conn = None
  try:
    conn = get_db()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return jsonify({"status": "ok"}), 200
    finally:
      if conn is not None:
        conn.close()
  except psycopg.Error:
    return jsonify({"status": "Internal Error"}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
