import argparse
import datetime
import jinja2
import json
import os
import urllib2


def get_spec(host, https, port):
    protocol = 'https://' if https else 'http://'
    url = "{}{}:{}/api/swagger.json".format(protocol, host, port)
    request = urllib2.Request(url)
    print("Getting API spec from NetBox instance...")
    try:
        response = urllib2.urlopen(request)
    except Exception:
        print("Failed to get the API spec!")
    return json.loads(response.read())


def sanitize_parameters(parameters):
    for parameter in parameters:
        if parameter['name'].endswith('_id'):
            parameter['type'] = "integer"
        elif parameter['name'] == 'id__in':
            parameter['type'] = "array"
            parameter['description'] = "Array of IDs"
        elif parameter['name'] == 'tags':
            parameter['type'] = "array"
            parameter['description'] = "Array of tag strings"
    return parameters


def parse_properties(properties, required, spec, ignore=None):
    """
    Given a definition's properties, parse out the parameters list for the action.

    We need to do some manipulation and explicitly ignore some elements.

    Input:
        properties(dict): properties for the definition
        required(list): list of required element names
        spec(dict): the overall spec object for linking outsite elements
        ignore(list): optional list of elements to explicitly ignore
    """
    parameters = []
    for name, data in properties.items():
        if data.get('readOnly', False):
            continue

        if ignore and name in ignore:
            continue

        parameter = {
            'name': name,
        }

        if data.get('$ref', False):
            parameter['type'] = "integer"
            parameter['description'] = spec['definitions'][data['$ref'].split('/')[-1]]['title']
        else:
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
    for path, verbs in spec['paths'].items():
        path_parts = [x.replace("-", "_") for x in path.replace("/{id}", "").strip("/").split("/")]
        for verb, verb_data in verbs.items():
            if verb == 'parameters':
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
                'verb': verb,
                'get_detail_route_eligible': True,
            }

            if verb_data['parameters'] and verb_data['parameters'][0].get('schema', False):
                ref_name = verb_data['parameters'][0]['schema']['$ref'].split('/')[-1]
                schema = spec['definitions'][ref_name]
                action['parameters'] = parse_properties(
                    schema['properties'], schema['required'], spec
                )

            #
            # Begin special endpoint processing
            #

            if verb == 'post' and action_name == 'post.ipam.prefixes.available_ips':
                # the spec defines the schema ref as Refix when it should really be IPAddress with
                # all parameters optional (since prefix and address are handled by the route)
                schema = spec['definitions']['IPAddress']
                action['parameters'] = parse_properties(
                    schema['properties'], schema['required'], spec, ['address']
                )
                action['parameters'].append({
                    'name': 'id',
                    'required': True,
                    'description': "ID of the Prefix.",
                    'type': 'integer'
                })
                action['get_detail_route_eligible'] = False
                action['description'] = "Create the next available IP Address in a given Prefix."
                actions[action_name] = action

            elif verb == 'post' and action_name == 'post.ipam.prefixes.available_prefixes':
                # the spec does not account for the required `prefix_length` field
                # also prefix is already accounted for in the route
                schema = spec['definitions']['Prefix']
                action['parameters'] = parse_properties(
                    schema['properties'], schema['required'], spec, ['prefix']
                )
                action['parameters'].append({
                    'name': 'id',
                    'required': True,
                    'description': "ID of the Prefix.",
                    'type': 'integer'
                })
                action['parameters'].append({
                    'name': 'prefix_length',
                    'required': True,
                    'description': "Prefix CIDR length to create.",
                    'type': 'integer'
                })
                action['get_detail_route_eligible'] = False
                action['description'] = "Create the next available Prefix in a given Prefix."
                actions[action_name] = action

            elif verb == 'get' and action_name == 'get.secrets.generate_rsa_key_pair':
                # description is not safe
                action['description'] = 'This endpoint can be used to generate a new RSA key pair.'
                actions[action_name] = action

            #
            # End special endpoint handling
            #

            elif verb == 'get' and verb_data['operationId'].endswith('_list'):
                action['parameters'] = sanitize_parameters(verb_data['parameters'])
                actions[action_name] = action

            elif verb == 'get' and path.endswith("/{{ id }}/"):
                # defer these until we have processed everything else to ensure the list
                # endoints are present for lookup
                deferred_detail_gets.append(action_name)

            elif verb == 'get' and "{{ id }}" in path and not path.endswith("{{ id }}"):
                action['parameters'].append({
                    'name': 'id',
                    'required': True,
                    'description': "ID of the object.",
                    'type': 'integer'
                })
                action['get_detail_route_eligible'] = False
                actions[action_name] = action

            elif verb in ['delete', 'put', 'patch']:
                action['parameters'].append({
                    'name': 'id',
                    'required': True,
                    'description': "ID of the object to {}.".format(verb),
                    'type': 'integer'
                })
                actions[action_name] = action

            elif verb == 'post' and "{{ id }}" not in path:
                actions[action_name] = action

            else:
                print("Unable to process endpoint {}, no defined logic".format(action_name))

    # process defered detail get endpoints
    for detailed_get in deferred_detail_gets:
        list_action = actions.get(detailed_get)
        if list_action is not None:
            list_action['parameters'].append({
                'name': 'id',
                'required': False,
                'description': 'If provided, will convert to using the detail route. '
                               'I.e., <endpoint_uri>/<id>/, '
                               'meaning a max of one entity will be returned and all '
                               'other entity query parameters will be ignored.',
                'type': 'integer'
            })
        else:
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
        template = jinja2.Template(f.read())
    for name, action in actions.items():
        template_vars = {
            'generation_date': datetime.datetime.now(),
            'version': spec['info']['version'],
            'action_name': name,
            'parameters': action['parameters'],
            'description': action['description'],
            'endpoint_uri': action['endpoint_uri'],
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
    args = parser.parse_args()

    spec = get_spec(args.host, args.https, args.port)
    total_actions = run(spec)
    print("Wrote {} actions to file.".format(total_actions))
    print("Done!")
