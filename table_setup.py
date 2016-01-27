from dbConnect import dbConnect

playerDef = """
    CREATE TABLE players (

        player_id      serial         PRIMARY KEY,
        name           varchar(30)    UNIQUE NOT NULL,
        join_date      date

    );
"""

gamesDef = """
    CREATE TABLE games (

        game_id        serial         PRIMARY KEY,
        date           date

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

conn = dbConnect()

cur = conn.cursor()

cur.execute(playerDef)
cur.execute(gamesDef)
cur.execute(scoresDef)

conn.commit()

cur.execute("SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';")

print("created:")
print(cur.fetchall())