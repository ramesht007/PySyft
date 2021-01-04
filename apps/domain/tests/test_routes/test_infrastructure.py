from json import dumps, loads

import jwt
import pytest
from flask import current_app as app

from src.main.core.database import *

JSON_DECODE_ERR_MSG = (
    "Expecting property name enclosed in " "double quotes: line 1 column 2 (char 1)"
)
owner_role = ("Owner", True, True, True, True, True, True, True)
user_role = ("User", False, False, False, False, False, False, False)
admin_role = ("Administrator", True, True, True, True, False, False, True)

user1 = (
    "tech@gibberish.com",
    "BDEB6E8EE39B6C70835993486C9E65DC",
    "]GBF[R>GX[9Cmk@DthFT!mhloUc%[f",
    "fd062d885b24bda173f6aa534a3418bcafadccecfefe2f8c6f5a8db563549ced",
    1,
)
user2 = (
    "anemail@anemail.com",
    "2amt5MXKdLhEEL8FiQLcl8Mp0FNhZI6",
    "$2b$12$rj8MnLcKBxAgL7GUHrYn6O",
    "acfc10d15d7ec9f7cd05a312489af2794619c6f11e9af34671a5f33da48c1de2",
    2,
)
user3 = (
    "anemail@anemail.com",
    "2amt5MXKdLhEEL8FiQLcl8Mp0FNhZI6",
    "$2b$12$rj8MnLcKBxAgL7GUHrYn6O",
    "acfc10d15d7ec9f7cd05a312489af2794619c6f11e9af34671a5f33da48c1de2",
    3,
)
user4 = (
    "tech@gibberish.com",
    "2amt5MXKdLhEEL8FiQLcl8Mp0FNhZI6",
    "$2b$12$tufn64/0gSIAdprqBrRzC.",
    "fd062d885b24bda173f6aa534a3418bcafadccecfefe2f8c6f5a8db563549ced",
    2,
)


@pytest.fixture
def cleanup(database):
    yield
    try:
        database.session.query(User).delete()
        database.session.query(Role).delete()
        database.session.query(Group).delete()
        database.session.query(UserGroup).delete()
        database.session.commit()
    except:
        database.session.rollback()


"""
def test_create_node(client):
    result = client.post("/dcfl/nodes", data={"name": "test_node", "password": "1234"})
    assert result.status_code == 200
    assert result.get_json() == {"msg": "Node created succesfully!"}


def test_get_all_nodes(client):
    result = client.get("/dcfl/nodes")
    assert result.status_code == 200
    assert result.get_json() == {
        "nodes": [
            {"id": "35654sad6ada", "address": "175.89.0.170"},
            {"id": "adfarf3f1af5", "address": "175.55.22.150"},
            {"id": "fas4e6e1fas", "address": "195.74.128.132"},
        ]
    }


def test_get_specific_node(client):
    result = client.get("/dcfl/nodes/464615")
    assert result.status_code == 200
    assert result.get_json() == {
        "node": {"id": "464615", "tags": ["node-a"], "description": "node sample"}
    }


def test_update_node(client):
    result = client.put("/dcfl/nodes/546313", data={"node": "{new_node}"})
    assert result.status_code == 200
    assert result.get_json() == {"msg": "Node changed succesfully!"}


def test_delete_node(client):
    result = client.delete("/dcfl/nodes/546313")
    assert result.status_code == 200
    assert result.get_json() == {"msg": "Node deleted succesfully!"}


def test_create_autoscaling(client):
    result = client.post(
        "/dcfl/nodes/autoscaling", data={"configs": "{auto-scaling_configs}"}
    )
    assert result.status_code == 200
    assert result.get_json() == {"msg": "Autoscaling condition created succesfully!"}


def test_get_all_autoscaling_conditions(client):
    result = client.get("/dcfl/nodes/autoscaling")
    assert result.status_code == 200
    assert result.get_json() == {
        "condition_a": {"mem_usage": "80%", "cpu_usage": "90%", "disk_usage": "75%"},
        "condition_b": {"mem_usage": "50%", "cpu_usage": "70%", "disk_usage": "95%"},
        "condition_c": {"mem_usage": "92%", "cpu_usage": "77%", "disk_usage": "50%"},
    }


def test_get_specific_autoscaling_condition(client):
    result = client.get("/dcfl/nodes/autoscaling/6413568")
    assert result.status_code == 200
    assert result.get_json() == {
        "mem_usage": "80%",
        "cpu_usage": "90%",
        "disk_usage": "75%",
    }


def test_update_autoscaling_condition(client):
    result = client.put(
        "/dcfl/nodes/autoscaling/6413568",
        data={"autoscaling": "{new_autoscaling_condition}"},
    )
    assert result.status_code == 200
    assert result.get_json() == {"msg": "Autoscaling condition updated succesfully!"}


def test_delete_autoscaling_condition(client):
    result = client.delete("/dcfl/nodes/autoscaling/6413568")
    assert result.status_code == 200
    assert result.get_json() == {"msg": "Autoscaling condition deleted succesfully!"}
"""


def test_create_worker(client, database, cleanup):
    new_role = create_role(*admin_role)
    database.session.add(new_role)
    new_user = create_user(*user1)
    database.session.add(new_user)

    database.session.commit()

    token = jwt.encode({"id": 1}, app.config["SECRET_KEY"])
    headers = {
        "token": token.decode("UTF-8"),
    }

    result = client.post(
        "/dcfl/workers",
        data={"name": "test_worker"},
        headers=headers,
    )
    # assert result.status_code == 200
    assert result.get_json() == {"msg": "Worker created succesfully!"}


def test_get_all_workers(client, database, cleanup):
    new_role = create_role(*admin_role)
    database.session.add(new_role)
    new_user = create_user(*user1)
    database.session.add(new_user)

    database.session.commit()

    token = jwt.encode({"id": 1}, app.config["SECRET_KEY"])
    headers = {
        "token": token.decode("UTF-8"),
    }

    result = client.get(
        "/dcfl/workers",
        headers=headers,
    )
    # assert result.status_code == 200
    assert result.get_json() == {
        "workers": [
            {"id": "546513231a", "address": "159.156.128.165", "datasets": 25320},
            {"id": "asfa16f5aa", "address": "138.142.125.125", "datasets": 2530},
            {"id": "af61ea3a3f", "address": "19.16.98.146", "datasets": 2320},
            {"id": "af4a51adas", "address": "15.59.18.165", "datasets": 5320},
        ]
    }


def test_get_specific_worker(client, database, cleanup):
    new_role = create_role(*admin_role)
    database.session.add(new_role)
    new_user = create_user(*user1)
    database.session.add(new_user)

    database.session.commit()

    token = jwt.encode({"id": 1}, app.config["SECRET_KEY"])
    headers = {
        "token": token.decode("UTF-8"),
    }

    result = client.get(
        "/dcfl/workers/9846165",
        headers=headers,
    )
    # assert result.status_code == 200
    assert result.get_json() == {
        "worker": {"id": "9846165", "address": "159.156.128.165", "datasets": 25320}
    }


def test_delete_worker(client, database, cleanup):
    new_role = create_role(*admin_role)
    database.session.add(new_role)
    new_user = create_user(*user1)
    database.session.add(new_user)

    database.session.commit()

    token = jwt.encode({"id": 1}, app.config["SECRET_KEY"])
    headers = {
        "token": token.decode("UTF-8"),
    }

    result = client.delete(
        "/dcfl/workers/9846165",
        headers=headers,
    )
    # assert result.status_code == 200
    assert result.get_json() == {"msg": "Worker was deleted succesfully!"}