#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

pairs = []


def connect(db_name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname={}".format(db_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print "Cannot connect to the database."


def deleteMatches():
    """Remove all the match records from the database."""
    db, cursor = connect()
    cursor.execute("DELETE FROM matches WHERE TRUE;")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db, cursor = connect()
    cursor.execute("DELETE FROM players WHERE TRUE;")
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db, cursor = connect()
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
    db, cursor = connect()
    cursor.execute("""INSERT INTO players(name) VALUES (%(p_name)s);""" ,
                   {"p_name": name})
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    db, cursor = connect()
    """
    fetch all the players with the matches and wins data
    """
    cursor.execute("""
    SELECT matches_tracker.id, matches_tracker.name, wins_tracker.wins,
  matches_tracker.matches_played
FROM matches_tracker LEFT JOIN wins_tracker
  ON matches_tracker.id = wins_tracker.id
GROUP BY matches_tracker.id, matches_tracker.name, matches_tracker
.matches_played, wins_tracker.wins
ORDER BY wins_tracker.wins DESC;
    """)
    result = cursor.fetchall()
    db.close()

    return result


def reportMatch(winner, loser, draw=False, tournament=None):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    """
    Check to see if the pairing has already happened before
    """
    db, cursor = connect()
    cursor.execute("""
    SELECT count(*) as pairs
FROM matches
WHERE (matches.winner=%(win)i AND matches.loser=%(los)i)
OR (matches.winner=%(los)i AND matches.loser=%(win)i);
    """ % {
        "win": winner,
        "los": loser
    })

    data = cursor.fetchone()

    if data[0] > 0:
        raise Exception("this pairing has already be matched up!")

    """
    Create the query. If tournament is provided, use tournament id
    """
    query_with_tournament = """
    INSERT INTO matches (winner, loser, draw, tournament_id)
    VALUES (%(w)i, %(l)i, %(d)s, %(t)i)
    """

    query_without_tournament = """
        INSERT INTO matches (winner, loser, draw)
        VALUES (%(w)i, %(l)i, %(d)s)
        """

    """
    Run the query based on inclusion of tournament_id
    """
    if(tournament):
        cursor.execute(query_with_tournament % {
            "w": winner,
            "l": loser,
            "d": draw,
            "t": tournament
        })

    else:
        cursor.execute(query_without_tournament % {
            "w": winner,
            "l": loser,
            "d": draw,
        })

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
    First, lest connect to the table and list the id and name of the players
    ordered in descending number of wins. This way if we select the
    consecutive players, they will be the ones adjacent to him or her in the
    standings.
    """
    cursor = playerStandings()

    """
    toggler toggles the result list and the tuple source. After each 2 records
    in the cursor, the two consecutive records are saved on a tuple and the
    tuple is appended to the result list. The tuple is cleared and the toggler
    starts over.
    """
    toggler = 0
    tupler = []
    result = []
    for row in cursor:

        """
        By the time control reaches here, tupler has one or 0 players so at
        least this player needs to be appended
        """
        tupler.append(row[0])
        tupler.append(row[1])
        toggler += 1

        """
        This is only possible if there are two players in the tupler list. So
        we need to create a tuple from the list and append the tuple to the
        result list. The tupler is then cleared out and toggler reset to 0 so
        that it may
        help in adding two more players.
        """
        if toggler >= 2:
            toggler = 0
            result.append(tuple(tupler))
            tupler = []

    return result
