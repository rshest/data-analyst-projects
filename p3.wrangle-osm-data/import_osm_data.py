import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

OSM_PATH = "example.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

DEFAULT_TAG_TYPE = 'regular'

def gather_attribs(el, attr_schema):
    res = {}
    for k, v in attr_schema.items():
        if k in el.attrib:
            val = el.attrib[k]
            if 'coerce' in v:
                res[k] = (v['coerce'])(val)
            else:
                res[k] = val
    return res


def gather_tags(el, parent_attr):
    parent_id = parent_attr['id']
    for tag in el.iter("tag"):
        if 'k' not in tag.attrib or 'v' not in tag.attrib:
            continue
        k = tag.attrib['k']
        if PROBLEMCHARS.search(k) is not None:
            continue
        parts = k.split(':', 1)
        if len(parts) > 1:
            tag_type = parts[0]
            tag_key = parts[1]
        else:
            tag_type = DEFAULT_TAG_TYPE
            tag_key = k
        yield {'id': parent_id, 
               'key': tag_key, 
               'type': tag_type, 
               'value': tag.attrib['v']}


def gather_way_nodes(el, parent_attr):
    parent_id = parent_attr['id']
    position = 0
    for tag in el.iter('nd'):
        if 'ref' not in tag.attrib:
            continue
        try:
            yield {'id': parent_id, 
                   'node_id': int(tag.attrib['ref']), 
                   'position': position}
            position += 1
        except ValueError:
            # skip node with invalid reference
            pass
            
def shape_element(element, 
                  node_attr_fields=NODE_FIELDS, 
                  way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, 
                  default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    
    if element.tag == 'node':
        node_attribs = gather_attribs(element, SCHEMA['node']['schema'])
        tags = list(gather_tags(element, node_attribs))
        return {'node': node_attribs, 
                'node_tags': tags}
    
    elif element.tag == 'way':
        way_attribs = gather_attribs(element, SCHEMA['way']['schema'])
        way_nodes = list(gather_way_nodes(element, way_attribs))
        tags = list(gather_tags(element, way_attribs))
        return {'way': way_attribs, 
                'way_nodes': way_nodes, 
                'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(iter(validator.errors.items()))
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: v for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


process_map(DATA_PATH, validate=True)