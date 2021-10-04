from peewee import *
import os

db = SqliteDatabase('my_database.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(Model):
    '''
    User Model containing (2) Fields:
            1 - username
                -   string, unique=True, required
            2 - password
                -   string (hashed), required
    '''
    username = CharField(max_length=255, unique=True)
    password = CharField(max_length=255)

    class Meta:
        database = db


class Task(Model):
    '''
    Task Model containing (3) Fields:
            1 - name
                -   string, required
            2 - performed
                -   date, optional
            3 - performed_by
                -   performed_by, relational, optional
    '''
    name = CharField(max_length=255)
    performed = DateTimeField(null=True)
    performed_by = ForeignKeyField(model=User, null=True)

    class Meta:
        database = db
