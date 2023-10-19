from flask import Flask
from flask import request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import re
import math
import json

# config flask framework
app = Flask(__name__,static_url_path='')
CORS(app,supports_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calc.db'

# initialize database
db = SQLAlchemy(app)
class __history__(db.Model):
    __tablename__ = '__history__'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mode = db.Column(db.Integer)
    expr = db.Column(db.String)
    month = db.Column(db.Integer)
    result = db.Column(db.Float)
    error = db.Column(db.Integer)

class __rate__(db.Model):
    __tablename__ = '__rate__'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mode = db.Column(db.Integer)
    month = db.Column(db.Float)
    rate = db.Column(db.Float)

def init():
    with app.app_context():
        db.create_all()


# application
math_replace_list = [
    ['π', 'math.pi'],
    ['e', 'math.e'],
    ['sin', 'math.sin'],
    ['cos', 'math.cos'],
    ['tan', 'math.tan'],
    ['log', 'math.log10'],
    ['√', 'math.sqrt'],
    ['÷', '/'],
    ['×', '*']
]

@app.route('/')
def index():
    return app.send_static_file("index.html")


@app.route('/api/getAns', methods=['GET'])
def getAns():
    history = __history__.query.filter(__history__.error==0).all();

    ans = 0
    if len(history) != 0:
        ans = history[-1].result

    ret = {
        'code': 200,
        'msg': '请求成功',
        'data': ans,
        'error': 0
    }

    return json.dumps(ret, ensure_ascii=False), 200


@app.route('/api/calcResult', methods=['POST'])
def calcResult():
    expr = request.get_json(force=True)['expression']
    expr = re.sub('[\'\"\n\r=]', '', expr)

    for i in math_replace_list:
        expr = re.sub(i[0], i[1], expr)

    result = 0
    error = 0
    try:
        result = eval(expr)
        error = 0
    except:
        result = 0
        error = -1

    with app.app_context():
        db.session.add(__history__(mode=0, expr=expr, result=result, error=error))
        db.session.commit()

    ret = {
        'code': 200,
        'msg': '请求成功',
        'data': result,
        'error': error
    }

    return json.dumps(ret, ensure_ascii=False), 200

@app.route('/api/rateResult', methods=['POST'])
def rateResult():
    req = request.get_json(force=True)
    expr = req['expression']
    expr = re.sub('[\'\"\n\r=]', '', expr)
    expr = float(expr)
    month = req['month']
    month = re.sub('[\'\"\n\r=]', '', month)
    month = int(month)
    mode = req['mode']
    mode = re.sub('[\'\"\n\r=]', '', mode)
    mode = int(mode)

    rate = __rate__.query.filter(__rate__.mode==mode, __rate__.month <= month).all();

    ret = {}
    result = 0
    error = 0
    if len(rate) == 0:
        ret = {
            'code': 200,
            'msg': '月份过少',
            'data': 0,
            'error': -1
        }
        error = -1;
        result = 0;
    else:
        rate = rate[-1].rate
        result = expr
        _month = month
        if _month >= 12:
            while _month > 0:
                result = result + result * (rate / 100)
                _month -= 12
        else:
            while _month > 0:
                result = result + result * (rate / 100)
                _month -= 1
        ret = {
            'code': 200,
            'msg': '请求成功',
            'data': result,
            'error': 0
        }

    with app.app_context():
        db.session.add(__history__(mode=mode, expr=expr, result=result, error=error, month = month))
        db.session.commit()

    ret = {
        'code': 200,
        'msg': '请求成功',
        'data': result,
        'error': error
    }

    return json.dumps(ret, ensure_ascii=False), 200

# for command line
if __name__ == '__main__':
    init()
    # with app.app_context():
    #     db.session.add(__rate__(mode=1,month=3,rate=2.85))
    #     db.session.add(__rate__(mode=1,month=6,rate=3.05))
    #     db.session.add(__rate__(mode=1,month=12,rate=3.25))
    #     db.session.add(__rate__(mode=1,month=24,rate=4.15))
    #     db.session.add(__rate__(mode=1,month=36,rate=4.75))
    #     db.session.add(__rate__(mode=1,month=60,rate=5.25))

    #     db.session.add(__rate__(mode=2,month=6,rate=5.85))
    #     db.session.add(__rate__(mode=2,month=12,rate=6.31))
    #     db.session.add(__rate__(mode=2,month=12.1,rate=6.4))
    #     db.session.add(__rate__(mode=2,month=36.1,rate=6.65))
    #     db.session.add(__rate__(mode=2,month=60,rate=6.8))
    #     db.session.commit()
    app.run(host="0.0.0.0", port=12345)