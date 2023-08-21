from json import load

def get_nodes():
    with open('./static/json/nodes.json', 'r') as nodes_database:
        nodes = load(nodes_database)
        return nodes

def handle_select_fields(form, nodes):
    remove_stairs, allow_shortcuts = form.remove_stairs.data, form.allow_shortcuts.data
    only_walkways, only_car_paths = form.only_walkways.data, form.only_car_paths.data
    for node in nodes.values():
        node['connected_nodes'] = [connected_node for connected_node in node['connected_nodes'] if not (
            (remove_stairs == 'yes' and connected_node['vertex_type'] == 'stairs') or
            (allow_shortcuts == 'no' and connected_node['vertex_type'] == 'shortcut') or
            (only_walkways == 'yes' and connected_node['vertex_type'] == 'car_path') or
            (only_car_paths == 'yes' and connected_node['vertex_type'] == 'walkway')
        )]
    return nodes

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