import psycopg2
import json


YEAR_IN_SECONDS = 31556926

def checkIfMemExists(cur, memId):
	query = f"""
		SELECT Id FROM members
		WHERE Id = {memId}
	"""
	try:
		cur.execute(query)
		qId = cur.fetchone()
		return qId is not None
	except:
		raise

def checkIfProExists(cur, proId):
	query = f"""
		SELECT Id FROM projects
		WHERE Id = {proId}
	"""
	try:
		cur.execute(query)
		qId = cur.fetchone()
		return qId is not None
	except:
		raise

def checkIfAuthExists(cur, authId):
	query = f"""
		SELECT Authority FROM projects
		WHERE Authority = {authId}
	"""
	try:
		cur.execute(query)
		qId = cur.fetchone()
		return qId is not None
	except:
		raise

def checkIfActExists(cur, actId):
	query = f"""
		SELECT Id FROM actions
		WHERE Id = {actId}
	"""
	try:
		cur.execute(query)
		qId = cur.fetchone()
		return qId is not None
	except:
		raise

def checkIfMemVoted(cur, memId, actId):
    query = f"""
        SELECT Id_member FROM votes
        WHERE Id_member = {memId}
        AND Id_action = {actId}
    """
    try:
        cur.execute(query)
        qId = cur.fetchone()
        return qId is not None
    except:
        print("cos")
        raise

def checkIfLeader(cur, memId):
    query = f"""
        SELECT Id FROM leaders
        WHERE Id = {memId}
    """
    try:
        cur.execute(query)
        qId = cur.fetchone()
        return qId is not None
    except:
        raise

def checkPassword(cur, memId, password):
    try:
        query = f"""
            SELECT Id FROM members 
            WHERE Id = {memId} AND password = crypt('{password}', password)
        """
        cur.execute(query)
        qId = cur.fetchone()
        return qId is not None
    except:
        raise

def checkIfUserIsActive(cur, Id, timestamp):
    try:
        query = f"SELECT last_activity FROM members WHERE id={Id}"
        cur.execute(query)
        prev_timestamp = cur.fetchall()[0][0]
        return True if timestamp - prev_timestamp < YEAR_IN_SECONDS else False
    except:
        raise