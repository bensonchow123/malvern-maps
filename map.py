from flask import Blueprint, render_template, request, flash
from forms import ShortestPathCalculationForm
from shortest_path_calculation import get_nodes, handle_select_fields, shortest_path_algorithm

map = Blueprint("map", __name__)

@map.route('/', methods=['GET', 'POST'])
def main_map_page():
    form = ShortestPathCalculationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            starting_point, destination = form.starting_point.data, form.destination.data
            nodes = get_nodes()
            select_fields_filtered_nodes = handle_select_fields(form, nodes)
            path, distance = shortest_path_algorithm(select_fields_filtered_nodes, starting_point, destination)
            if path is None:
                flash("No path found", "danger")
                return render_template('main_map_page.html', form=form, open_sidebar=True)
            flash(
                f'The shortest path from {starting_point} to {destination} is {path} with a distance of {distance}',
                 category='success')
            return render_template('main_map_page.html', form=form, open_sidebar=False)
        return render_template('main_map_page.html', form=form, open_sidebar=True)
    # if device with big screen open sidebar, if device with small screen, open sidebar
    return render_template(
        'main_map_page.html',
        form=form,
        open_sidebar=False
    )