#Application
from appl import create_app
from appl.models import User
from appl import db

app = create_app()


if __name__ == '__main__':
    app.run(port=5006, host='0.0.0.0')
