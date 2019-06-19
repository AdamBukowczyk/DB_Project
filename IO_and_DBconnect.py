import psycopg2
import json

def connectToDB(dbName, user, password, host='localhost'):
    """
    This function connect to database using psycopg2.
    """
    try:
        con = psycopg2.connect(dbname=dbName, user=user, host=host, password=password)
    except:
        raise 'Could not connect to database'
    return con

def clear(cur):
    with open ('clear.sql', 'r') as clear_sql:
        clear = clear_sql.read()
    cur.execute(clear)

def loadQueries(filename):
    """
    Change json file into list od dictonaries.
    """
    with open(filename, "r") as testFile:
        jsonLines = [line.strip() for line in testFile.readlines()]
        jsonObjects = [json.loads(line) for line in jsonLines]
    return jsonObjects