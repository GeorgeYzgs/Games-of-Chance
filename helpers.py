import requests
import urllib.parse
from datetime import datetime, timedelta

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


# Creates a decorator @ that prevents users from accessing certains html pages wihout being logged in
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Formats numeric values to 2 decimals and adds the EUR sign.
def eur(value):
    """Format value as EUR."""
    return f"{value:,.2f} €"


# Attempts to connect to OPAP api to retrieve game data.
def parser(game_id, game):

    # Contact API
    try:
        response = requests.get(f"https://api.opap.gr/draws/v3.0/{game_id}/last-result-and-active")
        response.raise_for_status()
        quote = response.json()
    except requests.RequestException:
        return None

    # Parse response
    if game == 'last':
        try:
            quote = response.json()
            return {
                "game_id": quote[game]["drawId"],
                "drawTime": datetime.fromtimestamp(quote[game]["drawTime"] / 1000),
                "numbers": quote[game]['winningNumbers'],
                "prizes": quote[game]["prizeCategories"],
                "players": quote[game]['wagerStatistics']['columns']
            }
        except (KeyError, TypeError, ValueError):
            return None

    if game == 'active':
        try:
            quote = response.json()
            return {
                "game_id": quote[game]["drawId"],
                "drawTime": datetime.fromtimestamp(quote[game]["drawTime"] / 1000),
            }
        except (KeyError, TypeError, ValueError):
            return None


# Attempts to connect to OPAP api to retrieve game data.
def results(game_id, game):

    # Contact API
    try:
        response = requests.get(f"https://api.opap.gr/draws/v3.0/{game_id}/{game}")
        response.raise_for_status()
        quote = response.json()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            'game': quote['gameId'],
            "game_id": quote["drawId"],
            "drawTime": datetime.fromtimestamp(quote["drawTime"] / 1000),
            "numbers": quote['winningNumbers'],
            "prizes": quote["prizeCategories"],
            "players": quote['wagerStatistics']['columns']
        }
    except (KeyError, TypeError, ValueError):
        return None
