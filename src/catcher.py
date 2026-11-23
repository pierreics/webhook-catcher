from flask import Blueprint, session, request, jsonify
from db import get_db
import json
import psycopg

catcher_bp = Blueprint("catcher", __name__)

@catcher_bp.route("/c/<slug>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def catcher(slug):
  query = "SELECT id FROM endpoints WHERE slug = %s"
  conn = None
  try :
    conn = get_db()
    try :
      with conn, conn.cursor() as cur:
        cur.execute(query, (slug,))
        row = cur.fetchone()
        if not row:
          return jsonify({"status" : "Not found"}), 404
        method = request.method
        headers = json.dumps(dict(request.headers))
        params = json.dumps(dict(request.args))
        body = request.get_data(as_text=True)
        path = request.path
        remote_addr = request.remote_addr
        query = "INSERT INTO requests (endpoint_id, method, path, query_string, headers, body, remote_addr) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cur.execute(query, (row[0], method, path, params, headers, body, remote_addr ))
        return jsonify({"status": "received"}), 200
    finally:
      if conn is not None:
        conn.close()
  except psycopg.Error:
    return jsonify({"status" : "Internal Error"}), 500
    
        