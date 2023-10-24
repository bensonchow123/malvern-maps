from os import getenv

from flask import Blueprint, render_template, request, flash, session, g
from forms import ShortestPathCalculationForm, ReportEventForm
from shortest_path_calculation import get_nodes, handle_select_fields, shortest_path_algorithm
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

malvern_maps_cluster = MongoClient(getenv("MONGODB_URL"))
malvern_maps_db = malvern_maps_cluster["malvern-maps"]

map = Blueprint("map", __name__)

@map.before_request
def get_staff_details():
    g.email = session.get('email', None)

def append_event(node, description):
    malvern_maps_db["reported-events"].insert_one({
        "node": node,
        "description": description
    })

@map.route('/', methods=['GET', 'POST'])
def main_map_page():
    def handle_render(open_sidebar, open_modal, flash_category=None, flash_message_content=None):
        if flash_message_content and flash_category is not None:
            flash(flash_message_content, flash_category)

        return render_template(
            'main_map_page.html',
            shortest_path_calculation_form=shortest_path_calculation_form,
            report_event_form=report_event_form,
            open_sidebar=open_sidebar,
            open_modal=open_modal
        )

    shortest_path_calculation_form = ShortestPathCalculationForm()
    report_event_form = ReportEventForm()

    if request.method == "POST":
        if shortest_path_calculation_form.submit.data:
            if shortest_path_calculation_form.validate_on_submit():
                starting_point = shortest_path_calculation_form.starting_point.data
                destination= shortest_path_calculation_form.destination.data
                nodes = get_nodes()
                select_fields_filtered_nodes = handle_select_fields(shortest_path_calculation_form, nodes)
                path, distance = shortest_path_algorithm(
                    nodes=select_fields_filtered_nodes,
                    starting_point=starting_point,
                    destination=destination
                )

                if path is None:
                    return handle_render(
                        open_sidebar=False,
                        open_modal=False,
                        flash_category="danger",
                        flash_message_content="No path found!"
                    )
                else:
                    return handle_render(
                        open_sidebar=False,
                        open_modal=False,
                        flash_category="success",
                        flash_message_content=f'The shortest path from {starting_point} to {destination} is {path} with a distance '
                        f'of {distance}'
                    )
            return handle_render(open_sidebar=True, open_modal=False)

        if report_event_form.submit_report.data:
            if report_event_form.validate_on_submit():
                node = report_event_form.node_to_report.data
                description = report_event_form.description.data
                append_event(node, description)
                return handle_render(
                    open_sidebar=False,
                    open_modal=False,
                    flash_category="success",
                    flash_message_content="Report submitted successfully!"
                )
            return handle_render(open_sidebar=True, open_modal=True)
    return handle_render(False, False)