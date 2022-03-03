
# from .constants import mongo
from mongoengine import *
from datetime import  datetime
from functools import wraps


userType = ["admin" , "user" , "guest" ] 

class User(Document):
    email = EmailField(required = True, unique=True)
    username = StringField(required = True, unique=True, max_length=50)
    password = StringField(required = True)
    userType = StringField(choices = userType,default= "guest" )
    is_email_confirmed = BooleanField(required = True,default = False)
    last_logged_in = DateTimeField(default=datetime.utcnow)
    is_current_user = BooleanField(required = True,default=False) 
    code = DecimalField(default = 000000)
    image = StringField() 

class Boards(Document):
    title = StringField(required = True)
    description = StringField()
    color = StringField()
    background_url = URLField()
    created_by = ReferenceField(User)
    created_on = DateTimeField(default=datetime.utcnow)
    task_contains = ListField()


class Task(Document):
    title = StringField(required = True, max_length=50)
    description = StringField()
    created_by = StringField(required = True)
    created_on = DateTimeField(default=datetime.utcnow)
    user = ReferenceField(User) 
    updated_on = DateTimeField(default=datetime.utcnow)
    is_a_member_on_board = BooleanField(required = True,default=False)
    boardName = StringField(required = False)
    board = ReferenceField(Boards)


class Comment(Document):
    title = StringField()
    comment_on = ReferenceField(Task)
    created_by = ReferenceField(User)
    created_on = DateTimeField(default=datetime.utcnow)
