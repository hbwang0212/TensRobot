import ntrtx_visualizer

def test():
    import ntrtx, spr, link_modifiers
    sim =  ntrtx.NTRTX(-9.8/6)

    #nodes, links = spr.loads('spring_platform.spr', scale = 0.00001)
    #nodes, links = spr.loads('t_sphere_6mod.spr', scale = 0.000005)
    nodes, links = spr.loads('t_sphere_6payload.spr', scale = 0.000005)
    #nodes, links = spr.loads('t_sphere_32.spr', scale = 0.00001)
    sim_nodes = []
    sim_links = []
    sim_link_modifiers = []
    for node in nodes:
        sim_node = sim.create_node(node["position"], node["velocity"], node["radius"],
                                   color=node["color"], mass=.005, fixed=node["fixed"])
        sim.add_node(sim_node)
        sim_nodes.append(sim_node)
    for i in range(len(links)):
        link = links[i]
        if link["elasticity"] > 200:
            link["elasticity"] = 0 # is rod
            link["mass"] = 0.035
        else:
            link["mass"] = 0.00005
        sim_link = sim.create_link(sim_nodes[link["nodes"][0]], sim_nodes[link["nodes"][1]],
                                     radius=link["radius"], elasticity=link["elasticity"], rest_length=link["length"],
                                     color=link["color"],  mass=link["mass"], fixed=link["fixed"])
        sim_links.append(sim_link)
        sim.add_link(sim_link)
        if link["elasticity"] > 0:
            modifier = link_modifiers.String(sim_link)
            #sim_link_modifiers.append(link_modifiers.SurfaceString(modifier))
            sim_link_modifiers.append(modifier)
            #sim.add_link_modifier(link_modifiers.SurfaceString(modifier))
            # if i == 23:
            #     sim.add_link_modifier(link_modifiers.SineString(modifier))
            # else:
            #     sim.add_link_modifier(modifier)
        #
        # if link["nodes"][0] == 0:
        #     motor_link = modifier
        #     modifier.set_string_force(100.0)

    sim_link_modifiers.append(link_modifiers.RocketRod(sim_links[42]))
    sim_link_modifiers[24].log = True
    sim.add_surface(sim.create_surface())
    # for i in range(10):
    #     sim.step(.04)

    motor_id = 21
    sim_links[motor_id].rest_length_delta = 0.01
    def idle_callback(vis):
        vis.origin = sim_nodes[10].body.getPosition()
        for link_modifier in sim_link_modifiers:
            link_modifier.modify_link()
        #sim_nodes[19].add_force((0, 1.5, 0))
        # pos1 = sim_nodes[12].body.getPosition()
        # pos2 = sim_nodes[19].body.getPosition()
        # dpos = [19 * (pos2[i] - pos1[i]) for i in range(len(pos1))]
        # sim_nodes[19].add_force(dpos)
        # print(dpos)
        pass
        # sim_links[motor_id].rest_length += sim_links[motor_id].rest_length_delta
        # if sim_links[motor_id].rest_length < .05:
        #     sim_links[motor_id].rest_length_delta = 0.005
        # if sim_links[motor_id].rest_length > .5:
        #     sim_links[motor_id].rest_length_delta = -0.005



        #print("sim_links[1].rest_length", sim_links[23].rest_length)
        #motor_link.set_string_force(50.0)

    vis = ntrtx_visualizer.ntrtx_visualizer(sim, idle_callback, -0.28)

test()