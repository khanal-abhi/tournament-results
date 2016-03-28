#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

pairs = []

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    cursor = db.cursor();
    cursor.execute("""
    UPDATE players SET matches=0, wins=0
    WHERE TRUE;
    """)
    db.commit()
    db.close()

def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    cursor = db.cursor()
    cursor.execute("DELETE FROM players WHERE TRUE;")
    db.commit()
    db.close()

def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    cursor = db.cursor()
    cursor.execute("SELECT count(*) AS count FROM players;")
    result = cursor.fetchone()
    result = result[0]
    db.commit()
    db.close()

    return result


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """

    """
    Here we will use the pyformat to prevent SQL injection.
    """
    db = connect()
    cursor = db.cursor()
    cursor.execute("INSERT INTO players (name, matches, wins) VALUES (%(p_name)s, 0, 0);", {"p_name": name})
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    db = connect()
    cursor = db.cursor()
    """
    fetch all the players with the matches and wins data
    """
    cursor.execute("SELECT id, name, wins, matches FROM players;")
    result = cursor.fetchall()
    db.close()

    return result


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    """
    Raise an exception if the pair has already competed
    """
    pair = (winner, loser)
    if pairs.__contains__(pair):
        raise Exception("pair already competed!")

    """
    First, lets increment the wins and matches for the winner
    """
    db = connect()
    cursor = db.cursor()
    cursor.execute("""
    UPDATE players
    SET
    matches = matches + 1, wins = wins + 1
    WHERE
    id = %(winner)i""" % {"winner": winner})

    """
    Next, lets increment the matches for the loser
    """

    cursor.execute("""
        UPDATE players
        SET
        matches = matches + 1
        WHERE
        id = %(loser)i""" % {"loser": loser})

    pairs.append((winner, loser))

    db.commit()
    db.close()



def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    """
    First, lest connect to the table and list the id and name of the players ordered in descending number of wins. This
    way if we select the consecutive players, they will be the ones adjacent to him or her in the standings.
    """
    db = connect()
    cursor = db.cursor()
    cursor.execute("""
    SELECT id, name
    FROM players
    ORDER BY wins DESC;
    """)

    """
    toggler toggles the result list and the tuple source. After each 2 records in the cursor, the two consecutive records
    are saved on a tuple and the tuple is appended to the result list. The tuple is cleared and the toggler starts over.
    """
    toggler = 0
    tupler = []
    result = []
    for row in cursor:

        """
        By the time control reaches here, tupler has one or 0 players so at least this player needs to be appended
        """
        tupler.append(row[0])
        tupler.append(row[1])
        toggler += 1

        """
        This is only possible if there are two players in the tupler list. So wee need to create a tuple from the list
        and append the tuple to the result list. The tupler is then cleared out and toggler reset to 0 so that it may
        help in adding two more players.
        """
        if toggler >= 2:
            toggler = 0
            result.append(tuple(tupler))
            tupler = []


    db.close()
    return result
