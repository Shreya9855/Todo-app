
from login.decorators import is_admin
from .constants import bcrypt , mail
from .models import User
from mongoengine import *
from flask import Blueprint, request ,Response , session
from flask_jwt_extended import create_access_token, jwt_required,get_jwt_identity
import json , random
from flask_mailing import  Message



auth = Blueprint('auth', __name__)

#register users
@auth.route("/api/v1/users", methods=["POST"])
def register():
	try:
		new_user = request.get_json()
		users_collection = User()
		users_collection.email = new_user.get("email")
		users_collection.username =	new_user.get("username")
		users_collection.password =	bcrypt.generate_password_hash(new_user.get("password"),rounds=None).decode('utf-8')		
		users_collection.userType =	new_user.get("userType")
		image_url = "https://fakeimg.pl/350x200/?text=Hello&font=arial"
		letters = "".join(str([s[0] for s in users_collection.username.split()]))
		users_collection.background_url = image_url.replace("Hello",letters)
		users_collection.save()
		return Response(
				response= json.dumps({
						"message" : "User Created"
					})
				)

	except Exception as e:
		print(e)
		return Response(
				response= json.dumps({
						"message" : "Problem : Exception occured.User cannot be Created",
					})
				)

#send mail
@auth.get("/api/v1/usercode")
async def send_otp():
	try:
		for user in User.objects:
			code_sent_to = user.email
		code = ''.join([str(random.randint(0,9)) for i in range(6)])
		check_user = User.objects.filter(email=code_sent_to).first()
		if check_user:
			User.objects(email = code_sent_to).update_one(set__code = code)
		msg = Message(subject="NEW OTP",
						sender = "MAIL_USERNAME",
						recipients= [code_sent_to],
						body= "Your OTP code is : " + (code))
		await mail.send_message(msg)
		return Response(
			response= json.dumps({
					"message" : "Code has been sent"
					})
				)

	except Exception as e:
		print(e)
		return Response(
			response= json.dumps({
				"message" : "Problem : Exception occured.Cannot send the code"
			})
		)

#Email confirmation
@auth.route("/api/v1/usercode", methods=["POST"])
def check_code():
	try:
		code_ret = request.get_json()
		for user in User.objects:
				code_sent_to = user.email
		check_user = User.objects.filter(email=code_sent_to).first()
		if check_user:
			if check_user.code == code_ret.get("code"):
				User.objects(email = code_sent_to).update_one(set__is_email_confirmed = True)
				return Response(
				response= json.dumps({
						"message" : "Email has been confirmed"
						})
					)
			else:
					return Response(
				response= json.dumps({
						"message" : "Code has time out or code is not valid.Try again"
						})
					)
	except Exception as e:
		print(e)
		return Response(
			response= ({
				"message" : "Problem : Exception occured.Cannot verify the email"
			})
		)

#for login
@auth.route("/api/v1/login", methods=["POST"])
def login():
	try:
		login_details = request.get_json() # store the json body request
		check_user = User.objects.filter(email=login_details.get('email')).first()
		if check_user:
			if  check_user.is_email_confirmed == True:
				if bcrypt.check_password_hash(check_user.password,login_details.get("password")):                  
					access_token = create_access_token(identity=str(check_user.id)) # create jwt token

					User.objects(email = login_details.get('email')).update_one(is_current_user = True)
					if User.objects(login_details.get('userType')) == "admin":
						User.objects(email = login_details.get('email')).update_one(userType = "admin")
					else:
						User.objects(email = login_details.get('email')).update_one(userType = "admin")
					# print(access_token)
					return Response(
						response= json.dumps({
								"message" : "User logged in",
								"access_token": access_token
							})
						)
				else:
					return json.dumps({'msg': 'The email or password is incorrect'})
		return json.dumps({'message': 'The email is invalid'})
	except Exception as e:
		print(e)
		return json.dumps({'message': ' Problem : Exception occured. Could not login.'})

#get profile of the logged in user
@auth.route("/api/v1/user", methods=["GET"])
@jwt_required()
def profile():
	try:
		current_user = get_jwt_identity() # Get the identity of the current user
		User.objects(id = current_user).update_one(is_current_user = True)

		user_from_db= User.objects.filter(id = current_user).aggregate([{"$project": {
			'_id' : 0,
			'password' : 0,
			'userType' : 0,
			'is_email_confirmed' : 0,
			'last_logged_in' : 0,
			'code' : 0
			}}])
		users = []
		for user in user_from_db:
			users.append(user)					
		if user_from_db:
			return Response(
						response= json.dumps({
								"profile" : users
							})
						)
		else:
			return Response(
						response= json.dumps({
								"message" : "Profile Not found"
							})
						)
	
	except Exception as e:
		print(e)
		return Response(
			response= json.dumps({
				"message" : "Problem : Exception occured.Couldn't get your user data"
			})
		)

@auth.route("/api/v1/users", methods=["GET"])
@jwt_required()
@is_admin
def profiles():
	try:
		current_user = get_jwt_identity()
		find_user = User.objects.filter(id = current_user)
		for user in find_user:
			is_current_user = user.is_current_user

		if is_current_user == False:
				return Response(
				response= json.dumps({
				"msg" : "You have to be logged in for this operation"
					})
				)
		else:
			user_from_db= User.objects().aggregate([{"$project": {
                '_id' : 0,
                'password' : 0,
                'last_logged_in' : 0,
                'code' : 0
                }}])
			users = []
			for user in user_from_db:
				users.append(user)					
			if user_from_db:
				return Response(
                            response= json.dumps({
                                    "profile" : users
                                })
                            )
			else:
				return Response(
                    response= json.dumps({
                                    "message" : "Profile Not found"
                                })
                            )   
	except Exception as e:
		print(e)
		return Response(
			response= json.dumps({
				"message" : "Problem : Exception occured.Couldn't get your user data"
			})
		)

@auth.route("/api/v1/logout")
@jwt_required(optional= True)
def logout():
	try:
		current_user = get_jwt_identity()
		
		find_user = User.objects.filter(id = current_user)
		for user in find_user:
			is_current_user = user.is_current_user
			username = user.username
		
		
		if is_current_user == False:
				return Response(
				response= json.dumps({
				"msg" : "You have to be logged in to log out"
					})
				)
		else:
			User.objects.filter(id = current_user).update(is_current_user = False)
			return Response(
				response= json.dumps({
				"msg" : "Logged out",
				"username" : username
					})
				)
	except Exception as e:
		print(e)
		return Response(
			response= json.dumps({
				"message" : "Problem : Exception occured.Couldn't logout"
			})
		)