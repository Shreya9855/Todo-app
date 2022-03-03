# from .constants import mongo
from .decorators import is_admin
from .models import Task,Boards,User
from mongoengine import *
from flask import Blueprint,request, Response
from flask_jwt_extended import  jwt_required,get_jwt_identity
import json
from bson import ObjectId
from webcolors import hex_to_name,name_to_hex

task = Blueprint('task',__name__)

#AddBoard

@task.route("/api/v1/board",methods = ['POST'])
def add_board():
    try:
        new_board = request.get_json()
        board_collection = Boards()
        board_collection.title = new_board.get('title')
        board_collection.description = new_board.get('description')
        image_url = "https://fakeimg.pl/650x350/0000ff/?text=Hello&font=arial"
        coded_color = image_url.split("/")[-2] 
        board_collection.color = new_board.get('color')
        hex_color = name_to_hex(board_collection.color)
        color_name = hex_to_name(hex_color)
        hex_color= name_to_hex(color_name).replace("#","")
        url_color = image_url.replace(coded_color,hex_color)
        background_color_url = url_color.replace("Hello",board_collection.title)
        board_collection.background_url = background_color_url
        board_collection.save()
        return Response(
			response= json.dumps({
						"message" : "Board Created"
					})
				)
    except Exception as e:
        print(e)
        return Response(
				response= json.dumps({
						"message" : "Board cannot be Created",
					})
				)

#get particular task
@task.route("/api/v1/board",methods = ['GET'])
def get_board():

    boards = Boards.objects()
    board_task = []

    for board in boards:
        print(board.title)
        task_list = []
        task_from_db = Task.objects.filter(boardName = board.title)
        for task in task_from_db:
            task_list.append(task.title)
        print(task_list)
        board_task.append({
                            "board" : board.title,
                            "description" : board.description,
                            "task" : task_list
                        })
                


    return Response(
        response=json.dumps(board_task))






#Add task
@task.route("/api/v1/tasks",methods = ['POST'])
@jwt_required()
def add_task():
    try:
        current_user = get_jwt_identity()
        new_task = request.get_json()
        tasks_collection = Task()
        tasks_collection.title = new_task.get("title")
        tasks_collection.description = new_task.get("description")
        tasks_collection.boardName = new_task.get("boardName")
        tasks_collection.board = Boards.objects.filter(title = tasks_collection.boardName).first().id
        if tasks_collection.boardName != None:
            Task.objects(title=new_task.get("title")).update_one(set__is_a_member_on_board = True)
        tasks_collection.user = ObjectId(current_user)
        tasks_collection.created_by = User.objects.filter(id = tasks_collection.user).first().username
        tasks_collection.save()

        return Response(
			response= json.dumps({
						"message" : "Task Created"
					})
				)

    except Exception as e:
        print(e)
        return Response(
				response= json.dumps({
						"message" : "Task cannot be Created",
					})
				)




#get task
@task.route("/api/v1/tasks",methods = ['GET'])
@jwt_required()
@is_admin
def read_task():
    try:
        task_from_db = Task.objects
        tasks = []
        for task in task_from_db:
            tasks.append(task.to_json())
        print(tasks)
        print(task_from_db)
        if task_from_db:
            return Response(
                    response=json.dumps({
                        "task " : tasks
                    }))
        else:
                return Response(
                    response=json.dumps({
                        "msg" : "tasks"
                    }))
            

    except Exception as e:
        print(e)
       


#get particular task
@task.route("/api/v1/taskuser",methods = ['GET'])
@jwt_required()
def read_task_by_user():
    try:
        current_user = get_jwt_identity()
        task_from_db = Task.objects.filter(user = current_user)
        print(task_from_db)
        tasks = []
        for task in task_from_db:
            tasks.append(task.to_json())
        # print(tasks)
        # print(task_from_db)
        if task_from_db:
            return Response(
                    response=json.dumps({
                        "task " : tasks
                    }))
        else:
                return Response(
                    response=json.dumps({
                        "msg" : "tasks"
                    }))
            

    except Exception as e:
        print(e)

@task.route("/api/v1/tasks/<id>",methods = ['PATCH'])
@jwt_required()
def update_task(id):
    try:
        task_updated = request.get_json()
        current_user = get_jwt_identity()
        created_by = User.objects.filter(id = ObjectId(current_user)).first().username
        print(created_by)

        Task.objects.filter(id = id).update(
            set__title = task_updated.get('title'),
            set__description = task_updated.get('description'),
            set__created_by = created_by
        )
        
        return Response(
                response=json.dumps({
                    "msg" : "task updated"
                }))
        
        
    except Exception as e:
        print(e)
        return Response(
                response=json.dumps({
                    "msg" : "cannot perform update operation"
                }))

@task.route("/api/v1/tasks/<id>",methods = ['DELETE'])
@jwt_required()
def delete_task(id):
    try:
        Task.objects(id = id).delete()
        return Response(
                response=json.dumps({
                    "msg" : "task deleted"
                }))
        
    except Exception as e:
        print(e)

