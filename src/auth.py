from db import get_db
from flask import  Blueprint, jsonify, request, session
import psycopg
from werkzeug.security import generate_password_hash, check_password_hash

def check_data(data):
  return not(not data or type(data) is not dict or not data.get("username") or not data.get("password") or type(data.get("password")) is not str or type(data.get("username")) is not str)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
  data = request.get_json(silent=True)
  if not check_data(data):
   return jsonify({"status": "bad request"}), 400
  password_hash = generate_password_hash(data['password'])
  conn = None
  try :
    conn = get_db()
    try :
      with conn, conn.cursor() as cur:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (data['username'], password_hash))
      return jsonify({"status" : "user successfully registered"}), 201
    finally:
      if conn is not None:
        conn.close()
  except psycopg.errors.UniqueViolation:
      return jsonify({"error" : "username already exists"}), 409
  except psycopg.Error:
    return jsonify({"status" : "Internal Error"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
  data = request.get_json(silent=True)
  if not check_data(data):
    return jsonify({"status": "bad request"}), 400
  conn = None
  try:
    conn = get_db()
    try :
      with conn, conn.cursor() as cur:
        cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (data['username'],))
        row = cur.fetchone()
        if not row or not check_password_hash(row[1], data['password']):
          session.clear()
          return jsonify({"status": "Incorrect username or password"}), 401
        session["user_id"]=row[0]
        return jsonify({"status": "successfully logged in"}), 200
    finally:
      if conn is not None:
        conn.close()
  except psycopg.Error:
      return jsonify({"status": "Internal Error"}), 500

@auth_bp.route("/logout", methods=["POST"])
def logout():
  if(not session.get("user_id")):
    return jsonify({"status":"user is not logged in"}), 401
  session.clear()
  return jsonify({"status": "user logged out"}), 200

@auth_bp.route("/me", methods=["GET"])
def me():
  user_id = session.get("user_id")
  if not user_id:
    return jsonify({"status":"invalid request"}), 401
  query = "SELECT id, username FROM users WHERE id = %s"
  conn = None
  try :
    conn = get_db()
    try :
      with conn, conn.cursor() as cur:
        cur.execute(query, (user_id,))
        row = cur.fetchone()
        if not row:
          return jsonify({"success":"false"}), 401
        res = {"id" : row[0] ,"username" : row[1]}
        return jsonify({"status" : "ok", "data" : res}), 200
    except psycopg.Error:
      return jsonify({"status": "Internal Error"}), 500
  finally:
    if conn is not None:
      conn.close()

@auth_bp.route("/changepassword", methods=["POST"])
def changepassword():
  user_id = session.get("user_id")
  if not user_id:
    return jsonify({"status":"invalid request"}), 401
  data = request.get_json(silent=True)
  if not data or type(data) is not dict:
    return jsonify({"status" : "bad request"}), 400
  oldpassword = data.get("oldpassword")
  newpassword = data.get("newpassword")
  if not oldpassword or not newpassword or type(oldpassword) is not str or type(newpassword) is not str or not oldpassword.strip() or not newpassword.strip():
   return jsonify({"status" : "bad request"}), 400
  query = "SELECT password_hash FROM users WHERE id = %s"
  conn = None
  try:
    conn = get_db()
    try:
      with conn, conn.cursor() as cur:
        cur.execute(query, (user_id,))
        row = cur.fetchone()
        if not row:
            session.clear()
            return jsonify({"success":"false"}), 401
        if not check_password_hash(row[0], oldpassword):
          return jsonify({"status" : "incorrect old password"}), 401
        query = "UPDATE users SET password_hash = %s WHERE id = %s"
        passwordHash = generate_password_hash(newpassword)
        cur.execute(query, (passwordHash, user_id))
        return jsonify({"status" : "password successfully changed"}), 200
    finally:
      if conn is not None:
        conn.close()
  except psycopg.Error:
    return jsonify({"status" : "Internal Error"}), 500
