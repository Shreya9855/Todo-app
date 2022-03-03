from .models import User
from .config import SECRET_KEY
from functools import wraps
import json
from flask import Response, request
from flask_jwt_extended import get_jwt_identity




def is_admin(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        current_user = get_jwt_identity() 
        user_db = User.objects.filter(id = current_user).first().userType
        # print(user_db)
        if not  user_db == 'admin':
            return Response(
						response= json.dumps({
								"message" : "You don't have access to this."
							})
						)

        if  user_db == 'admin':
            return f()


    return decorator