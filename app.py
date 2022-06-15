from flask import Flask, request
from flask_api import status
import mariadb
import json
from dotenv import load_dotenv
import os

app = Flask(__name__)
conn = None

@app.route('/')
def index():
    return 'Simple Game Wannabe'

@app.route('/get_bls_record', methods=['POST'])
def get_bls_record():
    if request.method == 'POST':
        result = json.dumps(get_record(5))
        return result, status.HTTP_200_OK, {"Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*"}

@app.route('/set_bls_record', methods=['POST'])
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
        sql = 'SELECT nickname, score FROM bls_record ORDER BY score DESC LIMIT 0, ' + str(limit)
        result = []
        cur = conn.cursor()
        cur.execute(sql)
        for data in cur:
            result.append({'nickname': data[0], 'score': str(data[1])})
        return result
    except mariadb.Error as e:
        print(e)

def set_record(nickname, score):
    try:
        sql = 'INSERT INTO bls_record(nickname, score) VALUES(?, ?)'
        cur = conn.cursor()
        cur.execute(sql, (nickname, score))
        conn.commit()
    except mariadb.Error as e:
        print(e)

if __name__ == "__main__":
    load_dotenv()
    conn = connect_db()
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)

# DROP TABLE bls_record;
# CREATE TABLE bls_record(id INT NOT NULL AUTO_INCREMENT, nickname VARCHAR(20) NOT NULL, score DECIMAL(7,3) NOT NULL, PRIMARY KEY (id));
# CREATE OR REPLACE INDEX score_idx ON bls_record (score);
# INSERT INTO bls_record(nickname, score) VALUES('TEST', 112.121);
# INSERT INTO bls_record(nickname, score) VALUES('TEST1', 33.321);
# INSERT INTO bls_record(nickname, score) VALUES('TEST2', 14.121);
# INSERT INTO bls_record(nickname, score) VALUES('TEST3', 125.122);
# INSERT INTO bls_record(nickname, score) VALUES('TEST4', 16.421);
# select nickname, score from bls_record order by score desc limit 0, 3;

# curl -X POST -H "Content-Type: application/json" http://localhost:8080/get_bls_record
# curl -X POST -H "Content-Type: application/json" -d '{"nickname":"bbbb","score":"333.222"}' http://localhost:8080/set_bls_record