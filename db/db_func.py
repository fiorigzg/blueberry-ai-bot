import sqlite3 as sql
import datetime
from dateutil.relativedelta import relativedelta


def add_subscription(id):
  con = sql.connect(f'./db/user.sqlite3')
  todate = datetime.date.today() + relativedelta(days=30)

  with con:
    cur = con.cursor()
    cur.execute(f"SELECT * FROM subscription WHERE id={id};")
    isuser = cur.fetchall() != []
    if isuser:
      cur.execute(f"UPDATE subscription SET todate='{todate.strftime('%d/%m/%Y')}' WHERE id={id}")
    else: 
      cur.execute(f"INSERT INTO subscription ('id', 'todate') VALUES ({id}, '{todate.strftime('%d/%m/%Y')}')")
    con.commit()

  con.close()

def get_subscription(id):
  con = sql.connect(f'./db/user.sqlite3')
  result = {"status": False, "date": "none"}

  with con:
    cur = con.cursor()

    cur.execute(f"SELECT * FROM subscription WHERE id={id};")
    subscription = cur.fetchall()
    if subscription != []:
      result = {"status": datetime.datetime.strptime(subscription[0][1], '%d/%m/%Y').date() >= datetime.date.today(), "date": subscription[0][1]}
    con.commit()

  con.close()
  return result

def add_generation(id, imgCount=1):
  con = sql.connect(f'./db/user.sqlite3')

  with con:
    cur = con.cursor()
    result = imgCount

    if not get_subscription(id)["status"]:
      cur.execute(f"SELECT * FROM generation WHERE id={id};")
      userGenerations = cur.fetchall()
      if userGenerations != []:
        if 10 - userGenerations[0][1] < result:
          result = 10 - userGenerations[0][1]
        cur.execute(f"UPDATE generation SET count='{userGenerations[0][1]+result}' WHERE id={id}")
      else: 
        cur.execute(f"INSERT INTO generation ('id', 'count') VALUES ({id}, '{result}')")
    con.commit()

  con.close()
  return result

def clear_generations():
  con = sql.connect(f'./db/user.sqlite3')

  with con:
    cur = con.cursor()

    cur.execute(f"DELETE FROM generation;")
    con.commit()

  con.close()