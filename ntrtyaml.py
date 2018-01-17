__author__ = 'aagogino'


import yaml


def loads(filename, scale = 1.0):
    yaml_struct = yaml.load(file(filename, "r"))

    nodes = []
    links = []

    #print(x)
    nodes_locs = yaml_struct["nodes"]
    pair_groups = yaml_struct["pair_groups"]
    builders = yaml_struct["builders"]

    for node_loc in nodes_locs:
        position = node_loc

    print(builders)

loads("three_bar.yaml")