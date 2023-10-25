from os import getenv
from datetime import datetime

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, render_template
from map import map
from report_system import report_system
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["15 per minute", "500 per hour"],
        storage_uri="memory://",
)

@app.template_filter('datetimeformat')
def datetimeformat(value):
    return datetime.utcfromtimestamp(value).strftime('%B %d, %Y, %H:%M:%S UTC')

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("rate_limited.html", rate_limit_exceeded=e.description), 429

app.config['SECRET_KEY'] = getenv("FLASKSECRETKEY")

app.register_blueprint(map)
app.register_blueprint(report_system),

app.run(host="0.0.0.0", port=5000, debug=True)

