from os import getenv

from flask import Flask
from map import map
from report_system import report_system
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = getenv("FLASKSECRETKEY")
app.register_blueprint(map)
app.register_blueprint(report_system)

app.run(host="0.0.0.0", port=5000, debug=True)

