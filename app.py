from positions import *
from cs50 import SQL
from flask import Flask, render_template, request, session, url_for
from functools import wraps
from flask import redirect, render_template, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from math import *
import json
import requests

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///chess.db")

RANKS = ["rapid", "blitz", "bullet"]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("login")
        return f(*args, **kwargs)
    return decorated_function

def replace_space(string):
    result = ""
    for i in string:
        if i == " ":
            result = result + "%"
        else:
            result = result + i
    return result

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        action = request.json.get("action")
        if action == "move":
            possibilites = positions(request.json.get("piece"), request.json.get("source"), request.json.get("oldPos"), request.json.get("target"), "get_movement")
            turn = db.execute("SELECT turn FROM games WHERE id_game = ?", request.json.get("game_id"))
            if request.json.get("target") not in possibilites or  turn[0]["turn"] != request.json.get("orientation") or request.json.get("piece")[0] != request.json.get("orientation")[0] or possibilites == "illegal play":
                return {"code": 400, "message": "bad request", "display": "illegal move"}
            else:
                new_pose = json.dumps(request.json.get("newPos"))
                db.execute("UPDATE games SET position = ? WHERE id_game = ?", new_pose, request.json.get("game_id"))
                return {"code": 200, "message": "OK"}
        elif action == "create_game":
            position = json.dumps(request.json.get("position")) 
            db.execute("INSERT INTO games (state, turn, position) VALUES (?, ?, ?)", 0, "white", position)
            db.execute("INSERT INTO players (id_user, seconds, color) VALUES (?, ?, ?)", session["user_id"], 600, "white")

            game = db.execute("SELECT id_game FROM games ORDER BY id_game DESC LIMIT 1")[0]
            db.execute("INSERT INTO participants (id_game, id_user) VALUES (?, ?)", game["id_game"], session["user_id"])            
            return {"code": 200, "message": "OK", "game_id": game["id_game"]}   
        
        elif action == "start":
            games_id = db.execute("SELECT id_game FROM games WHERE state = 0")
            if len(games_id) == 0:
                return {"code": 300, "message": "NOT ANY GAME CREATED"}
            else:
                db.execute("INSERT INTO participants (id_game, id_user) VALUES (?, ?)",games_id[0]["id_game"], session["user_id"])
                db.execute("INSERT INTO players (id_user, seconds, color) VALUES (?, ?, ?)", session["user_id"], 600, "black")
                db.execute("UPDATE games SET state = 1 WHERE id_game = ?", games_id[0]["id_game"])
                ids = db.execute("SELECT id_user FROM participants WHERE id_game = ?", games_id[0]["id_game"])
                color = db.execute("SELECT color FROM players WHERE id_user = ?", session["user_id"])[0]["color"]
                return {"code": 200, "message": "OK", "game_id": games_id[0]["id_game"], "white_id": ids[0]["id_user"], "black_id": ids[1]["id_user"], "color": color}
        elif action == "leave_game":
            game_id = request.json.get("game_id")
            players = db.execute("SELECT id_user FROM participants WHERE id_game = ?", game_id)
            for player in players:
                db.execute("DELETE FROM players WHERE id_user = ?", player["id_user"])
            db.execute("DELETE FROM games WHERE id_game = ?", game_id)
            db.execute("DELETE FROM participants WHERE id_game = ?", game_id)
            return {"code": 200, "message": "OK"}
        elif action == "change_turn":
            if request.json.get("orientation") == "white":
                    db.execute("UPDATE games SET turn = ? WHERE id_game = ?", "black", request.json.get("game_id"))
                    return {"code": 200, "message": "OK"}
            elif request.json.get("orientation") == "black":
                    db.execute("UPDATE games SET turn = ? WHERE id_game = ?", "white", request.json.get("game_id"))
                    return {"code": 200, "message": "OK"}
        
        elif action == "check_game":
            state = db.execute("SELECT state FROM games WHERE id_game = ?", request.json.get("game_id"))
            if state[0]["state"] == 1:
                white =  db.execute("""SELECT players.id_user FROM players JOIN participants ON players.id_user = participants.id_user
                                    JOIN games ON games.id_game = participants.id_game WHERE players.color = ? AND games.id_game = ?""", "white", request.json.get("game_id"))
                black =  db.execute("""SELECT players.id_user FROM players JOIN participants ON players.id_user = participants.id_user
                                    JOIN games ON games.id_game = participants.id_game WHERE players.color = ? AND games.id_game = ?""", "black", request.json.get("game_id"))
                return {"code": 200, "message": "game has begun", "black_id": black[0]["id_user"], "white_id": white[0]["id_user"]}
            else:
                return {"code": 201, "message": "game hasn't begun"}
            
