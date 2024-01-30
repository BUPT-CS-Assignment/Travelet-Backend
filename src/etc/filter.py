from flask_sqlalchemy import SQLAlchemy

def filter_json(model, json_data, allowed_fields=None):
    if allowed_fields is not None:
        valid_fields = allowed_fields
    else:
        valid_fields = set(model.__table__.columns.keys())
    valid_json_data = {k: v for k, v in json_data.items() if k in valid_fields}
    return valid_json_data

def filter_query(model, json_data):
    filter_json_data = filter_json(model, json_data)
    return model.query.filter_by(**filter_json_data).all()

def fuzzy_query(model, string, allowed_fields=None):
    if allowed_fields is not None:
        valid_fields = allowed_fields
    else:
        valid_fields = set(model.__table__.columns.keys())
    # collect all results from each field
    results = []
    for field in valid_fields:
        results += model.query.filter(getattr(model, field).like('%' + string + '%')).all()
    # remove duplicates
    results = list(set(results))
    return results