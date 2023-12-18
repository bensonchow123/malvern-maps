from os import getenv
from time import sleep
from threading import Thread
from datetime import datetime
from bson.objectid import ObjectId

from flask import Blueprint, render_template, request, flash, session, g, Markup
from forms import ShortestPathCalculationForm, ReportEventForm, ManageStaffForm, RemoveReportedEventForm, FilterEventsForm
from shortest_path_calculations import get_nodes, handle_select_fields, shortest_path_algorithm, get_shortest_path_details
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

malvern_maps_cluster = MongoClient(getenv("MONGODB_URL"))
malvern_maps_db = malvern_maps_cluster["malvern-maps"]
reported_events_db = malvern_maps_db["reported-events"]

map = Blueprint("map", __name__)

thirty_newest_events = None

@map.before_request
def handle_staff_details():
    if 'email' in session:
        update_staff_session()
    g.email = session.get('email', None)
    g.admin = session.get('admin', None)

@map.record_once
def fetch_data_on_start(setup_state):
    Thread(target=fetch_data_periodically).start()

def update_staff_session():
    email = session['email']
    staff_data = malvern_maps_db["staff-emails"].find_one({"email": email})
    if not staff_data:
        session.clear()
    else:
        session['admin'] = staff_data["admin"]

def fetch_data_periodically():
    global thirty_newest_events
    while True:
        thirty_newest_events = get_reported_events()
        print(thirty_newest_events)
        sleep(60)

def append_event(node, description):
    reported_events_db.insert_one({
        "timestamp": int(datetime.utcnow().timestamp()),
        "node": node,
        "description": description
    })

def get_reported_events():
    events = reported_events_db.find().sort("timestamp", -1).limit(30)
    return list(events)

def do_staff_action(email, action):
    if action == "remove":
        malvern_maps_db["registered-accounts"].delete_many({"email": email})
        malvern_maps_db["staff-emails"].delete_many({"email": email})
        return

    admin = False
    if action == "admin":
        admin = True
    malvern_maps_db["staff-emails"].update_one(
        {"email": email},
        {"$set": {"admin": admin}},
        upsert=True
    )

def delete_event(event_id):
    malvern_maps_db["reported-events"].delete_one({"_id": ObjectId(event_id)})

def get_filtered_events(groups_to_filter, number_to_filter):
    filter = {"node": {"$regex": ""}}
    if groups_to_filter:
        filter["node"]["$regex"] += ".*[" + "".join(groups_to_filter) + "].*"
    if number_to_filter:
        filter["node"]["$regex"] += str(number_to_filter) + "$"

    results = reported_events_db.find(filter).sort('timestamp', -1).limit(30)
    results = list(results)
    # prioritize matches with fewer irrelevant characters
    results.sort(key=lambda x: len([c for c in x['node'] if c not in groups_to_filter]))
    return results


