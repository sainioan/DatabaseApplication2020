from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash


def login(username, password):
    sql = "SELECT password, id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if user == None:
        return False
    else:
        if check_password_hash(user[0], password):
            session["user_id"] = user[1]
            return True
        else:
            return False


def logout():
    del session["user_id"]


def register(username, password):
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username,password) VALUES (:username,:password)"
        db.session.execute(sql, {"username": username, "password": hash_value})
        db.session.commit()
    except:
        return False
    return login(username, password)


def user_check(username):
    sql = "SELECT username FROM users WHERE username = :username"
    db.session.execute(    {"username": username}).fetchone()
    db.session.commit()


def user_id():
    return session.get("user_id", 0)


def is_admin(id):
    sql = "SELECT admin FROM users WHERE id=:id AND admin = True"
    res = db.session.execute(sql, {"id": id})
    return res.fetchall()



def delete_user(id):
    sql = "DELETE from users WHERE id=:id"
    db.session.execute(sql, {"id": id})
    db.session.commit()
    return True
def get_users():
    sql = "SELECT id, username, admin FROM users"
    res = db.session.execute(sql)
    users = res.fetchall()
    return users


