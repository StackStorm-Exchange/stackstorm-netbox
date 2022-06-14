import argparse
import os

import jinja2
import requests


def get_spec(host, https, port, ssl_verify):
    protocol = 'https://' if https else 'http://'
    url = "{}{}:{}/api/swagger.json".format(protocol, host, port)
    print(f"Getting API spec from NetBox instance at {host}")
    try:
        response = requests.get(url, verify=ssl_verify)
        return response.json()
    except Exception as e:
        print(f"Failed to get the API spec!: {e}")
        exit(1)


def sanitize_parameters(parameters):
    for parameter in parameters:
        if parameter['name'] == 'tags':
            parameter['description'] = "Array of tag strings"

        if parameter['type'] == 'number':
            parameter['type'] = 'integer'
    return parameters


def parse_properties(properties, required, spec, ignore=None):
    """
    Given a definition's properties, parse out the parameters list for the action.

    We need to do some manipulation and explicitly ignore some elements.

    Input:
        properties(dict): properties for the definition
        required(list): list of required element names
        spec(dict): the overall spec object for linking outside elements
        ignore(list): optional list of elements to explicitly ignore
    """
    parameters = []
    for name, data in list(properties.items()):
        if data.get('readOnly', False):
            continue

        if ignore and name in ignore:
            continue

        parameter = {
            'name': name,
        }

        data_properties = data.get('properties', {})

        if data.get('$ref', False):
            # foreign key relationships should be integers
            props = spec['definitions'][data['$ref'].split('/')[-1]]['properties']
            parameter['type'] = props['id']['type']
            parameter['description'] = f"{props['id']['title']} of {name}"
        elif data_properties.get('label', False) and data_properties.get('value', False):
            # choice fields should be converted to integer types
            parameter['type'] = "integer"
            parameter['description'] = name.replace("_", " ").capitalize()
        else:
            # everything else is just copied over
            parameter['type'] = data['type']
            if data.get('title', False):
                parameter['description'] = data['title']
            else:
                parameter['description'] = name.replace("_", " ").capitalize()

        if name in required:
            parameter['required'] = True
        else:
            parameter['required'] = False

        parameters.append(parameter)

    return sanitize_parameters(parameters)


def run(spec):
    actions = {}
    deferred_detail_gets = []
    for path, verbs in list(spec['paths'].items()):
        path_parts = [x.replace("-", "_") for x in path.replace("/{id}", "").strip("/").split("/")]
        for verb, verb_data in verbs.items():
            if verb == "parameters":
                continue

            action_name = "{}.{}".format(verb, ".".join(path_parts))
            if "{id}" in path:
                path = path.replace("{id}", "{{ id }}")
            action = {
                'description': verb_data['description'].replace("\n", "") or "{} {}".format(
                    verb.upper(), path_parts[-1].replace("_", " ").title()
                ),
                'parameters': [],
                'endpoint_uri': path,
                'immutable': True,
                'verb': verb,
                'get_detail_route_eligible': True,
            }
            print(f"Processing {action_name}...")

            if verb_data['parameters'] and verb_data['parameters'][0].get('schema', False):
                ref_name = verb_data['parameters'][0]['schema']['$ref'].split('/')[-1]
                schema = spec['definitions'][ref_name]
                try:
                    required = ['id'] if verb == 'patch' else schema['required']
                except KeyError:
                    required = []
                action['parameters'] = parse_properties(schema['properties'], required, spec)

            if verb == 'get':
                if verb_data['operationId'].endswith('_list'):
                    action['parameters'] = sanitize_parameters(verb_data['parameters'])
                    actions[action_name] = action
                elif path.endswith("/{{ id }}/"):
                    # defer these until we have processed everything else to ensure the list
                    # endpoints are present for lookup
                    deferred_detail_gets.append(action_name)
                elif "{{ id }}" in path and not path.endswith("{{ id }}"):
                    action['parameters'].append({
                        'name': 'id',
                        'required': True,
                        'description': "ID of the object.",
                        'type': 'string'
                    })
                    action['get_detail_route_eligible'] = False
                    actions[action_name] = action

            if verb in ['delete', 'put', 'patch']:
                action['parameters'].append({
                    'name': 'id',
                    'required': True,
                    'description': "ID of the object to {}.".format(verb),
                    'type': 'string'
                })
                actions[action_name] = action

            if verb == 'post':
                if "{{ id }}" not in path:
                    actions[action_name] = action

            #
            # Begin special endpoint processing
            #
            if action_name == 'get.dcim.devices.napalm':
                action.update({'immutable': False})
                actions[action_name] = action

            #
            # End special endpoint handling
            #

    # process deferred detail get endpoints
    for detailed_get in deferred_detail_gets:
        list_action = actions.get(detailed_get)
        if list_action is None:
            print("Unable to find list action for deferred GET endpoint {}".format(detailed_get))

    # delete all current ".yaml" action files
    running_dir_name = os.path.dirname(__file__)
    actions_dir = os.path.join(running_dir_name, '../actions')
    current_actions_listing = os.listdir(actions_dir)
    for item in current_actions_listing:
        if item.endswith('.yaml'):
            os.remove(os.path.join(actions_dir, item))

    # render the new actions and write them to file
    with open('action-template.jinja2') as f:
        template = jinja2.Template(f.read(), autoescape=True)
    for name, action in list(actions.items()):
        template_vars = {
            'version': spec['info']['version'],
            'action_name': name,
            'parameters': action['parameters'],
            'description': action['description'],
            'endpoint_uri': action['endpoint_uri'],
            'immutable': action['immutable'],
            'verb': action['verb'],
            'get_detail_route_eligible': action['get_detail_route_eligible'],
        }
        rendered_template = template.render(**template_vars)
        f = open(os.path.join(actions_dir, "{}.yaml".format(name)), 'w')
        f.write(rendered_template)
        f.close()

    return len(actions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate action meta yaml files from a NetBox API Swagger spec.'
    )
    parser.add_argument(
        'host',
        type=str,
        help='NetBox instance to pull API spec from',
        default='demo.netbox.dev'
    )
    parser.add_argument(
        '--https',
        help='Use HTTPS (If using the default HTTPS port, you must also specify --port 443)',
        action='store_true',
    )
    parser.add_argument(
        '--port',
        type=int,
        help='Port NetBox is run on',
        default=8000,
    )
    parser.add_argument(
        '--skip-ssl',
        action='store_false',
        help='Skips SSL certificate verification',
        default=True
    )
    args = parser.parse_args()

    specification = get_spec(args.host, args.https, args.port, args.skip_ssl)
    total_actions = run(specification)
    print("Wrote {} actions to file.".format(total_actions))
    print("Done!")
