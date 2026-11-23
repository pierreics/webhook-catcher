from db import get_db
from flask import Blueprint, session, request, jsonify
import psycopg
import secrets

endpoints_bp = Blueprint("endpoints", __name__)

@endpoints_bp.route("/endpoints", methods=["POST"])
def create_endpoint():
  user_id = session.get("user_id")
  if not user_id:
    return jsonify({"status" : "Unauthorized"}), 401
  data = request.get_json(silent=True)
  if not data or type(data) is not dict:
    return jsonify({"status" : "Invalid request"}), 400
  name = data.get("name")
  if not name or type(name) is not str or not name.strip():
    return jsonify({"status" : "Invalid request"}), 400
  name = name.strip()
  slug = secrets.token_urlsafe(8)
  query = "INSERT INTO endpoints (user_id, slug, name) VALUES (%s, %s, %s) RETURNING id, slug, name, created_at"
  conn = None
  try :
    conn = get_db()
    try :
      with conn, conn.cursor() as cur:
        cur.execute(query, (user_id, slug, name))
        row = cur.fetchone()
        data = {"id" : row[0], "slug" : row[1], "name" : row[2], "created_at" : row[3].isoformat()}
        return jsonify({"status" : "ok", "data" : data }), 201
    finally : 
      if conn is not None:
        conn.close()
  except psycopg.errors.UniqueViolation:
    return jsonify({"status" : "endpoint id already taken, try again"}), 500
  except psycopg.Error:
    return jsonify({"status" : "Internal Error"}), 500


@endpoints_bp.route("/endpoints", methods=["GET"])
def list_endpoints():
  user_id = session.get("user_id")
  if not user_id:
    return jsonify({"status" : "Unauthorized"}), 401
  query = "SELECT id, slug, name, created_at FROM endpoints WHERE user_id = %s ORDER BY created_at DESC"
  conn = None
  try :
    conn = get_db()
    try:
      with conn, conn.cursor() as cur:
        cur.execute(query, (user_id,))
        rows = cur.fetchall()
        data = []
        for row in rows:
          temp = {"id" : row[0], "slug" : row[1], "name" : row[2], "created_at" : row[3].isoformat()}
          data.append(temp)
        return jsonify({"status" : "ok", "data" : data }), 200
    finally:
      if conn is not None:
        conn.close()
  except psycopg.Error:
    return jsonify({"status" : "Internal Error"}), 500
    
@endpoints_bp.route("/endpoints/<int:endpoint_id>", methods=["DELETE"])
def delete_endpoint(endpoint_id):
  user_id = session.get("user_id")
  if not user_id:
    return jsonify({"status" : "Unauthorized"}), 401
  query = "DELETE FROM endpoints WHERE id = %s AND user_id = %s RETURNING id"
  conn = None
  try :
    conn = get_db()
    try :
      with conn, conn.cursor() as cur:
        cur.execute(query, (endpoint_id, user_id))
        row = cur.fetchone()
        if not row:
          return jsonify({"status" : "Not found"}), 404
        return jsonify({"status" : f"endpoint {endpoint_id} deleted"}), 200
    finally:
      if conn is not None:
        conn.close()
  except psycopg.Error:
    return jsonify({"status" : "Internal Error"}), 500

@endpoints_bp.route("/endpoints/<int:endpoint_id>/requests", methods=["GET"])
def get_requests(endpoint_id):
  user_id = session.get("user_id")
  if not user_id:
    return jsonify({"status" : "Unauthorized"}), 401
  query= "SELECT id FROM endpoints WHERE user_id = %s AND id = %s"
  conn = None
  try:
    conn = get_db()
    try:
      with conn, conn.cursor() as cur:
        cur.execute(query, (user_id, endpoint_id))
        row = cur.fetchone()
        if not row:
          return jsonify({"status" : "Not found"}), 404
        query = "SELECT id, method, path, query_string, headers, body, remote_addr, received_at FROM requests WHERE endpoint_id = %s ORDER BY received_at DESC"
        cur.execute(query, (endpoint_id,))
        rows = cur.fetchall()
        data = []
        for row in rows:
          temp = {"id" : row[0], "method" : row[1], "path": row[2], "query_string" : row[3], "headers" : row[4], "body" : row[5], "remote_addr" : row[6], "received_at": row[7].isoformat()}
          data.append(temp)
        return jsonify({"status" : "ok", "data" : data}), 200
    finally:
      if conn is not None:
        conn.close()
  except psycopg.Error:
    return jsonify({"status" : "Internal Error"}), 500