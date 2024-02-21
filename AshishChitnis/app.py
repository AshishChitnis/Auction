import os

from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import time

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///auction.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        rows = db.execute("SELECT * FROM users;")
        print(rows)
        for row in rows:
            if username == row["username"] or username == "":
                return apology("Sorry, please enter a unique user name")
        if password == "" or confirmation == "" or password != confirmation:
            return apology(
                "Sorry, password and confirmation need to match and cannot be blank"
            )
        else:
            hash = generate_password_hash(password, method="pbkdf2", salt_length=16)
            db.execute(
                "INSERT INTO users(username, hash) VALUES(?, ?);", username, hash
            )
            return render_template(
                "register.html",
                username="username",
                password="password",
                confirmation="confirmation",
                message="You are successfully registered",
            )
    return render_template(
        "register.html",
        username="username",
        password="password",
        confirmation="confirmation",
    )
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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        print(rows)
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """New Feature: Allow user to change password"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure orig_passowrd is submitted
        if not request.form.get("orig_pw"):
            return apology("must provide current password", 403)
        # Query database for hash value
        hash_list = db.execute(
            "SELECT hash FROM users WHERE id = ?;", session["user_id"]
        )

        # Ensure username exists and password is correct
        if not check_password_hash(hash_list[0]["hash"], request.form.get("orig_pw")):
            return apology("Entry does not match your current password", 403)
        # Ensure original password was submitted
        elif not request.form.get("new_pw"):
            return apology("must provide password", 403)
        elif not request.form.get("confirmation"):
            return apology("Please confirm passowrd")
        else:
            new_pw = request.form.get("new_pw")
            confirmation = request.form.get("confirmation")
        if new_pw != confirmation:
            return apology("New password does not match confirmation")
        else:
            hash_value = generate_password_hash(new_pw, method="pbkdf2", salt_length=16)
            db.execute(
                "UPDATE users SET hash = ? WHERE id=?;", hash_value, session["user_id"]
            )
            return render_template(
                "password.html",
                orig_pw="orig_pw",
                new_pw="new_pw",
                confirmation="confirmation",
                message="Your password has been successfully changed",
            )
    return render_template(
        "password.html", orig_pw="orig_pw", new_pw="new_pw", confirmation="confirmation"
    )


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")



@app.route('/')
@login_required

def index():
    rows_status = db.execute("SELECT items.item_id, status, start_time, end_time, MAX(bid_time) as last_time, current_bid_price, bidder_id, buyer_id, seller_id FROM items JOIN history on items.item_id = history.item_id GROUP BY items.item_id")
    current_time = datetime.now()
    user_cash_hold=db.execute("SELECT cash_hold_for_bid FROM users")
    print("User cash hold: " , user_cash_hold)
    for row in rows_status:
        end_time = datetime.strptime(row['end_time'], '%Y-%m-%d %H:%M:%S')
        id_bidder=int(row["bidder_id"])
        id_item=int(row["item_id"])
        if end_time > current_time:
            pass
        else:
            if (row['status'] == "active"):
                bought_price = float(row['current_bid_price'])
                print("Bought price: ", bought_price)
                db.execute('UPDATE items SET status = ? WHERE item_id=?', "complete", id_item)
                if id_bidder !=0:
                    cash_b4_buy = float(db.execute('SELECT cash_hold_for_bid FROM users WHERE id=?', id_bidder)[0]['cash_hold_for_bid'])
                    cash_hold = cash_b4_buy - bought_price
                    id_seller = row['seller_id']
                    cash_seller = db.execute('SELECT cash FROM users WHERE id=?', id_seller)[0]['cash']
                    cash_seller = cash_seller + bought_price
                    db.execute('UPDATE users SET cash=? WHERE id=?', cash_seller, id_seller)
                    db.execute('UPDATE items SET buyer_id = ? WHERE item_id=?', id_bidder, id_item)
                    db.execute('UPDATE items SET bought_price = ? WHERE item_id=?', bought_price, id_item)
                    db.execute('UPDATE users SET cash_hold_for_bid=? WHERE id=?', cash_hold, id_bidder)

                if 'user_id' in session and session['user_id'] == row['buyer_id']:
                    flash("Your bid for item id {} was successful".format(row['item_id'], 'success'))
                    message="Your bid for item id {} was successful".format(row['item_id'])
                if 'user_id' in session and session['user_id'] == row['seller_id']:
                    if id_bidder != 0:
                        flash("Your auctioned item id {} has been sold".format(row['item_id'], 'success'))
                    else:
                        flash("Your auctioned item id {} did not get a bid and has been archived".format(row['item_id'], 'success'))
        items = db.execute("SELECT items.item_id, item_name, class, desc, status, MAX(current_bid_price) as last_price, end_time, seller_id FROM items JOIN history on items.item_id = history.item_id WHERE status=? GROUP BY items.item_id", "active")
        user_id = db.execute("SELECT id from users WHERE id=?", session['user_id'])[0]['id']
        message = "Welcome to the Auction website"
    return render_template("index.html", items=items, user_id=user_id, message = message)


@app.route('/bid/<int:item_id>', methods=['POST'])
def bid(item_id):
    bidderid = session["user_id"]
    try:
        bid_amount = float(request.form['bid_amount'])
    except:
        return apology("Enter a valid bid")
    now = datetime.now()
    time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")

    last_bid = db.execute('SELECT current_bid_price FROM history WHERE item_id = ?', (item_id))[-1]['current_bid_price']
    if bid_amount > last_bid:
        cash = db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])
        available_cash = float(cash[0]["cash"])
        if available_cash > bid_amount:
            last_bidder_id = db.execute('SELECT bidder_id FROM history WHERE item_id = ?', (item_id))[-1]['bidder_id']
            if last_bidder_id == 0:
                pass
            else:
                last_bidder_cash = float(db.execute('SELECT cash FROM users WHERE id=?', last_bidder_id)[0]['cash'])
                last_bidder_cash_hold = db.execute('SELECT cash_hold_for_bid FROM users WHERE id=?', last_bidder_id)[0]['cash_hold_for_bid']
                if last_bidder_cash_hold is None:
                    last_bidder_cash_hold = 0.0
                else:
                    last_bidder_cash_hold = float(last_bidder_cash_hold)
                last_bidder_cash = last_bidder_cash + last_bid
                last_bidder_cash_hold = last_bidder_cash_hold - last_bid
                db.execute('UPDATE users SET cash=?, cash_hold_for_bid=? WHERE id=?', last_bidder_cash, last_bidder_cash_hold, last_bidder_id)
            #New bid - update cash position
            available_cash = available_cash - bid_amount
            cash_hold = db.execute('SELECT cash_hold_for_bid FROM users WHERE id=?', session['user_id'])[0]['cash_hold_for_bid']
            try:
                cash_hold = float(cash_hold) + bid_amount
            except:
                cash_hold = float(bid_amount)
            db.execute('UPDATE users SET cash=?, cash_hold_for_bid=? WHERE id=?', available_cash, cash_hold, bidderid )
            db.execute('INSERT INTO history(item_id, bidder_id, current_bid_price, bid_time) VALUES (?, ?, ?, ?)', item_id, bidderid, bid_amount, time_stamp)
            flash("Your bid has been placed")
        else:
            flash("Sorry, you do not have enough cash avaialable for this bid" )
    else:
        flash("Sorry, your bid is lower than the current bid")
    return redirect(url_for('index'))

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Add Item for Auction"""
    if request.method == "POST":
      item_name = request.form['item_name']
      item_class = request.form['item_class']
      item_description = request.form['item_description']
      item_price = request.form['item_price']
      if float(item_price) < 0:
            flash('Please enter a valid positive number for the price.')
            return redirect('/sell')
      duration = request.form['duration']
      if float(duration) < 0:
            flash('Please enter a valid positive number for the duration.')
            return redirect('/sell')
      duration_hours=int(duration)
      status = "active"
      now = datetime.now()
      time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")
      endtime = now + timedelta(hours=duration_hours)
      db.execute("INSERT INTO items (item_name, class, desc, status, seller_id, start_price, start_time, end_time) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", item_name, item_class, item_description, status, session["user_id"], item_price, time_stamp, endtime)
      itemid = db.execute("SELECT item_id FROM items ORDER BY item_id DESC LIMIT 1;")[0]['item_id']
      print(itemid)
      bid_price = db.execute("SELECT start_price FROM items WHERE item_id = ?", itemid)[0]['start_price']
      db.execute("INSERT INTO history (item_id, current_bid_price, bid_time, bidder_id) VALUES (?, ?, ?, ?)", itemid, bid_price, time_stamp, 0)
    return render_template("sell.html")

