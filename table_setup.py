from dbConnect import dbConnect

# Use "heroku pg:reset DATABASE" to clear everything from the database before
#  running this.
# Run with "heroku run python table_setup.py"


playerDef = """
    CREATE TABLE players (

        player_id      serial         PRIMARY KEY,
        name           varchar(30)    UNIQUE NOT NULL,
        join_date      timestamp

    );
"""

monthlyConfig = """
    CREATE TABLE monthlyConfig (
        month_id       serial          PRIMARY KEY,
        firstDay       timestamp,
        wizard         integer         REFERENCES players,
        jester         integer         REFERENCES players,
        league_members JSON
    );
"""

gamesDef = """
    CREATE TABLE games (

        game_id        serial         PRIMARY KEY,
        month_id       integer        REFERENCES monthlyConfig,
        date           timestamp
        league_game    boolean

    );
"""

scoresDef = """
    CREATE TABLE scores (
        player_id      integer        REFERENCES players,
        game_id        integer        REFERENCES games,
        score          smallint,
        points         smallint,
        tiebreak       smallint,

        PRIMARY KEY(game_id,player_id)
    );
"""

datedScores = """
    CREATE VIEW datedScores AS
    SELECT * FROM games INNER JOIN scores
    USING (game_id)
"""


conn = dbConnect()

cur = conn.cursor()

cur.execute(playerDef)
cur.execute(monthlyConfig)
cur.execute(gamesDef)
cur.execute(scoresDef)
cur.execute(datedScores)

conn.commit()

cur.execute("""SELECT relname FROM pg_class
            WHERE relkind='r' AND relname !~ '^(pg_|sql_)';""")

print("created:")
print(cur.fetchall())
