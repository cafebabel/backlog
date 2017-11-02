from pathlib import Path

from flask import Flask
from flask_mail import Mail

from .core.database import Database


app = Flask(__name__)
ROOT_PATH = Path(__file__).parent.parent
app.root_path = str(ROOT_PATH)
app.config.from_pyfile(str(ROOT_PATH / 'settings.py'))
if Path.exists(ROOT_PATH / 'settings.local.py'):
    app.config.from_pyfile(str(ROOT_PATH / 'settings.local.py'))
db = Database(app)
mail = Mail(app)


from .articles import views  # noqa: F401, F801
from .api import views  # noqa: F401, F801
from .core import commands, views  # noqa: F401, F801
from .users import views  # noqa: F401, F801

# Dev specific packages
try:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)
except ModuleNotFoundError:
    pass


if __name__ == '__main__':
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'),
            debug=app.config.get('DEBUG'))
