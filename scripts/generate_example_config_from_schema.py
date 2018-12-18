
import yaml
import sys

if __name__ == '__main__':

    with open(sys.argv[1], 'r') as f:
        config_schema = yaml.safe_load(f.read())

    example_config_dict = {}

    for key in config_schema.keys():
        current_type = config_schema[key]['type']
        if current_type == 'string':
            if 'url' in key:
                example_config_dict[key] = 'http://test.url'
            else:
                example_config_dict[key] = 'test_value'
        elif current_type == 'array':
            items = config_schema[key]['items']
            item_type = items['type']
            if item_type == 'string':
                if 'url' in key:
                    example_config_dict[key] = ['http://test.url']
                else:
                    example_config_dict[key] = ['test']
            elif item_type == 'object':
                item = {}
                for item_key in items['properties'].keys():
                    if 'url' in item_key:
                        item[item_key] = 'http://test.url'
                    else:
                        item[item_key] = 'test'
                example_config_dict[key] = [item]
            else:
                raise NotImplementedError("No handling implemented for type: {} for key: {}".format(item_type, key))
        elif current_type == 'integer':
            example_config_dict[key] = 0
        else:
            raise NotImplementedError("No handling implemented for type: {} for key: ".format(current_type, key))

    print(yaml.safe_dump(example_config_dict, default_flow_style=False))

