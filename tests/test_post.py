import json
import random

import pytest
import requests
from fakerabbit import FakeRabbit

from main import db, User, Post


class TestPost:

    @pytest.fixture
    def create_post(self):
        title = FakeRabbit.random_str()
        body = FakeRabbit.random_str(20)

        rand = random.randrange(0, db.session.query(User).count())
        username = db.session.query(User.username)[rand][0]

        query_graphql = '''
                    mutation ($title: String!, $body: String!, $username: String!) {
                        CreatePost (body:$body, title: $title, username: $username) {
                            ok
                            message
                            post {
                              uuid
                              title
                              body
                              author {
                                username
                              }
                            }
                      }
                    }
                '''

        variables = {
            "title": title,
            "body": body,
            "username": username
        }

        query = {"query": query_graphql, "variables": variables}

        return requests.post('http://localhost:5000/graphql', json=query)

    def test_create_post_returns_status_code_200(self, create_post):
        assert create_post.status_code == 200

    def test_create_post_inserts_in_database(self, create_post):
        response = json.loads(create_post.text)

        response_new_post_id = response['data']['CreatePost']['post']['uuid']

        new_post = db.session.query(Post).filter_by(uuid=response_new_post_id).one_or_none()

        assert new_post

    def test_create_post_with_invalid_user(self):
        title = FakeRabbit.random_str()
        body = FakeRabbit.random_str(20)
        username = FakeRabbit.random_str(11)

        query_graphql = '''
                    mutation ($title: String!, $body: String!, $username: String!) {
                        CreatePost (body:$body, title: $title, username: $username) {
                            ok
                            message
                            post {
                              title
                              body
                              author {
                                username
                              }
                            }
                      }
                    }
                '''

        variables = {
            "title": title,
            "body": body,
            "username": username
        }

        query = {"query": query_graphql, "variables": variables}

        response = json.loads(requests.post('http://localhost:5000/graphql', json=query).text)

        ok_status = response['data']['CreatePost']['ok']
        message = response['data']['CreatePost']['message']

        assert ok_status is False and message == "Usuário inválido"

    def test_get_all_posts_returns_status_code_200(self):
        query_graphql = '''
            {
                getAllPosts {
                    title
                    body
                    authorId
                }
            }
        '''

        query = {"query": query_graphql}

        response = requests.post('http://localhost:5000/graphql', json=query)

        assert response.status_code == 200

    def test_get_all_posts(self):
        """
        Checa se os dados do banco são iguais aos dados retornados na query
        """

        all_posts_database = db.session.query(Post).all()
        all_posts_database = [{"title": post.title, "body": post.body, "authorId": post.author_id} for post in
                              all_posts_database]

        query_graphql = '''
            {
                allPosts {
                    title
                    body
                    authorId
                }
            }
        '''

        query = {"query": query_graphql}

        response = requests.post('http://localhost:5000/graphql', json=query)
        response = json.loads(response.text)

        response = response['data']['allPosts']

        assert response == all_posts_database

    def test_delete_post_returns_status_code_200(self, create_post):
        new_post_response = json.loads(create_post.text)

        new_post_id = new_post_response['data']['CreatePost']['post']['uuid']

        query_graphql = '''
            mutation ($post_id: Int){
              DeletePost (postId: $post_id) {
                ok
                message
              }
            }
        '''

        variables = {
            "post_id": new_post_id,
        }

        query = {"query": query_graphql, "variables": variables}

        deleted_post_response = requests.post('http://localhost:5000/graphql', json=query)

        assert deleted_post_response.status_code == 200

    def test_delete_post_with_invalid_id(self):
        fake_post_id = 9999999

        query_graphql = '''
            mutation ($post_id: Int){
              DeletePost (postId: $post_id) {
                ok
                message
              }
            }
        '''

        variables = {
            "post_id": fake_post_id,
        }

        query = {"query": query_graphql, "variables": variables}

        response = json.loads(requests.post('http://localhost:5000/graphql', json=query).text)

        ok_status = response['data']['DeletePost']['ok']
        message = response['data']['DeletePost']['message']

        assert ok_status is False and message == "Post inválido."

    def test_delete_post_remove_from_database(self, create_post):
        new_post_response = json.loads(create_post.text)
        new_post_id = new_post_response['data']['CreatePost']['post']['uuid']

        query_graphql = '''
                    mutation ($post_id: Int){
                      DeletePost (postId: $post_id) {
                        ok
                        message
                      }
                    }
                '''

        variables = {
            "post_id": new_post_id,
        }

        query = {"query": query_graphql, "variables": variables}

        requests.post('http://localhost:5000/graphql', json=query).text

        deleted_post = not db.session.query(Post).filter_by(uuid=new_post_id).one_or_none()

        assert deleted_post

    def test_update_post_returns_status_code_200(self):
        rand = random.randrange(0, db.session.query(Post).count())
        post_id = db.session.query(Post.uuid)[rand][0]

        body = FakeRabbit.random_str()
        title = FakeRabbit.random_str()

        query_graphql = '''
                    mutation ($post_id: Int, $title: String, $body: String) {
                        UpdatePost (postId: $post_id, title: $title, body: $body) {
                            ok
                            message
                            post {
                                title
                                body
                            }
                        }
                    }
                '''

        variables = {
            "post_id": post_id,
            "body": body,
            "title": title
        }

        query = {"query": query_graphql, 'variables': variables}

        update_post_response = requests.post('http://localhost:5000/graphql', json=query)

        assert update_post_response.status_code == 200

    def test_update_post_with_invalid_id(self):
        fake_post_id = 99999999

        body = FakeRabbit.random_str()
        title = FakeRabbit.random_str()

        query_graphql = '''
                        mutation ($post_id: Int, $title: String, $body: String) {
                            UpdatePost (postId: $post_id, title: $title, body: $body) {
                                ok
                                message
                                post {
                                    title
                                    body
                                }
                            }
                        }
                    '''

        variables = {
            "post_id": fake_post_id,
            "body": body,
            "title": title
        }

        query = {"query": query_graphql, 'variables': variables}

        update_post_response = json.loads(requests.post('http://localhost:5000/graphql', json=query).text)

        ok_status = update_post_response['data']['UpdatePost']['ok']

        assert ok_status is False

    def test_update_post(self):
        post_id = random.randrange(0, db.session.query(Post).count())

        body = FakeRabbit.random_str()
        title = FakeRabbit.random_str()

        query_graphql = '''
                    mutation ($post_id: Int, $title: String, $body: String) {
                        UpdatePost (postId: $post_id, title: $title, body: $body) {
                            ok
                            message
                            post {
                                title
                                body
                            }
                        }
                    }
                '''

        variables = {
            "post_id": post_id,
            "body": body,
            "title": title
        }

        query = {"query": query_graphql, 'variables': variables}

        updated_post_response = json.loads(requests.post('http://localhost:5000/graphql', json=query).text)

        updated_post_title = updated_post_response['data']['UpdatePost']['post']['title']
        updated_post_body = updated_post_response['data']['UpdatePost']['post']['body']

        post = db.session.query(Post).filter_by(uuid=post_id).one_or_none()

        assert updated_post_title == post.title and updated_post_body == post.body