@app.route('/history_my_bids')
@login_required
def history_my_bids():
    items = db.execute("SELECT items.item_id, item_name, class, desc, status, current_bid_price, end_time FROM items JOIN history on items.item_id = history.item_id  WHERE bidder_id=? ORDER BY items.item_id", session["user_id"])
    print(items)
    return render_template("history_my_bids.html", items=items)

@app.route('/history_my_auctioned_items')
@login_required
def history_my_auctioned_items():
    items = db.execute("SELECT items.item_id, item_name, class, desc, status, current_bid_price, end_time FROM items JOIN history on items.item_id = history.item_id  WHERE seller_id=? and status = ? ORDER BY items.item_id", session["user_id"], "active")
    print(items)
    return render_template("history_my_auctioned_items.html", items=items)

@app.route('/history_my_bought_items')
@login_required
def history_my_bought_items():
    items = db.execute("SELECT items.item_id, item_name, class, desc, bought_price FROM items WHERE buyer_id=? ORDER BY items.item_id", session["user_id"])
    print(items)
    return render_template("history_my_bought_items.html", items=items)

@app.route('/history_my_sold_items')
@login_required
def history_my_sold_items():
    items = db.execute("SELECT items.item_id, item_name, class, desc, bought_price FROM items WHERE status=? AND seller_id=? AND buyer_id <> 0 ORDER BY items.item_id", "complete", session["user_id"])
    print(items)
    return render_template("history_my_sold_items.html", items=items)

@app.route('/history_all_sold_items')
@login_required
def history_all_sold_items():
    items = db.execute("SELECT items.item_id, item_name, class, desc, bought_price FROM items WHERE buyer_id <> 0 ORDER BY items.item_id")
    print(items)
    return render_template("history_all_sold_items.html", items=items)

@app.route('/my_cash')
@login_required
def my_cash():
    items = db.execute("SELECT cash, cash_hold_for_bid FROM users WHERE id=?", session['user_id'])
    return render_template("my_cash.html", items=items)
