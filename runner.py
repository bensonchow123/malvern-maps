from flask import Flask
from map import map

app = Flask(__name__)
app.register_blueprint(map)

app.run(host="127.0.0.1", port=5000, debug=True)



