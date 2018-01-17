from xml.etree import ElementTree

def loads(filename, scale = 0.00002):
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    print(root.tag)
    nodes = []
    links = []
    for node_section in root.iter("nodes"):
        for node_class in node_section.iter("class"):
            for node_type in node_class.iter("type"):
                for node in node_type.iter("node"):
                    position = node.find("position")
                    velocity = node.find("velocity")
                    new_node = {}
                    new_node["position"] = [scale * int(position.attrib.get(i, 0)) for i in ["x", "y", "z"]]
                    new_node["velocity"] = [scale * int(velocity.attrib.get(i, 0)) for i in ["x", "y", "z"]]
                    new_node["radius"] = scale * int(node_type.attrib["radius"])
                    new_node["color"] = [float(node_class.attrib.get(color, 0.2)) for color in ["red", "green", "blue"]]
                    new_node["fixed"] = node_type.attrib.get("fixed", "false").lower() == "true"
                    nodes.append(new_node)


    for link_section in root.iter("links"):
        for link_class in link_section.iter("class"):
            for link_type in link_class.iter("type"):
                for link in link_type.iter("link"):
                    new_link = {}
                    new_link["nodes"] = [int(x) for x in link.attrib["nodes"].split()]
                    new_link["length"] = scale * int(link_type.attrib["length"])
                    new_link["radius"] = scale * int(link_type.attrib["radius"])
                    new_link["elasticity"] = int(link_type.attrib["elasticity"])
                    new_link["damping"] = int(link_type.attrib["damping"])
                    new_link["color"] = [float(link_class.attrib.get(color, 0.2)) for color in ["red", "green", "blue"]]
                    new_link["fixed"] = link_type.attrib.get("fixed", "false").lower() == "true"

                    links.append(new_link)

    return nodes, links