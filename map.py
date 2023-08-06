from flask import Blueprint, render_template

map = Blueprint("map", __name__)

@map.route('/', methods=['GET', 'POST'])
def main_map_page():
    return render_template('main_map_page.html')