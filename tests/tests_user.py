import json
import random

import pytest
import requests
from fakerabbit import FakeRabbit

from main import db, User


class TestUser:

    @pytest.fixture
    def create_user(self):
        username = FakeRabbit.random_str()
        password = FakeRabbit.random_str()

        query_graphql = '''
                        mutation ($username: String, $password: String) {
                              CreateUser (username: $username, password: $password) {
                                    user {
                                          username
                                          uuid
                                    }
                              }
                        }
                        '''

        variables = \
            {
                "username": username,
                "password": password
            }

        query = {"query": query_graphql, 'variables': variables}

        response = requests.post('http://localhost:5000/graphql', json=query)

        return response

    def test_create_user_returns_status_code_200(self, create_user):
        assert create_user.status_code == 200

    def test_create_user_inserts_id_database(self, create_user):
        response = json.loads(create_user.text)
        new_user_username = response['data']['CreateUser']['user']['username']

        user = db.session.query(User).filter_by(username=new_user_username).one_or_none()

        assert user

    def test_create_user_returns_username_and_uuid(self, create_user):
        response = json.loads(create_user.text)

        new_user_username = response['data']['CreateUser']['user']['username']
        new_user_uuid = response['data']['CreateUser']['user']['uuid']

        assert new_user_username and new_user_uuid

    def test_create_user_with_invalid_username(self, create_user):
        """
        Um username inválido é um username que já existe na base de dados
        """

        new_user_response = json.loads(create_user.text)
        new_user_username = new_user_response['data']['CreateUser']['user']['username']

        query_graphql = '''
                        mutation ($username: String, $password: String) {
                              CreateUser (username: $username, password: $password) {
                                    ok
                              }
                        }
                        '''

        variables = \
            {
                "username": new_user_username,
                "password": FakeRabbit.random_str()
            }

        query = {"query": query_graphql, 'variables': variables}

        existing_user_response = json.loads(requests.post('http://localhost:5000/graphql', json=query).text)

        ok_status = existing_user_response['data']['CreateUser']['ok']

        assert ok_status is False

    def test_delete_user_returns_status_code_200(self, create_user):
        response = json.loads(create_user.text)
        new_user_uuid = response['data']['CreateUser']['user']['uuid']

        query_graphql = '''
                        mutation ($user_id: Int) {
                              DeleteUser (userId: $user_id) {
                                    ok
                                    message
                              }
                        }
                        '''

        variables = \
            {
                "user_id": new_user_uuid
            }

        query = {"query": query_graphql, 'variables': variables}

        response = requests.post('http://localhost:5000/graphql', json=query)

        assert response.status_code == 200

    def test_delete_user_removes_from_database(self, create_user):
        response = json.loads(create_user.text)
        new_user_uuid = response['data']['CreateUser']['user']['uuid']

        query_graphql = '''
                        mutation ($user_id: Int) {
                              DeleteUser (userId: $user_id) {
                                    ok
                                    message
                              }
                        }
                        '''

        variables = {"user_id": new_user_uuid}

        query = {"query": query_graphql, 'variables': variables}

        requests.post('http://localhost:5000/graphql', json=query)

        user_is_deleted = not db.session.query(User).filter_by(uuid=new_user_uuid).one_or_none()

        assert user_is_deleted

    def test_delete_user_with_invalid_id(self):
        fake_user_id = 999999999

        query_graphql = '''
            mutation ($user_id: Int) {
                DeleteUser (userId: $user_id) {
                    ok
                    message
                }
            }
            '''

        variables = {"user_id": fake_user_id}

        query = {"query": query_graphql, 'variables': variables}

        fake_user_delete_response = json.loads(requests.post('http://localhost:5000/graphql', json=query).text)

        ok_status = fake_user_delete_response['data']['DeleteUser']['ok']

        assert ok_status is False

    def test_update_user_returns_status_code_200(self, create_user):
        response = json.loads(create_user.text)

        user_id = response['data']['CreateUser']['user']['uuid']
        username = FakeRabbit.random_str()
        password = FakeRabbit.random_str()

        query_graphql = '''
            mutation ($user_id: Int, $username: String, $password: String) {
                UpdateUser (userId: $user_id, username: $username, password: $password) {
                    ok
                    message
                    user {
                        username
                        password
                    }
                }
            }
        '''

        variables = {
            "user_id": user_id,
            "username": username,
            "password": password
        }

        query = {"query": query_graphql, 'variables': variables}

        update_user_response = requests.post('http://localhost:5000/graphql', json=query)

        assert update_user_response.status_code == 200

    def test_update_user(self, create_user):
        response = json.loads(create_user.text)

        user_id = response['data']['CreateUser']['user']['uuid']
        username = FakeRabbit.random_str()
        password = FakeRabbit.random_str()

        query_graphql = '''
                    mutation ($user_id: Int, $username: String, $password: String) {
                        UpdateUser (userId: $user_id, username: $username, password: $password) {
                            ok
                            message
                            user {
                                username
                                password
                            }
                        }
                    }
                '''

        variables = {
            "user_id": user_id,
            "username": username,
            "password": password
        }

        query = {"query": query_graphql, 'variables': variables}

        update_user_response = json.loads(requests.post('http://localhost:5000/graphql', json=query).text)

        updated_username = update_user_response['data']['UpdateUser']['user']['username']
        updated_password = update_user_response['data']['UpdateUser']['user']['password']

        assert username == updated_username and password == updated_password

    def test_update_user_with_invalid_id(self):
        fake_user_id = 999999999
        username = FakeRabbit.random_str()
        password = FakeRabbit.random_str()

        query_graphql = '''
            mutation ($user_id: Int, $username: String, $password: String) {
                UpdateUser (userId: $user_id, username: $username, password: $password) {
                    ok
                    message
                    user {
                        username
                        password
                    }
                }
            }
        '''

        variables = {
            "user_id": fake_user_id,
            "username": username,
            "password": password
        }

        query = {"query": query_graphql, 'variables': variables}

        fake_user_delete_response = json.loads(requests.post('http://localhost:5000/graphql', json=query).text)

        ok_status = fake_user_delete_response['data']['UpdateUser']['ok']

        assert ok_status is False

    # verificar depois se está correto o uso do SET
    def test_get_all_users(self):
        all_users_database = db.session.query(User.username).all()
        all_users_database = set([user[0] for user in all_users_database])

        query_graphql = '''
                       {
                          getAllUsers {
                            username
                          }
                        }
                     '''

        query = {"query": query_graphql}

        all_users_response = json.loads(requests.post('http://localhost:5000/graphql', json=query).text)

        all_users_graphql = set([user.get('username') for user in all_users_response['data']['getAllUsers']])

        assert all_users_database == all_users_graphql

    def test_get_user_by_id(self):
        rand = random.randrange(0, db.session.query(User).count())
        user = db.session.query(User)[rand]

        query_graphql = '''
                    query ($user_id: Int) {
                        getUser (userId: $user_id) {
                            username
                        }
                    }
                    '''

        variables = {"user_id": user.uuid}

        query = {"query": query_graphql, "variables": variables}

        response = json.loads(requests.post('http://localhost:5000/graphql', json=query).text)

        response_user_username = response['data']['getUser']['username']

        assert response_user_username == user.username

    def test_get_user_with_invalid_id(self):
        fake_user_id = 999999999

        query_graphql = '''
                        query ($user_id: Int) {
                            getUser (userId: $user_id) {
                                username
                            }
                        }
                        '''

        variables = {"user_id": fake_user_id}

        query = {"query": query_graphql, "variables": variables}

        response = json.loads(requests.post('http://localhost:5000/graphql', json=query).text)

        message = response['errors'][0]['message']

        assert message == "Usuário não encontrado"
