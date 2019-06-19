import psycopg2
import json


def updateLastActivity(cur, memId, timestamp):
    try:
        query=f"UPDATE members SET last_activity = {timestamp} WHERE Id={memId}"
        cur.execute(query)
    except:
        raise

def updateMemberVotes(cur, memId, vote):
    try:
        if vote == 'Y':
            query = f"UPDATE members SET uppvote = uppvote + 1 WHERE Id = {memId}"
        else:
            query = f"UPDATE members SET downvote = downvote + 1 WHERE Id = {memId}"
        cur.execute(query)
    except:
        raise

def updateActionVotes(cur, actId, vote):
    try:
        if vote == 'Y':
            query = f"UPDATE actions SET uppvote = uppvote + 1 WHERE Id = {actId}"
        else:
            query = f"UPDATE actions SET downvote = downvote + 1 WHERE Id = {actId}"
        cur.execute(query)
    except:
        raise