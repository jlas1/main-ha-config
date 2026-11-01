import sqlite3 
from sqlite3 import Error
from requests import get,post 


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def retrieve_history(conn,meta_id):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    power = [[0] * 24  for i in range(8)]
    cur = conn.cursor()
    cur.execute(f"SELECT avg(mean) as mean,strftime('%u',start_ts,'unixepoch') as weekday,strftime('%H',start_ts,'unixepoch') as hour, statistics_short_term.metadata_id as id FROM 'statistics_short_term' INNER JOIN 'statistics_meta' on statistics_meta.id = statistics_short_term.metadata_id where statistics_meta.statistic_id = '{meta_id}' group by weekday,hour")

    rows = cur.fetchall()

    for row in rows:
      power[int(row[1])][int(row[2])]=float(row[0])
    
    return power


def substract_history(total,sub):
    
    power = [[0] * 24  for i in range(8)]
    for i in range(1,8):
      for j in range(24):
        power[i][j] = total[i][j] - sub[i][j]

    return power

def print_result(power):
    for i in range(1,8):
      for j in range(24):
        print (f"Mean {i},{j} {power[i][j]}")

def export_state(power,entidy_id):
    url = "http://10.10.10.80:8123/api/states/"

@service
def main():
    database = r"/root/config/home-assistant_v2.db"

    # create a database connection
    conn = create_connection(database)

    total_power = retrieve_history(conn, "sensor.solax_local_total_home_use")
    aqs_power = retrieve_history(conn, "sensor.tomada_aqs_power")

    total_power = substract_history(total_power,aqs_power)
    print_result(total_power)

