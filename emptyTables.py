from dbConnect import dbConnect

with dbConnect() as conn:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE players,games,scores")


print("cleared data from tables.")
