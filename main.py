import psycopg

## connect syntax is not the same as explained in section because I'm using psycopg not psycogp2
conn = None


def connect(): ##msh fahme a dah howa wl func el ta7t wl variable el foo2
    global conn
    conn = psycopg.connect(
        host="ep-little-sea-a5pqiybv.us-east-2.aws.neon.tech",
        dbname="neondb",
        user="neondb_owner",
        password="t7K0zdwGikXf",
        port=5432
    )


def execute():
    cur = conn.cursor()
    cur.execute(
        "SELECT Sup.name, Sup.age , count(E.id) FROM Employee E join Employee Sup on E.supervisor_id=Sup.id GROUP BY Sup.id ,Sup.name, Sup.age;")
    records = cur.fetchall()
    for record in records:
        print(record)
