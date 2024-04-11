import psycopg2

conn = psycopg2.connect(
    dbname="database",
    user="username",
    password="password",
    host="db"
)
cur = conn.cursor()

