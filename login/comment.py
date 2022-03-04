from flask import Blueprint,request, Response
from .models import Comment,User,Task
from mongoengine import *
import json

comment = Blueprint('comment',__name__)

@comment.route("/api/v1/comment",methods = ['POST'])
def add_comment():
    try:
        new_comment = request.get_json()
        comment_collection = Comment()
        comment_collection.title = new_comment.get('title')
        comment_collection.created_by = new_comment.get('created_by')
        comment_collection.comment_on = new_comment.get('comment_on')
        user = User.objects.filter(username = new_comment.get('created_by')).first().id
        task = Task.objects.filter(title = new_comment.get('comment_on')).first().id
        comment_collection.created_by = user
        comment_collection.comment_on = task

        comment_collection.save()
        return Response(
			response= json.dumps({
						"message" : "Comment Created"
					})
				)
    except Exception as e:
        print(e)
        return Response(
				response= json.dumps({
						"message" : "Problem : Comment cannot be Created",
					})
				)