@app.route("/time", methods=["GET", "POST"])
def time():
    if request.method == "POST":
        game_id = request.json.get("game_id")
        black_id = request.json.get("black_id")
        white_id = request.json.get("white_id")
        turn = db.execute("SELECT turn FROM games WHERE id_game = ?", game_id)
        if turn[0]["turn"] == "black":
            db.execute("UPDATE players SET seconds = seconds - 1 WHERE id_user = ?", black_id)
        elif turn[0]["turn"] == "white":
            db.execute("UPDATE players SET seconds = seconds - 1 WHERE id_user = ?", white_id)
        black_time = db.execute("SELECT seconds FROM players WHERE id_user = ?", black_id)
        black_minutes = floor(black_time[0]["seconds"] / 60)
        black_seconds = black_time[0]["seconds"] % 60

        white_time = db.execute("SELECT seconds FROM players WHERE id_user = ?", white_id)
        white_minutes = floor(white_time[0]["seconds"] / 60)
        white_seconds = white_time[0]["seconds"] % 60

        return {"code": 200, "message": "OK", "black_time": (f"{black_minutes}:{black_seconds}"), "white_time": (f"{white_minutes}:{white_seconds}")}
    
@app.route("/position", methods=["POST", "GET"])
def position():
    if request.method == "POST":
        position = db.execute("SELECT position FROM games WHERE id_game = ?", request.json.get("game_id"))
        if position == []:
            return {"code": 300, "message": "position empty"}
        else:
            new_pose = json.loads(position[0]["position"])
            return {"code": 200, "message": "OK", "position": new_pose}


@app.route("/logging_out")
def loggingOut():
    if request.method == "GET":
        session.clear()
        return {"code": 200, "message": "OK"}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        action = request.json.get("action")
        response = str()
        if action == "logging in":
            users = db.execute("SELECT * FROM users")
            for user in users:
                print(user)
                if (user["username"] == request.json.get("username")) and (check_password_hash(user["password"], request.json.get("password"))):
                    session["user_id"] = user["id"]
                    response = {"code": 200, "message": "OK", "url": url_for("index")}
                    break
            else:
                response = {"code": 400, "message": "bad request", "display": "THE USERNAME OR THE PASSWORD IS INCORRECT", "color": "red"}
            return response


@app.route("/mdp")
def mdp():
    if request.method == "GET":
        return render_template("mdp.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        action = request.json.get("action")
        if action == "inscription":
            username = request.json.get("username")
            password = request.json.get("password")
            confirmation = request.json.get("confirmation")
            response = str()
            inscription = True
            
            if password != confirmation:
                response = {"code": 400, "message": "bad request", "display": "PASSWORD AND CONFIRMATION ARE THE SAME", "color": "red", "field": "confirmation"}
                inscription = False

            names = db.execute("SELECT username FROM users")
            for name in names:
                if username == name["username"]:
                    response = {"code": 400, "message": "bad request", "display": "THAT USERNAME IS ALREADY USED", "color": "red", "field": "username"}
                    inscription = False
            
            if inscription:
                db.execute("INSERT INTO users (username, password, rapid, blitz, bullet) VALUES (?, ?, ?, ?, ?)", username, generate_password_hash(password), 100, 100, 100)
                response = {"code": 200, "message": "OK", "redirect": url_for("login")}

            return response
        
@app.route("/profile")
@login_required
def profile():
    if request.method == "GET":
        user_data = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        return render_template("profile.html", user_data=user_data[0], ranks=RANKS)

@app.route("/infos_players", methods=["GET", "POST"])
@login_required
def infos_players():
    if request.method == "GET":
        return render_template("infos_players.html")
    elif request.method == "POST":
        action = request.json.get("action")
        if action == "get_infos":
            name = request.json.get("name")
            return requests.get(f'https://lichess.org/api/fide/player?q={replace_space(name.lower())}').text
    return {"code": 200, "message": "OK"}
