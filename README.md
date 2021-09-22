# GraphQL API with Python
## [Flask](https://github.com/pallets/flask) and [Graphene](https://github.com/graphql-python/graphene)


This is an API built for the purpose of studying the GraphQL technology and its integration with Python and the Flask framework.
The library Graphene was used to build it.

---

## Summary

1. [What is the API?](#What-is-the-API?)
2. [API](#API-Docs)


## What is the API?

This API has two main models: Users and Posts. So, basically the goal here is to create a CRUD for them.
It will also be possible to link a post to a user (its creator, in this case).

## How to run the project

Go into your work directory and clone this repository:

```bash
$ git clone git@github.com:vitumenezes/flask-with-graphql.git
```

Now you will need to create a virtual environment to correctly run the projet.

There are differents ways to do it, here we will use the standard python lib called **venv**.

The virtualenv will be created in a folder. And where, leave it?
I suggest creating it with a "." in front of the name, for example: **.venv**.
And create it **inside** the project folder, so we know that that virtual environment belongs to the project itself.
It's just a pattern and there are several, use whichever you prefer.

Enter the folder:

```bash
$ cd flask-with-graphql
```

Create the virtual environment:
```bash
$ python -m venv .venv
```
> Use Python 3 versions to run this project. You can manage them with [Pyenv](https://github.com/pyenv/pyenv) ;)

Now, activate it:
```bash
$ source .venv/bin/activate
```

After that, you will now see the active prefix on your terminal:
```bash
(.venv) user@hostname$
```

> This means that the virtualenv is active.
Make shure it is always active while using the project for development purposes.

Now, install the depedencies on requirements.txt:
Enter a python interpreter of your choice and import the **SQLAlchemy** instance from the **main.py** file

Before running the project, we first need to create the tables in our sqlite database.
Enter a python interpreter of your choice and import the **SQLAlchemy** (called **db**) instance from the **main.py** file.
```bash
(.venv) $ python

...

>>> from main import db
>>> db.create_all()
```

Now, run it:
```bash
(.venv) $ python main.py runserver
```

Access http://127.0.0.1:5000/graphql to see the interface to write and test **graphql** queries.

<img src=".github/graphql-interface.png" width="80%"/>

## API Docs