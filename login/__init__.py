from flask import  Flask
from datetime import timedelta
from .constants import mongo , jwt , mail
from .config import mail_settings




def create_app():

    app = Flask(__name__)
    
    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')

    from .task import task
    app.register_blueprint(task, url_prefix='/')

    from .comment import comment
    app.register_blueprint(comment, url_prefix='/')


    mongo.init_app(app)

    jwt.init_app(app)
    app.config['JWT_SECRET_KEY'] = 'Secret_Key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

    app.config.update(mail_settings)
    mail.init_app(app)


    return app
