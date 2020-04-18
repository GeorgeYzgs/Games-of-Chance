from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from validators import valid_register, valid_login, valid_cash, valid_joker, valid_check, valid_lotto, valid_proto
from helpers import apology, login_required, eur, parser, results
from datetime import datetime


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["eur"] = eur

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///gambling.db")

last_joker_game = {}
last_lotto_game = {}
last_proto_game = {}


@app.route('/refreshJoker')
def lastjoker():
    global last_joker_game
    last_joker_game = parser(5104, 'last')
    flash("Last joker game updated!", 'success')
    return render_template('/joker.html', draw=last_joker_game)


@app.route('/refreshLotto')
def lastlotto():
    global last_lotto_game
    last_lotto_game = parser(5103, 'last')
    flash("Last lotto game updated!", 'success')
    return render_template('/lotto.html', draw=last_lotto_game)


@app.route('/refreshProto')
def lastproto():
    global last_proto_game
    last_proto_game = parser(2101, 'last')
    flash("Last lotto game updated!", 'success')
    return render_template('/proto.html', draw=last_proto_game)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not valid_login(request.form.get("username"), request.form.get("password")):
            return redirect('/login')

        flash("You have been logged in!", 'primary')
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not valid_register(request.form.get('username'), request.form.get("password"), request.form.get("password2")):
            return redirect("/register")

        # Inserts user into db
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                   username=request.form.get("username").casefold(),
                   hash=generate_password_hash(request.form.get("password")))

        flash("Registered succesfully!", 'success')
        flash("You have been gifted 10 euros as a sign up bonus!", 'primary')
        # Redirect user to login page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/")
@login_required
def index():

    # Converts the date string back to date-time for the visibility of check button on index
    games = db.execute('SELECT * FROM games where user_id = :uid AND isFinished = 0', uid=session['user_id'])
    for game in games:
        game['draw_time'] = datetime.strptime(game['draw_time'], '%Y-%m-%d %H:%M:%S')

    return render_template("index.html", games=games, time=datetime.now())


@app.route("/history")
@login_required
def history():

    games = db.execute('SELECT * FROM games where user_id = :uid AND isFinished = 1', uid=session['user_id'])
    return render_template("history.html", games=games)


@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():
    """Allows a user to deposit more cash"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        if not valid_cash(request.form.get("amount")):
            return redirect('/cash')

        # Update database
        cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])[0]['cash']
        new_balance = cash + int(request.form.get("amount"))
        db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=new_balance, id=session["user_id"])
        session['user_cash'] = new_balance

        flash("Funds added!", 'success')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("cash.html")


@app.route("/joker", methods=["GET", "POST"])
@login_required
def joker():
    """Joker Game main page"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        first = int(request.form.get("first"))
        second = int(request.form.get("second"))
        third = int(request.form.get("third"))
        fourth = int(request.form.get("fourth"))
        fifth = int(request.form.get("fifth"))
        joker = int(request.form.get("joker"))

        game = valid_joker(first, second, third, fourth, fifth, joker)
        if not game:
            return redirect('/joker')

        # Converts number into a string for normalization in database, can be split('-') later
        # Casting to int removes trailing 0s
        numbers = str(first) + "-" + str(second) + "-" + str(third)  \
            + "-" + str(fourth) + "-" + str(fifth) + "-" + str(joker)

        # Inserts new game into database
        db.execute('INSERT INTO games (user_id, game_id, numbers, game, draw_time) VALUES (:uid,:gid,:numbers,:game,:drawtime)',
                   uid=session['user_id'], gid=game['game_id'], numbers=numbers, game='Joker', drawtime=game['drawTime'])

        # Update database the price of each game is 0.5 euros
        price = 0.5
        db.execute("UPDATE users SET cash = cash - :cash WHERE id = :id", cash=price, id=session["user_id"])
        session['user_cash'] -= 0.5

        flash("Numbers submitted, Good Luck!", 'success')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("joker.html", draw=last_joker_game)


@app.route("/lotto", methods=["GET", "POST"])
@login_required
def lotto():
    """Lotto Game main page"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        first = int(request.form.get("first"))
        second = int(request.form.get("second"))
        third = int(request.form.get("third"))
        fourth = int(request.form.get("fourth"))
        fifth = int(request.form.get("fifth"))
        sixth = int(request.form.get("sixth"))
        bonus = int(request.form.get("bonus"))

        game = valid_lotto(first, second, third, fourth, fifth, sixth, bonus)
        if not game:
            return redirect('/lotto')

        # Converts number into a string for normalization in database, can be split('-') later
        # Casting to int removes trailing 0s
        numbers = str(first) + "-" + str(second) + "-" + str(third) \
            + "-" + str(fourth) + "-" + str(fifth) + "-" + str(sixth) + "-" + str(bonus)

        # Inserts new game into database
        db.execute('INSERT INTO games (user_id, game_id, numbers, game, draw_time) VALUES (:uid,:gid,:numbers,:game,:drawtime)',
                   uid=session['user_id'], gid=game['game_id'], numbers=numbers, game='Lotto', drawtime=game['drawTime'])

        # Update database the price of each game is 0.5 euros
        price = 0.5
        db.execute("UPDATE users SET cash = cash - :cash WHERE id = :id", cash=price, id=session["user_id"])
        session['user_cash'] -= 0.5

        flash("Numbers submitted, Good Luck!", 'success')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("lotto.html", draw=last_lotto_game)


@app.route("/proto", methods=["GET", "POST"])
@login_required
def proto():
    """Proto Game main page"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        first = int(request.form.get("first"))
        second = int(request.form.get("second"))
        third = int(request.form.get("third"))
        fourth = int(request.form.get("fourth"))
        fifth = int(request.form.get("fifth"))
        sixth = int(request.form.get("sixth"))
        seventh = int(request.form.get("seventh"))

        game = valid_proto(first, second, third, fourth, fifth, sixth, seventh)
        if not game:
            return redirect('/proto')

        # Converts number into a string for normalization in database, can be split('-') later
        # Casting to int removes trailing 0s
        numbers = str(first) + "-" + str(second) + "-" + str(third) \
            + "-" + str(fourth) + "-" + str(fifth) + "-" + str(sixth) + "-" + str(seventh)

        # Inserts new game into database
        db.execute('INSERT INTO games (user_id, game_id, numbers, game, draw_time) VALUES (:uid,:gid,:numbers,:game,:drawtime)',
                   uid=session['user_id'], gid=game['game_id'], numbers=numbers, game='Proto', drawtime=game['drawTime'])

        # Update database the price of each game is 0.5 euros
        price = 0.5
        db.execute("UPDATE users SET cash = cash - :cash WHERE id = :id", cash=price, id=session["user_id"])
        session['user_cash'] -= 0.5

        flash("Numbers submitted, Good Luck!", 'success')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("proto.html", draw=last_proto_game)


@app.route('/check', methods=['POST'])
@login_required
def check():

    valid_check(request.form.get("id"), request.form.get("game_id"), request.form.get("game"), request.form.get("numbers"))
    return redirect("/")


@app.route('/search', methods=["GET", "POST"])
@login_required
def search():
    """Game Search Page"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        game = results(int(request.form.get('game_id')), int(request.form.get('game')))
        if not game:
            flash("No such game was found!", 'danger')
            return redirect("/search")

        flash("Game Loaded!", 'primary')
        return render_template("/search.html", draw=game)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("search.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

