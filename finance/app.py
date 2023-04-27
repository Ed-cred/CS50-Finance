import os

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    stock_info = db.execute("SELECT symbol, SUM(shares) AS shares FROM purchase WHERE personid = ? GROUP BY symbol", user_id)
    current_price = []
    for key in stock_info:
        stock = lookup(key["symbol"])
        current_price.append(stock["price"])
    cash_get = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    current_cash = cash_get[0]["cash"]
    return render_template("index.html", stock_info=stock_info, price = current_price, cash=current_cash)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        stock = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        user_id = session["user_id"]
        if not stock:
            return apology("Please input a symbol", 403)
        elif lookup(stock) == None:
            return apology("The stock you have requested is unavailable", 403)
        elif shares <= 0:
            return apology("The number of shares must be a positive integer greater than 0", 403)
        stock_stats = lookup(stock)
        price = stock_stats["price"]
        user_cash = db.execute("SELECT cash FROM users,sqlite_sequence WHERE users.id == sqlite_sequence.seq")
        if (price * shares) > user_cash[0]["cash"]:
            return apology("Insufficient funds to complete transaction", 403)
        date_of_purchase = datetime.now()
        db.execute("INSERT INTO purchase (symbol, stock_price, date_of_purchase, shares, personid) VALUES(?, ?, ?, ?, ?)", stock, price, date_of_purchase, shares, user_id)
        cash_update = user_cash[0]["cash"] - (price * shares)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_update, user_id)
        flash("Transaction successful!")
        return redirect("/")
    else:
        return render_template("buy.html")







@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        option = request.form.get("symbol")
        stock = lookup(option)
        if stock == None:
            return apology("Requested stock is unavailable", 403)
        return render_template("quoted.html", stock=stock)
    else:
        return render_template("quote.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        user = request.form.get("username")
        passw = request.form.get("password")
        confirm = request.form.get("confirmation")
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        elif not request.form.get("confirmation"):
            return apology("please confirm your password", 403)
        elif passw != confirm:
            return apology("passwords must match", 403)
        pwhash = generate_password_hash(passw, method='pbkdf2:sha256', salt_length=8)
        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", user, pwhash)
        except:
            return apology("username is already taken", 403)
        session["user_id"] = new_user
        return redirect("/login")
    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol or lookup(symbol) == None :
            return apology("Please input a valid symbol")

        return redirect("/")
    else:
        return render_template("sell.html")
