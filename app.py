from flask import Flask, request
from flask_api import status
import mariadb
import json
from dotenv import load_dotenv
import os

application = Flask(__name__)

@application.route('/')
def index():
    return 'Simple Game Wannabe'

@application.route('/get_bls_record', methods=['POST'])
def get_bls_record():
    if request.method == 'POST':
        result = json.dumps(get_record(100))
        return result, status.HTTP_200_OK, {"Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*"}

@application.route('/set_bls_record', methods=['POST'])
def set_bls_record():
    if request.method == 'POST':
        if request.is_json:
            params = request.get_json()
            set_record(params['nickname'], params['score'])
            return {"result_code": "0000"}, status.HTTP_200_OK, {"Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*"}

def get_env(name):
    return os.environ.get(name)

def connect_db():
    try:
        return mariadb.connect(
            user=get_env('USERNAME'),
            password=get_env('PASSWORD'),
            host=get_env('HOST'),
            port=int(get_env('PORT')),
            database=get_env('DB')
        )
    except mariadb.Error as e:
        print(e)

def get_record(limit):
    try:
        conn = connect_db()
        sql = 'SELECT id, nickname, score FROM bls_record ORDER BY score DESC LIMIT 0, ' + str(limit)
        result = []
        cur = conn.cursor()
        cur.execute(sql)
        for data in cur:
            result.append({
                'id': str(data[0]),
                'nickname': data[1],
                'score': str(data[2])
                })
        conn.close()
        return result
    except mariadb.Error as e:
        print(e)

def set_record(nickname, score):
    try:
        conn = connect_db()
        sql = 'INSERT INTO bls_record(nickname, score) VALUES(?, ?)'
        cur = conn.cursor()
        cur.execute(sql, (nickname, score))
        conn.commit()
        conn.close()
    except mariadb.Error as e:
        print(e)

if __name__ == "app":
    load_dotenv()
    conn = connect_db()

if __name__ == "__main__":
    application.run(host="localhost", posrt="5000")