from flask import Blueprint, request, jsonify
from database.db import db
from classes.User import User
from classes.Request import Request, RequestStatus, RequestFile, RequestTag
from classes.Response import Response, ResponseStatus, ResponseFile
from classes.Summary import SuccessLog, Bill
from etc.filter import filter_json, filter_query, fuzzy_query
from etc.json import to_json
from etc.file import FileTypes

app = Blueprint('user', __name__)
items_per_page = 10

def try_expire():
    requests = Request.query.filter_by(status=RequestStatus.Waiting).all()
    for request in requests:
        if request.expired_time < datetime.now():
            request.status = RequestStatus.Expired
    db.session.commit()

@app.route('/user/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first() is not None:
        return jsonify({
            "status": 1,
            "message": "用户名已存在",
        })
    user = User(
        username = data['username'],
        password = data['password'],
        is_admin = False,
        name = data['name'],
        certificate_type = data['certificate_type'],
        certificate_number = data['certificate_number'],
        telephone = data['telephone'],
        level = data['level'],
        description = data['description'],
        register_city = data['register_city'],
        register_time = datetime.now(),
        modify_time = datetime.now(),
        cost = 0
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "status": 0,
        "message": "注册成功",
    })

@app.route('/user/modify_data', methods=['POST'])
def modify_data():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('user_id')).first()
    if user is None:
        return jsonify({
            "status": 1,
            "message": "用户名不存在",
        })
    allowed_fields = set(['password', 'telephone', 'description'])
    data = filter_json(User, data, allowed_fields)
    for k, v in data.items():
        setattr(user, k, v)
    user.modify_time = datetime.now()
    db.session.commit()
    return jsonify({
        "status": 0,
        "message": "修改成功",
    })

@app.route('/user/login', methods=['GET'])
def login():
    data = request.get_json()
    if data.get('username') is None:
        return jsonify({
            "status": 1,
            "message": "用户名不能为空",
        })
    user = User.query.filter_by(username=data.get('username')).first()
    if user is None:
        return jsonify({
            "status": 2,
            "message": "用户名不存在",
        })
    if user.password != data.get('password'):
        return jsonify({
            "status": 3,
            "message": "密码错误",
        })
    return jsonify({
        "status": 0,
        "message": "登录成功",
    })

@app.route('/user/logout', methods=['POST'])
def post_request(): # for post users
    data = request.get_json()
    files = data.get('files')

    for file in files:
        request_file = RequestFile(
            file_type = file.get('file_type'),
            data = file.get('data')
        )
        db.session.add(request_file)

    for tag in data.get('tags'):
        request_tag = RequestTag(
            name = tag.get('name')
        )
        db.session.add(request_tag)

    request = Request(
        poster_id = data['poster_id'],
        title = data['title'],
        description = data['description'],
        highest_price = data['highest_price'],
        expired_time = data['expired_time'],
        create_time = datetime.now(),
        modify_time = datetime.now(),
        status = RequestStatus.Waiting
    )

    for file in files:
        if file.get('file_type') == FileTypes.Image:
            request.image_files.append(file)
        elif file.get('file_type') == FileTypes.Video:
            request.video_files.append(file)
        else:
            request.raw_files.append(file)
    for tag in tags:
        request.tags.append(tag)
    
    db.session.add(request)
    db.session.commit()
    return jsonify({
        "status": 0,
        "message": "发布成功",
    })

@app.route('/user/request/query', methods=['GET'])
def query_request(): # for both post and response users
    try_expire()
    data = request.get_json()
    allowed_fields = set(['title', 'description', 'tags'])
    requests = fuzzy_query(Request, data.get('str'), allowed_fields)

    if data.get('poster_id') is not None:
        requests = requests.filter_by(poster_id=data.get('poster_id'))
    
    if data.get('is_responder') == True:
        requests = requests.filter_by(status=RequestStatus.Waiting)
    
    return jsonify({
        "status": 0,
        "message": "查询成功",
        "data": to_json(requests),
    })

@app.route('/user/request/query_brief', methods=['GET'])
def query_request_brief():
    try_expire()
    data = request.get_json()
    allowed_fields = set(['title', 'description', 'tags'])
    requests = fuzzy_query(Request, data.get('str'), allowed_fields)

    if data.get('poster_id') is not None:
        requests = requests.filter_by(poster_id=data.get('poster_id'))
    
    page = data.get('page')
    requests = requests[(page-1)*items_per_page:page*items_per_page]
    filter_fields = set(['description', 'id', 'image_files'])
    requests = [{k: v for k, v in request.items() if k in filter_fields} for request in requests]
    requests = to_json(requests)

    return jsonify({
        "status": 0,
        "message": "查询成功",
        "data": requests,
    })

