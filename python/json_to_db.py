import psycopg2
import json

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')

        # connect to the PostgreSQL server
        conn = psycopg2.connect(
            host="localhost", # change to your hostname
            database="dmo_analysis_db", # change to your database name
            user="postgres", # change to your db username
            password="password") # change to your db password
		
        # create a cursor
        cur = conn.cursor()
        
	    # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        # add a row
        #print("Added row: " + str(insert_row(cur, conn, 2, "Virginia", "test.com", "2022-7-26")))
        open_json(cur, conn)

	    # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def insert_row(cur, conn, id, state, url, date, internal, external):
    sql = """INSERT INTO tourismwebsites(id, state, url, date, internal, external)
             VALUES(%s, %s, %s, %s, %s, %s) RETURNING   id;"""
    try:
        # execute the INSERT statement
        cur.execute(sql, (id, state, url, date, internal, external))
        # get the generated id back
        #added_id = cur.fetchone()[0]
        # commit the changes to the database
        #conn.commit()
        # close communication with the database
        #cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    #return added_id

def open_json(cur, conn):
    # Opening JSON file
    f = open("websites.json", "r", encoding="utf-8")
  
    # returns JSON object as a dictionary
    data = json.load(f)
  
    id_count = 1

    # iterating through the json list
    for year in data:
        print(year)
        for month in data[year]:
            print(month)
            for url in data[year][month]:
                state = data[year][month][url]['state']
                date = year + "-" + month + "-01" 
                internal = data[year][month][url]['internal']
                external = data[year][month][url]['external']

                # remove protocol from URLs
                internal = [s.replace("http://", "") for s in internal]
                internal = [s.replace("https://", "") for s in internal]
                internal = [s.replace("www.", "") for s in internal]
                external = [s.replace("http://", "") for s in external]
                external = [s.replace("https://", "") for s in external]
                external = [s.replace("www.", "") for s in external]
                #print(data[year][month][url]['external'])

                # insert json data into db
                insert_row(cur, conn, id_count, state, url.replace("http://", "").replace("https://", "").replace("www.", ""), date, internal, external)
                id_count += 1

    # closing file
    conn.commit()
    f.close()

if __name__ == '__main__':
    connect()
    #open_json()