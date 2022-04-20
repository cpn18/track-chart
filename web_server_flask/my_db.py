import sqlite3
from flask import g

DATABASE = "TrackDataDB.db"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def init_db():
    # db = get_db()
    # print("initializing database")
    query = """CREATE TABLE IF NOT EXISTS track(time_stamp integer UNIQUE, acc_x integer, 
        acc_y integer, acc_z integer, pitch integer, yaw integer, roll integer, mileage integer )"""
    query_db(query)


def get_data(mini, maxi):
    query = 'SELECT acc_z, mileage FROM track WHERE mileage between ? and ?'
    rows = query_db(query, (mini, maxi,))
    return rows


def get_stats(mini, maxi):
    query = '''SELECT acc_x, acc_y, acc_z, roll, pitch, yaw
                FROM track WHERE mileage between ? and ?'''
    rows = query_db(query, (mini, maxi,))
    return rows


