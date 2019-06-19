import psycopg2
import json
import argparse
from status import createStatus, createErrorStatus
from checkFunctions import (
    checkIfMemExists,
    checkIfProExists, 
    checkIfActExists,
    checkIfLeader,
    checkIfMemVoted,
    checkPassword,
    checkIfUserIsActive
)
from updateFunctions import (
    updateActionVotes,
    updateLastActivity,
    updateMemberVotes
)
from createFunctions import (
    createAll_id,
    createMember,
    createProject
)
from IO_and_DBconnect import connectToDB


YEAR_IN_SECONDS = 31556926

def openDB(openInfo):
    """
    This function open the database as user from openInfo parametrs.
    """
    try:
        database = openInfo['database']
        login = openInfo['login']
        password = openInfo['password']
        con = connectToDB(database, login, password)
        cur = con.cursor()
        createStatus()
        return con, cur
    except:
        createErrorStatus(debug='Error while opening database')

def createLeader(cur, con, data):
    try:
        timestamp = data["timestamp"]
        password = data["password"]
        id = data["member"]
        createMember(cur, timestamp, password, id)
        query = f"INSERT INTO leaders VALUES({id})"
        cur.execute(query)
        createStatus()
        con.commit()
    except:
        con.rollback()
        createErrorStatus(debug='Error while creating leader')

def createAction(cur, con, data, types):
    timestamp = data["timestamp"]
    password = data["password"]
    memId = data["member"]
    actId = data["action"]
    proId = data["project"]
    try:
        if checkIfMemExists(cur, memId):
            if not (checkPassword(cur, memId, password) 
                and checkIfUserIsActive(cur, memId, timestamp)):
                raise 
        else:
            createMember(cur, timestamp, password, memId)
        if not checkIfProExists(cur, proId):
            authority = data["authority"]
            createProject(cur, proId, authority)
        createAll_id(cur, actId)
        query = f"""
            INSERT INTO actions VALUES(
                {actId},
                '{types}',
                {memId},
                {proId},
                {0},
                {0}
            )
        """
        cur.execute(query)
        updateLastActivity(cur, memId, timestamp)
        createStatus()
        con.commit()
    except:
        con.rollback()
        createErrorStatus(debug='Error while creating protest/support')

def createVote(cur, con, data, vote): 
    timestamp = data["timestamp"]
    password = data["password"]
    memId = data["member"]
    actId = data["action"]
    try:
        if not checkIfActExists(cur, actId):
            raise
        if checkIfMemExists(cur, memId):
            if not (checkPassword(cur, memId, password) 
                and checkIfUserIsActive(cur, memId, timestamp)
                and (not checkIfMemVoted(cur, memId, actId))):
                raise
        else:
            createMember(cur, timestamp, password, memId)
        query = f"INSERT INTO votes VALUES({memId}, {actId}, '{vote}')"
        cur.execute(query)
        updateLastActivity(cur, memId, timestamp)
        updateActionVotes(cur, actId, vote)
        updateMemberVotes(cur, memId, vote)
        createStatus()
        con.commit()
    except:
        con.rollback()
        createErrorStatus(debug='Error while adding vote/unvote')

def actions(cur, con, data):
    try:
        timestamp = data["timestamp"]
        password = data["password"]
        memId = data["member"]
        if not (checkIfLeader(cur, memId)
            and checkPassword(cur, memId, password)
            and checkIfUserIsActive(cur, memId, timestamp)):
            createErrorStatus(debug='Error while executing action function')
        query = """
                SELECT a.Id, a.type, p.Id, p.authority, a.uppvote, a.downvote
                FROM actions a
                    JOIN projects p ON a.Id_project = p.Id
            """
        if "type" in data and "project" in data:
            types, proId = data["type"], data["project"]
            query += f"WHERE a.type = '{types}' AND p.Id = {proId}"
        elif "type" in data and "authority" in data:
            types, authority = data["type"], data["authority"]
            query += f"WHERE a.type = '{types}' AND p.authority = {authority}"
        elif "type" in data:
            types = data["type"]
            query += f"WHERE a.type = '{types}'"
        elif "project" in data:
            proId = data["project"]
            query += f"WHERE p.Id = {proId}"
        elif "authority" in data:
            authority = data["authority"]
            query += f"WHERE p.authority = {authority}"
        query += "\nORDER BY 1"
        cur.execute(query)
        createStatus(cur.fetchall())
        updateLastActivity(cur, memId, timestamp)
        con.commit()
    except:
        con.rollback()
        createErrorStatus(debug='Error while executing action function')

def project(cur, con, data):
    try:
        timestamp = data["timestamp"]
        password = data["password"]
        memId = data["member"]
        if not (checkIfLeader(cur, memId) 
            and checkPassword(cur, memId, password)
            and checkIfUserIsActive(cur, memId, timestamp)):
            createErrorStatus(debug='Error while executing project function')
        query = """
                SELECT Id, authority
                FROM projects
            """
        if "authority" in data:
            authority = data["authority"]
            query += f"WHERE authority = {authority}"
        query += "\nORDER BY 1"
        cur.execute(query)
        createStatus(cur.fetchall())
        updateLastActivity(cur, memId, timestamp)
        con.commit()
    except:
        con.rollback()
        createErrorStatus(debug='Error while executing projects function')

def votes(cur, con, data):
    timestamp = data["timestamp"]
    password = data["password"]
    memId = data["member"]
    try:
        if not (checkIfLeader(cur, memId)
            and checkPassword(cur, memId, password)
            and checkIfUserIsActive(cur, memId, timestamp)):
            createErrorStatus(debug='Error while executing votes function')
        action = f"WHERE Id_action={data['action']}" if "action" in data else ""
        project = f"WHERE Id_project={data['project']}" if "project" in data else ""
        query = """
            SELECT 
            members.Id, 
            SUM(CASE WHEN votes.vote=\'Y\' THEN 1 ELSE 0 END) AS upvotes,
            SUM(CASE WHEN votes.vote=\'N\' THEN 1 ELSE 0 END) AS downvotes
            FROM members
            LEFT JOIN votes ON (votes.Id_member = members.Id)
            LEFT JOIN actions ON (votes.Id_action = actions.Id)
            LEFT JOIN projects ON (projects.Id = actions.Id_project)\n
        """ + action + project + "\nGROUP BY members.Id ORDER BY Id"
        cur.execute(query)
        createStatus(cur.fetchall())
        updateLastActivity(cur, memId, timestamp)
        con.commit()
    except:
        con.rollback()
        createErrorStatus(debug='Error while executing votes function')

def trolls(cur, data):
    try:
        timestamp = data["timestamp"]
        query = f"""
            SELECT 
                a.Id_member,
                SUM(a.uppvote) AS up,
                SUM(a.downvote) AS down,
                CASE WHEN {timestamp} - m.last_activity < {YEAR_IN_SECONDS}
                    THEN 'true' ELSE 'false' END AS is_active
            FROM actions a
                JOIN members m ON (a.Id_member = m.Id)
            GROUP BY a.Id_member, m.last_activity
            HAVING SUM(a.downvote) > SUM(a.uppvote)
            ORDER BY down DESC, a.Id_member
        """
        cur.execute(query)
        createStatus(cur.fetchall())
    except:
        createErrorStatus(debug='Error while executing trolls function')
