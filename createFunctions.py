import psycopg2
import json
from checkFunctions import checkIfAuthExists


def createMember(cur, timestamp, password, id):
    try:
        createAll_id(cur, id)
        query = f"""
        INSERT INTO members VALUES(
            {id},
            crypt('{password}',
            gen_salt('bf')),
            {timestamp}, 
            {0},
            {0})
        """
        cur.execute(query)
    except:
        raise

def createAll_id(cur, id):
    try:
        query = f"INSERT INTO allid VALUES({id})"
        cur.execute(query)
    except:
        raise

def createProject(cur, id, authority):
    try:
        createAll_id(cur, id)
        if not checkIfAuthExists(cur, authority):
            createAll_id(cur, authority)
        query = f"INSERT INTO projects VALUES({id}, {authority})"
        cur.execute(query)
    except:
        raise
