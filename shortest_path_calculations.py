from json import load
from flask import Markup
from humanfriendly import format_timespan
def get_nodes():
    with open('./static/json/nodes.json', 'r') as nodes_database:
        nodes = load(nodes_database)
        return nodes

def handle_select_fields(nodes, remove_stairs, allow_shortcuts, only_walkways, only_car_paths):
    for node in nodes.values():
        node['connected_nodes'] = [connected_node for connected_node in node['connected_nodes'] if not (
            (remove_stairs == 'yes' and connected_node['vertex_type'] == 'stairs') or
            (allow_shortcuts == 'no' and connected_node['vertex_type'] == 'shortcut') or
            (only_walkways == 'yes' and connected_node['vertex_type'] == 'car_path') or
            (only_car_paths == 'yes' and connected_node['vertex_type'] == 'walkway')
        )]
    return nodes

def get_shortest_path_details(
        distance,
        starting_point,
        destination,
        remove_stairs,
        allow_shortcuts,
        only_walkways,
        only_car_paths
):
    average_walking_speed = 1.30  # m/s
    average_running_speed = 3.5  # m/s
    average_calories_per_meter_walking = 0.064  # cal/m
    average_calories_per_meter_running = 0.078  # cal/m

    details_dict = {}
    details_dict["Path distance:"] = f"{distance} meters"
    details_dict["Avg time to walk (1.3m/s):"] = format_timespan(distance / average_walking_speed)
    details_dict["Avg time to run (3.5m/s):"] = format_timespan(distance / average_running_speed)
    details_dict["Avg calories burned walking:"] = f"{round(distance * average_calories_per_meter_walking, 2)} cal"
    details_dict["Avg calories burned running:"] = f"{round(distance * average_calories_per_meter_running, 2)} cal"
    details_dict["Route:"] = f"{starting_point} -> {destination}"
    details_dict["Calculation parameters:"] = Markup(
        f"Remove stairs: {remove_stairs}<br>"
        f"Allow shortcuts: {allow_shortcuts}<br>"
        f"Only walkways:  {only_walkways}<br>"
        f"Only car paths: {only_car_paths}<br>"
    )
    return details_dict

def shortest_path_algorithm(nodes, starting_point, destination):
    frontier = [(0, starting_point)]
    cost_so_far = {starting_point: 0}
    came_from = {starting_point: None}

    while frontier:
        frontier.sort(key=lambda x: x[0])
        current_cost, current_node = frontier.pop(0)

        if current_node == destination:
            path = []
            while current_node != starting_point:
                path.append(current_node)
                current_node = came_from[current_node]
            path.append(starting_point)
            path.reverse()
            return path, cost_so_far[destination]

        neighbors = nodes[current_node]['connected_nodes']
        for neighbor in neighbors:
            new_cost = cost_so_far[current_node] + neighbor['distance']
            if neighbor['name'] not in cost_so_far or new_cost < cost_so_far[neighbor['name']]:
                cost_so_far[neighbor['name']] = new_cost
                frontier.append((new_cost, neighbor['name']))
                came_from[neighbor['name']] = current_node
    return None, None