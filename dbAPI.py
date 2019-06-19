import psycopg2
import json
import argparse
from status import createStatus, createErrorStatus
from API_Functions import (
    openDB,
    createAction,
    createLeader,
    createVote,
    actions,
    project,
    votes,
    trolls
)
from IO_and_DBconnect import (
    clear,
    loadQueries
)


def initDB(jsonObjects, dbCreateSQL='createDB.sql', reset=False):
    """
    Init new database.
    """
    try:
        jsonOpen = jsonObjects[0]
        con, cur = openDB(jsonOpen['open'])

        if reset:
            clear(cur)

        with open (dbCreateSQL, 'r') as DB_sql:
            query = DB_sql.read()
        cur.execute(query)
        
        for newLead in jsonObjects[1:]:
            createLeader(cur, con, newLead['leader'])
        return con, cur
    except:
        createErrorStatus(debug='Error while initializng database')

def execQuieries(jsonObjects):
    queriesFunctions = {
        'actions': actions,
        'projects': project,
        'votes': votes,
    }
    try:
        jsonOpen = jsonObjects[0]
        con, cur = openDB(jsonOpen['open'])
        for jsonQuery in jsonObjects[1:]:
            query, data = list(jsonQuery.items())[0]
            if query == 'support' or query == 'protest':
                createAction(cur, con, data, query)
            elif query == 'upvote':
                createVote(cur, con, data, 'Y')
            elif query == 'downvote':
                createVote(cur, con, data, 'N')
            elif query == 'trolls':
                trolls(cur, data)
            elif query not in queriesFunctions.keys():
                createErrorStatus(debug=f'Query {query} does not exist')
                continue
            else:
                queriesFunctions[query](cur, con, data)
        return con, cur
    except:
        createErrorStatus(debug='Error while executing queries') 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Adam Bukowczyk, Bazy Danych 2018/19')
    parser.add_argument('inputFile', help='Name of the input file with json queries')
    parser.add_argument('--init', action='store_true', help='init database')
    parser.add_argument('--reset', action='store_true', help='clear database')
    args = parser.parse_args()
    jsonObjects = loadQueries(args.inputFile)

    if args.init:
        con, cur = initDB(jsonObjects, reset=True) if args.reset else initDB(jsonObjects)
    else:
        con, cur = execQuieries(jsonObjects)


    con.commit()
    cur.close()
    con.close()
