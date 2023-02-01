from flask import Flask, render_template
from flask_admin import Admin
from flask_login import LoginManager
from uuid import uuid4
from sqlalchemy import select

from app.db.session import SyncSession, scope
from app.core.config import settings

from app.models.messenger import Messenger
from app.admin.views.messeger import MessengerView

from app.models.chat import Message, Chat
from app.admin.views import message, chat

from app.models.devices import Device
from app.admin.views.device import DeviceView


session = SyncSession(settings.SYNC_SQLALCHEMY_DATABASE_URI)

# Instantiate the Flask application with configurations
secureApp = Flask(__name__)


# Configure a specific Bootswatch theme
secureApp.config['SECRET_KEY'] = 'secretkey'


# set session in scope
class middleware():
    '''
    Simple WSGI middleware
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scope.set(str(uuid4()))        
        try:
            return self.app(environ, start_response)
        except:
            session.session.rollback()
        finally:
            session.session.expunge_all()
            session.scoped_session.remove()


secureApp.wsgi_app = middleware(secureApp.wsgi_app)


#settings for auth
# @login.user_loader
# def load_user(user_id):
#     return sync_session.execute(
#         select(User).filter_by(id=user_id)
#     ).scalars().first()


# create admin
admin = Admin(secureApp, name='Admin', base_template='my_master.html', template_mode='bootstrap4')
admin.add_view(MessengerView(Messenger, session.session))
admin.add_view(DeviceView(Device, session.session))
admin.add_view(chat.ChatView(Chat, session.session))
admin.add_view(message.MessageView(Message, session.session))
# Create a ModelView to add to our administrative interface


# Add administrative views to Flask-Admin

# Define the index route
# @secureApp.route('/')
# def index():
#     return render_template('index.html')
