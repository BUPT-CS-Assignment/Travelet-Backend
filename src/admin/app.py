from flask import Blueprint, request, jsonify
from database.db import db
from classes.User import User
from classes.Request import Request
from classes.Response import Response
from classes.Summary import SuccessLog, Bill
from etc.filter import filter_json, filter_query
from etc.json import to_json

app = Blueprint('admin', __name__)

@app.route('/admin/query/user', methods=['GET'])
def query_user_data():
    data = request.get_json()
    if data.get('user_id') is None:
        user = User.query.all()
    else :
        user = User.query.filter_by(username=data.get('user_id')).first()
    return jsonify({
        "status": 0,
        "message": "查询成功",
        "data": to_json(user)
    })

@app.route('/admin/query/request', methods=['GET'])
def query_request():
    data = request.get_json()
    requests = filter_query(Request, data)
    return jsonify({
        "status": 0,
        "message": "查询成功",
        "data": to_json(requests)
    })

@app.route('/admin/query/response', methods=['GET'])
def query_response():
    data = request.get_json()
    responses = filter_query(Response, data)
    return jsonify({
        "status": 0,
        "message": "查询成功",
        "data": to_json(responses)
    })

@app.route('/admin/query/bill', methods=['GET'])
def query_bill(): # xkx do this!
    data = request.get_json()
    return jsonify({
        "status": 0,
        "message": "查询成功", # todo
    })


