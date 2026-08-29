USERS = {"u1": {"name": "Ada"}}
def read_user(user_id):
    return dict(USERS[user_id])
def write_user(user_id, data):
    USERS[user_id] = dict(data)
