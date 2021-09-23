import os
from typing import Optional

import graphene
from flask import Flask
from flask_graphql import GraphQLView
from flask_sqlalchemy import SQLAlchemy
from graphene_sqlalchemy import SQLAlchemyObjectType

app = Flask(__name__)
app.debug = True

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Post(db.Model):
    __tablename__ = 'posts'

    uuid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.uuid'))

    def __repr__(self):
        return '<Post %r>' % self.title


class User(db.Model):
    __tablename__ = 'users'

    uuid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), index=True, unique=True)
    password = db.Column(db.String(256))
    posts = db.relationship('Post', backref='author')

    def __repr__(self):
        return '<User %r>' % self.username


class PostType(SQLAlchemyObjectType):
    class Meta:
        model = Post


class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User


class Query(graphene.ObjectType):
    # posts
    get_all_posts = graphene.List(PostType)
    get_post = graphene.Field(PostType, post_id=graphene.Int())

    # users
    get_all_users = graphene.List(UserType)
    get_user = graphene.Field(UserType, user_id=graphene.Int())

    @staticmethod
    def resolve_get_all_posts(self, info):
        return db.session.query(Post).all()

    @staticmethod
    def resolve_get_all_users(self, info):
        return db.session.query(User).all()

    @staticmethod
    def resolve_get_post(self, info, post_id):
        post = db.session.query(Post).filter_by(uuid=post_id).one_or_none()

        if not post:
            raise Exception('Post não encontrado')

        return post

    @staticmethod
    def resolve_get_user(self, info, user_id):
        user = db.session.query(User).filter_by(uuid=user_id).one_or_none()

        if not user:
            raise Exception('Usuário não encontrado')

        return user


class UpdatePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int()
        title = graphene.String()
        body = graphene.String()

    ok = graphene.Boolean()
    message = graphene.String()
    post = graphene.Field(PostType)

    @staticmethod
    def mutate(self, info, post_id, title: Optional[str] = None, body: Optional[str] = None):
        post = db.session.query(Post).filter_by(uuid=post_id).one_or_none()

        if not post:
            ok = False
            message = "Post não encontrado"

            return UpdatePost(ok=ok, message=message)

        if title:
            post.title = title

        if body:
            post.body = body

        db.session.add(post)
        db.session.commit()

        ok = True
        message = "Post atualizado"

        return UpdatePost(ok=ok, message=message, post=post)


class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        body = graphene.String(required=True)
        username = graphene.String(required=True)

    post = graphene.Field(lambda: PostType)
    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, title, body, username):
        user = User.query.filter_by(username=username).first()
        post = Post(title=title, body=body)

        if not user:
            ok = False
            message = "Usuário inválido"

            return CreatePost(ok=ok, message=message)

        post.author = user

        db.session.add(post)
        db.session.commit()

        ok = True
        message = "Post criado"

        return CreatePost(ok=ok, message=message, post=post)


class DeletePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.Int()

    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, post_id):
        post = db.session.query(Post).filter_by(uuid=post_id).one_or_none()

        if not post:
            ok = False
            message = "Post inválido."

            return DeletePost(ok=ok, message=message)

        db.session.delete(post)
        db.session.commit()

        ok = True
        message = "Post removido com sucesso."

        return DeletePost(ok=ok, message=message)


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        password = graphene.String()

    ok = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    @staticmethod
    def mutate(self, info, username, password):
        user = db.session.query(User).filter_by(username=username).one_or_none()

        if user:
            ok = False
            message = "username já existe"

            return CreateUser(ok=ok, message=message)

        new_user = User(username=username, password=password)

        db.session.add(new_user)
        db.session.commit()

        ok = True
        message = "Criado com sucesso"

        return CreateUser(ok=ok, message=message, user=new_user)


class DeleteUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int()

    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(self, info, user_id):
        user = db.session.query(User).filter_by(uuid=user_id).first()

        if not user:
            ok = False
            message = "Falha ao remover usuário"

            return DeleteUser(ok=ok, message=message)

        db.session.delete(user)
        db.session.commit()

        ok = True
        message = "Usuário removido com sucesso."

        return DeleteUser(ok=ok, message=message)


class UpdateUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int()
        username = graphene.String()
        password = graphene.String()

    ok = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    @staticmethod
    def mutate(self, info, user_id, username: Optional[str] = None, password: Optional[str] = None):
        user = db.session.query(User).filter_by(uuid=user_id).one_or_none()

        if not user:
            ok = False
            message = "Usuário não encontrado"

            return UpdateUser(ok=ok, message=message)

        if username:
            user.username = username

        if password:
            user.password = password

        db.session.add(user)
        db.session.commit()

        ok = True
        message = "Usuário atualizado"

        return UpdateUser(ok=ok, message=message, user=user)


class Mutation(graphene.ObjectType):
    # posts
    CreatePost = CreatePost.Field()
    DeletePost = DeletePost.Field()
    UpdatePost = UpdatePost.Field()

    # users
    CreateUser = CreateUser.Field()
    DeleteUser = DeleteUser.Field()
    UpdateUser = UpdateUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    )
)

if __name__ == '__main__':
    app.run()
