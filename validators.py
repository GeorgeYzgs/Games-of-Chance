from cs50 import SQL
from flask import Flask, flash, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import parser, results
from datetime import datetime, timedelta

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///gambling.db")


def valid_register(username, password, password2):
    # Ensure username was submitted
    if not username:
        flash("Must Provide Username!", "danger")
        return False

    # Ensure password was submitted
    elif not password:
        flash("Must Provide Password!", "danger")
        return False

    # Ensure second password was submitted
    elif not password2:
        flash("Must Provide Second Password to validate!", "danger")
        return False

    # Ensure username length is correct
    if len(username) < 4 or len(username) > 16:
        flash("Username length should be between 4 and 16 characters", 'danger')
        return False

    if len(password) < 4 or len(password) > 20:
        flash("Password length should be between 4 and 20 characters", 'danger')
        return False

    # Ensure username is available
    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username.casefold())
    if len(rows) != 0:
        flash("Username unavailable!", "danger")
        return False

    # Ensure the two given passwords match
    if password != password2:
        flash("Passwords do not match!", "danger")
        return False

    return True


def valid_login(username, password):

    # Ensure username was submitted
    if not username:
        flash("Must Provide Username!", "danger")
        return False

    # Ensure password was submitted
    elif not password:
        flash("Must Provide Password!", "danger")
        return False

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                      username=username.casefold())

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        flash("Invalid username and/or password!", 'danger')
        return False

    # Remember which user has logged in
    session["user_id"] = rows[0]["id"]
    session['user_cash'] = rows[0]['cash']
    return True


def valid_cash(amount):

    # Ensures the user provided an amount, back - end validation
    if not amount:
        flash("Must provide an amount", 'danger')
        return False

    money = int(amount)
    # Ensures amount is positive in the back - end too
    if money < 1 or money > 1000:
        flash("Must provide a positive amount up to 1000 euros", 'danger')
        return False

    return True


def valid_joker(one, two, three, four, five, six):

    # Ensures user provided 5 + 1 numbers
    if (not one or not two or not three or not four or not five or not six):
        flash("Must provide 5 numbers and a Joker number", 'danger')
        return False

    # Ensures user provided 5 unique numbers by creating a set
    set_Numbers = {int(one), int(two), int(three), int(four), int(five)}
    if len(set_Numbers) != 5:
        flash("Each number must be unique & from 1 to 45", 'danger')
        return False

    # Ensures each number is in valid range
    for number in set_Numbers:
        if number < 1 or number > 45:
            flash("Each number must be within 1 to 45", 'danger')
            return False

    # Ensures joker is in valid range
    joker = int(six)
    if joker < 1 or joker > 20:
        flash("Joker must be within 1 to 20", 'danger')
        return False

    # Checks users funds
    cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])[0]['cash']
    if cash < 0.5:
        flash("Insufficient funds", 'danger')
        return False

    # Ensures that participation is still open
    game = parser(5104, 'active')
    draw_time_limit = game['drawTime'] + timedelta(hours=-1)
    if datetime.now() > draw_time_limit:
        flash("Participation is now closed, draw in less than 1 hour", 'danger')
        return False

    return {
        'game_id': game['game_id'],
        "drawTime": game['drawTime']
    }


def valid_lotto(one, two, three, four, five, six, seven):

    # Ensures user provided 6 + 1 numbers
    if (not one or not two or not three or not four or not five or not six or not seven):
        flash("Must provide 6 numbers and a Bonus number", 'danger')
        return False

    # Ensures user provided 7 unique numbers by creating a set
    set_Numbers = {int(one), int(two), int(three), int(four), int(five), int(six), int(seven)}
    if len(set_Numbers) != 7:
        flash("Each number must be unique & from 1 to 49", 'danger')
        return False

    # Ensures each number is in valid range
    for number in set_Numbers:
        if number < 1 or number > 49:
            flash("Each number must be within 1 to 49", 'danger')
            return False

    # Checks users funds
    cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])[0]['cash']
    if cash < 0.5:
        flash("Insufficient funds", 'danger')
        return False

    # Ensures that participation is still open
    game = parser(5103, 'active')
    draw_time_limit = game['drawTime'] + timedelta(hours=-1)
    if datetime.now() > draw_time_limit:
        flash("Participation is now closed, draw in less than 1 hour", 'danger')
        return False

    return {
        'game_id': game['game_id'],
        "drawTime": game['drawTime']
    }


def valid_proto(one, two, three, four, five, six, seven):

    # Ensures user provided 6 + 1 numbers
    if (not one or not two or not three or not four or not five or not six or not seven):
        flash("Must provide 7 numbers", 'danger')
        return False

    numbers = (int(one), int(two), int(three), int(four), int(five), int(six), int(seven))
    # Ensures each number is in valid range
    for number in numbers:
        if number < 0 or number > 9:
            flash("Each number must be within 0 to 9", 'danger')
            return False

    # Checks users funds
    cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])[0]['cash']
    if cash < 0.5:
        flash("Insufficient funds", 'danger')
        return False

    # Ensures that participation is still open
    game = parser(2101, 'active')
    draw_time_limit = game['drawTime'] + timedelta(hours=-1)
    if datetime.now() > draw_time_limit:
        flash("Participation is now closed, draw in less than 1 hour", 'danger')
        return False

    return {
        'game_id': game['game_id'],
        "drawTime": game['drawTime']
    }


