-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- We only need one table for this project.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

-- Players table will hold the players id and description(name)
CREATE TABLE players (
  id SERIAL PRIMARY KEY,
  name TEXT
);

-- Tournaments table will hold the tournaments id and description(name)
CREATE TABLE tournament (
  id SERIAL PRIMARY KEY,
  name TEXT
);

-- Matches table will hold the references to the tournament_id, winning
-- and losing player ids, as well as if it is a draw
CREATE TABLE matches (
  id SERIAL PRIMARY KEY,
  tournament_id INTEGER REFERENCES tournament(id),
  winner INTEGER REFERENCES players(id),
  loser INTEGER REFERENCES players(id),
  draw BOOLEAN
);

CREATE VIEW wins_tracker
  AS
  SELECT players.id, players.name, COUNT(matches.winner) AS wins
  FROM players LEFT JOIN matches
    ON players.id = matches.winner
  GROUP BY players.id;

CREATE VIEW matches_tracker
  AS
  SELECT players.id, players.name, COUNT(matches) AS matches_played
  FROM players LEFT JOIN matches
    ON players.id = matches.winner OR players.id = matches.loser
  GROUP BY players.id;