@map.route('/', methods=['GET', 'POST'])
def main_map_page():
    def handle_render(
            shortest_path_details = None,
            shortest_path_calculation_results = None,
            open_sidebar=False,
            open_reported_node_modal=False,
            open_report_event_modal=False,
            open_remove_reported_event_modal=False,
            open_manage_staff_modal=False,
            open_filter_events_modal=False,
            flash_category=None,
            flash_message_content=None,
            events_to_display = thirty_newest_events
    ):
        if flash_message_content and flash_category is not None:
            flash(flash_message_content, flash_category)

        return render_template(
            'main_map_page.html',
            shortest_path_details=shortest_path_details,
            shortest_path_calculation_results=shortest_path_calculation_results,
            shortest_path_calculation_form=shortest_path_calculation_form,
            report_event_form=report_event_form,
            remove_reported_event_form=remove_reported_event_form,
            manage_staff_form=manage_staff_form,
            filter_events_form=filter_events_form,
            open_sidebar=open_sidebar,
            open_reported_node_modal=open_reported_node_modal,
            open_report_event_modal=open_report_event_modal,
            open_remove_reported_event_modal= open_remove_reported_event_modal,
            open_manage_staff_modal=open_manage_staff_modal,
            open_filter_events_modal=open_filter_events_modal,
            events_to_display=events_to_display
        )

    shortest_path_calculation_form = ShortestPathCalculationForm()
    report_event_form = ReportEventForm()
    remove_reported_event_form = RemoveReportedEventForm()
    manage_staff_form = ManageStaffForm()
    filter_events_form = FilterEventsForm()

    if request.method == "POST":
        if shortest_path_calculation_form.submit.data:
            if shortest_path_calculation_form.validate_on_submit():
                form = shortest_path_calculation_form

                starting_point = form.starting_point.data.casefold()
                destination= form.destination.data.casefold()

                remove_stairs, allow_shortcuts = form.remove_stairs.data, form.allow_shortcuts.data
                only_walkways, only_car_paths = form.only_walkways.data, form.only_car_paths.data

                nodes = get_nodes()
                select_fields_filtered_nodes = handle_select_fields(
                    nodes=nodes,
                    remove_stairs=remove_stairs,
                    allow_shortcuts=allow_shortcuts,
                    only_walkways=only_walkways,
                    only_car_paths=only_car_paths
                )
                path, distance = shortest_path_algorithm(
                    nodes=select_fields_filtered_nodes,
                    starting_point=starting_point,
                    destination=destination
                )

                if path is None:
                    return handle_render(
                        flash_category="danger",
                        flash_message_content="No path found!"
                    )
                else:
                    shortest_path_details = get_shortest_path_details(
                        distance=distance,
                        starting_point=starting_point,
                        destination=destination,
                        remove_stairs=remove_stairs,
                        allow_shortcuts=allow_shortcuts,
                        only_walkways=only_walkways,
                        only_car_paths=only_car_paths
                    )
                    print(path)
                    return handle_render(
                        shortest_path_details=shortest_path_details,
                        shortest_path_calculation_results=path,
                        flash_category="success",
                        flash_message_content=Markup(
                            f'Shortest path is shown on map, it have a distance of {distance} meters! <br>'
                            f'<a href="#" data-bs-toggle="modal" data-bs-target="#shortestPathDetailsModal">Click here for more details!</a>'
                        )
                    )
            return handle_render(open_sidebar=True, open_report_event_modal=False)

        if report_event_form.submit_report.data:
            if report_event_form.validate_on_submit():
                if not g.email:
                    return handle_render(
                        flash_category="danger",
                        flash_message_content="Staff login required to report an event!"
                    )

                node = report_event_form.node_to_report.data.casefold()
                description = report_event_form.description.data
                append_event(node, description)
                return handle_render(
                    open_sidebar=True,
                    flash_category="success",
                    flash_message_content="Report submitted! Refresh in a minute to view."
                )
            return handle_render(open_sidebar=True, open_report_event_modal=True)

        if remove_reported_event_form.submit_event_to_remove.data:
            if not g.email:
                return handle_render(
                    flash_category="danger",
                    flash_message_content="Staff login required to remove an event!"
                )
            if remove_reported_event_form.validate_on_submit():
                event_id = remove_reported_event_form.event_to_remove_id.data
                delete_event(event_id)
                return handle_render(
                    open_sidebar=True,
                    flash_category="success",
                    flash_message_content="Event removed! Refresh in a minute to view."
                )
            return handle_render(open_sidebar=True, open_remove_reported_event_modal=True)

        if manage_staff_form.submit_staff_action.data:
            if not g.admin:
                return handle_render(
                    flash_category="danger",
                    flash_message_content="Only admins can preform staff action!"
                )
            if manage_staff_form.validate_on_submit():
                email = manage_staff_form.email.data
                action = manage_staff_form.action.data
                do_staff_action(email, action)
                return handle_render(
                    open_sidebar=True,
                    flash_category="success",
                    flash_message_content=f"Action to {email} is finished! Refresh in a minute to view."
                )
            return handle_render(open_sidebar=True, open_manage_staff_modal=True)

        if filter_events_form.submit_filter_param.data:
            if filter_events_form.validate_on_submit():
                groups_to_filter = filter_events_form.groups_to_filter.data
                number_to_filter = filter_events_form.number_to_filter.data
                filtered_events = get_filtered_events(groups_to_filter, number_to_filter)
                if filtered_events:
                    return handle_render(
                        open_sidebar=True,
                        open_reported_node_modal=True,
                        events_to_display=filtered_events
                    )
                else:
                    return handle_render(
                        open_sidebar=True,
                        open_reported_node_modal=True,
                        flash_category="danger",
                        flash_message_content=f"No matching events found.",
                    )
            return handle_render(open_sidebar=True, open_filter_events_modal=True)

    return handle_render()