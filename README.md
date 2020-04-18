# Final Project

CS50 Introduction to Computer Science

# GeorgeYzgs

The goal of this project was to create a website consuming OPAP's API conducting games of chance.
OPAP is the Greek Organisation of Football Prognostics and their web services are offered for free.

Most of the content is locked to users that are not logged in, so a user should register and then login.

The home page, once logged in, displays active games that a user has placed.
Once a game is drawn (by checking the time compared to the game's draw time) a button
will appear next to the game which will check whether a user has won a prize.
The game is thereafter considered inactive and is moved to the history page and the user's balance will be updated
if they have won a prize.

In addition, a user can view their balance on the top right corner, and can add to it by clicking the add funds link and
filling the form.

The three gaming pages, joker - lotto - proto offer information about each game about how it is played, winning
conditions and the ability to check the last drawn game. Furthermore a user can play a game by filling each form.
Once successful a new game will be listed under the home page.

Finally the search page allows the user to search for any of the three games' older draws.

Warning: Due to the pandemic OPAP has halted Lotto & Proto games,
so you will be unable to play as their API is not being updated.
Tests have been done with dummy data to make sure the application works as intended.

Good luck!