def valid_check(id, game_id, game, numbers):

    # Maps games to web service game id
    # Checks your numbers against the drawn numbers and updates database entry, appoints winnings
    if game == "Joker":
        check = results(5104, game_id)
        if not check:
            flash("This game has not been drawn yet!", 'danger')
            return False
        earnings = check_joker(check, numbers)
    elif game == "Lotto":
        check = results(5103, game_id)
        if not check:
            flash("This game has not been drawn yet!", 'danger')
            return False
        earnings = check_lotto(check, numbers)
    elif game == "Proto":
        check = results(2101, game_id)
        if not check:
            flash("This game has not been drawn yet!", 'danger')
            return False
        earnings = check_proto(check, numbers)

    db.execute("UPDATE games SET isFinished = 1, earnings = :earnings WHERE id = :gid", gid=id, earnings=earnings)
    if earnings != 0:
        db.execute("UPDATE users SET cash = cash + :cash WHERE id = :id", cash=earnings, id=session["user_id"])
        session['user_cash'] += earnings


def check_joker(check, numbers):

    numbers = numbers.split("-")
    counter = 0
    bonus = int(numbers[-1])
    for number in numbers[:-1]:
        if int(number) in check['numbers']['list']:
            counter += 1
    if bonus == check['numbers']['bonus'][0]:
        joker = True
    else:
        joker = False

    earnings = 0
    if counter == 5 and joker:
        earnings = check['prizes'][0]['jackpot']
        flash("YOU HAVE WON THE JACKPOT!!", 'success')
    elif counter == 5 and not joker:
        earnings = check['prizes'][1]['jackpot']
        flash("YOU HAVE WON A GRAND PRIZE!", 'success')
    elif counter == 4 and joker:
        earnings = 2500.00
        flash("You have won 2.500 euros!", 'success')
    elif counter == 4 and not joker:
        earnings = 50.00
        flash("You have won 50 euros!", 'success')
    elif counter == 3 and joker:
        earnings = 50.00
        flash("You have won 50 euros!", 'success')
    elif counter == 3 and not joker:
        earnings = 2.00
        flash("You have won 2 euros!", 'success')
    elif counter == 2 and joker:
        earnings = 2.00
        flash("You have won 2 euros!", 'success')
    elif counter == 1 and joker:
        earnings = 1.50
        flash("You have won 1,5 euros!", 'success')
    else:
        flash("You did not win anything, better luck next time", 'primary')

    return earnings


def check_lotto(check, numbers):

    numbers = numbers.split("-")
    counter = 0
    bonus = int(numbers[-1])
    for number in numbers[:-1]:
        if int(number) in check['numbers']['list']:
            counter += 1
    if bonus == check['numbers']['bonus'][0]:
        joker = True
    else:
        joker = False

    earnings = 0
    if counter == 6:
        earnings = check['prizes'][0]['jackpot']
        flash("YOU HAVE WON THE JACKPOT!!", 'success')
    elif counter == 5 and joker:
        earnings = 50000.00
        flash("YOU HAVE WON 50.000 EUROS!", 'success')
    elif counter == 5 and not joker:
        earnings = 1500.00
        flash("You have won 1.500 euros!", 'success')
    elif counter == 4:
        earnings = 30.00
        flash("You have won 30 euros!", 'success')
    elif counter == 3:
        earnings = 1.50
        flash("You have won 1,5 euros!", 'success')
    else:
        flash("You did not win anything, better luck next time", 'primary')

    return earnings


def check_proto(check, numbers):

    numbers = numbers.replace("-", "")
    drawn = ''
    for number in check['numbers']['list']:
        drawn += str(number)

    earnings = 0
    if numbers == drawn:
        earnings = check['prizes'][0]['jackpot']
        flash("YOU HAVE WON THE JACKPOT!!", 'success')
    elif numbers[:-1] == drawn[:-1] or numbers[1:] == drawn[1:]:
        earnings = 25000.0
        flash("YOU HAVE WON 25.000 EUROS!", 'success')
    elif numbers[:-2] == drawn[:-2] or numbers[2:] == drawn[2:]:
        earnings = 2500.00
        flash("You have won 2.500 euros!", 'success')
    elif numbers[:-3] == drawn[:-3] or numbers[3:] == drawn[3:]:
        earnings = 250.00
        flash("You have won 250 euros!", 'success')
    elif numbers[:-4] == drawn[:-4] or numbers[4:] == drawn[4:]:
        earnings = 25.00
        flash("You have won 25 euros!", 'success')
    elif numbers[:-5] == drawn[:-5] or numbers[5:] == drawn[5:]:
        earnings = 2.50
        flash("You have won 2,5 euros!", 'success')
    else:
        flash("You did not win anything, better luck next time", 'primary')

    return earnings