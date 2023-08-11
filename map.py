from flask import Blueprint, render_template, request
from forms import ShortestPathCalculationForm

MAP = Blueprint("map", __name__)


@MAP.route('/', methods=['GET', 'POST'])
def main_map_page():
    form = ShortestPathCalculationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            #do shortest path calculation
            pass
        return render_template('main_map_page.html', form=form, open_sidebar=True)
    return render_template('main_map_page.html', form=form, open_sidebar=False)