@app.route('/user/request/reply', methods=['POST'])
def reply_request(): # for post users
    data = request.get_json()
    request = Request.query.filter_by(id=data.get('request_id')).first()
    response = Response.query.filter_by(id=data.get('response_id')).first()
    action = data.get('action')
    if request is None or response is None:
        return jsonify({
            "status": 1,
            "message": "请求不存在",
        })
    if action == 'accept':
        request.status = RequestStatus.Finished
        response.status = ResponseStatus.Accepted
        poster = User.query.filter_by(id=request.poster_id).first()
        responder = User.query.filter_by(id=response.responder_id).first()
        poster.cost += 2
        responder.cost += 2

        success_log = SuccessLog(
            request_id = request.id,
            poster_id = request.poster_id,
            responder_id = response.responder_id,
            poster_cost = 2,
            responder_cost = 2,
            deal_time = datetime.now()
        )

        db.session.add(success_log)
    elif action == 'deny':
        response.status = RequestStatus.Denied
    db.session.commit()
    return jsonify({
        "status": 0,
        "message": "操作成功",
    })

@app.route('/user/request/modify', methods=['POST'])
def modify_request(): # for post users
    data = request.get_json()
    request = Request.query.filter_by(id=data.get('request_id')).first()
    if request is None:
        return jsonify({
            "status": 1,
            "message": "请求不存在",
        })
    allowed_fields = set(['location_type', 'title', 'description', 'file_folder_uri', 'highest_price', 'expired_time'])
    data = filter_json(Request, data, allowed_fields)
    for k, v in data.items():
        setattr(request, k, v)
    request.modify_time = datetime.now()
    db.session.commit()
    return jsonify({
        "status": 0,
        "message": "修改成功",
    })

@app.route('/user/request/delete', methods=['POST'])
def delete_request(): # for post users
    data = request.get_json()
    request = Request.query.filter_by(id=data.get('request_id')).first()
    if request is None:
        return jsonify({
            "status": 1,
            "message": "请求不存在",
        })
    request.status = RequestStatus.Canceled
    db.session.commit()
    return jsonify({
        "status": 0,
        "message": "删除成功",
    })

@app.route('/user/response/post', methods=['POST'])
def post_respose(): # for response users
    data = request.get_json()
    files = data.get('files')
    for file in files:
        response_file = ResponseFile(
            file_type = file.get('file_type'),
            data = file.get('data')
        )
        db.session.add(response_file)
    response = Response(
        request_id = data['request_id'],
        responder_id = data['responder_id'],
        description = data['description'],
        create_time = datetime.now(),
        modify_time = datetime.now(),
        status = ResponseStatus.Waiting
    )
    for file in files:
        if file.get('file_type') == FileTypes.Image:
            response.image_files.append(file)
        elif file.get('file_type') == FileTypes.Video:
            response.video_files.append(file)
        else:
            response.raw_files.append(file)
    db.session.add(response)
    db.session.commit()
    return jsonify({
        "status": 0,
        "message": "发布成功",
    })

@app.route('/user/response/query', methods=['GET'])
def query_response(): # for response users 
    data = request.get_json()
    allowed_fields = set(['description'])
    responses = fuzzy_query(Response, data.get('str'), allowed_fields)

    if data.get('responder_id') is not None:
        responses = responses.filter_by(responder_id=data.get('responder_id'))
    
    return jsonify({
        "status": 0,
        "message": "查询成功",
        "data": to_json(responses),
    })

@app.route('/user/response/query_brief', methods=['GET'])
def query_response_brief():
    data = request.get_json()
    allowed_fields = set(['description'])
    responses = fuzzy_query(Response, data.get('str'), allowed_fields)

    if data.get('responder_id') is not None:
        responses = responses.filter_by(responder_id=data.get('responder_id'))

    page = data.get('page')
    responses = responses[(page-1)*items_per_page:page*items_per_page]
    filter_fields = set(['description', 'id'])
    responses = [{k: v for k, v in response.items() if k in filter_fields} for response in responses]
    return jsonify({
        "status": 0,
        "message": "查询成功",
        "data": responses,
    })

@app.route('/user/response/modify', methods=['POST'])
def modify_response(): # for response users
    data = request.get_json()
    response = Response.query.filter_by(id=data.get('response_id')).first()
    if response is None:
        return jsonify({
            "status": 1,
            "message": "响应不存在",
        })
    allowed_fields = set(['description', 'files'])
    data = filter_json(Response, data, allowed_fields)
    for k, v in data.items():
        setattr(response, k, v)
    response.modify_time = datetime.now()
    db.session.commit()
    return jsonify({
        "status": 0,
        "message": "修改成功",
    })

@app.route('/user/response/delete', methods=['POST'])
def delete_response(): # for response users
    data = request.get_json()
    response = Response.query.filter_by(id=data.get('response_id')).first()
    if response is None:
        return jsonify({
            "status": 1,
            "message": "响应不存在",
        })
    response.status = ResponseStatus.Canceled
    db.session.commit()
    return jsonify({
        "status": 0,
        "message": "删除成功",
    })


