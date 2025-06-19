from flask import Flask
app=None


from application.config import Config
from application.database import db


def create_app():
    app= Flask(__name__)
    app.debug = True  # Example database URI  #3 database model
    app.config.from_object(Config)
    db.init_app(app)  # Initialize the database with the app context
    app.app_context().push() #it has to work in the context of the app adding meaning to the line 6 if not used it gives a runtime error
    return app

app=create_app()

from application.models import *
from application.controllers import *


if __name__ == '__main__':
    app.run(debug=True)