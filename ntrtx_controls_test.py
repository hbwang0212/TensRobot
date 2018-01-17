import ntrtx_visualizer
import ntrtx, spr, link_modifiers
import math, random


class SineTensSim:

    def __init__(self, gravity, params):
        sim =  ntrtx.NTRTX(gravity)
        nodes, links = spr.loads('t_sphere_6mod.spr', scale = 0.000005)
        sim_nodes = []
        sim_links = []
        sim_link_modifiers = []
        for i in range(len(nodes)):
            node = nodes[i]
            sim_node = sim.create_node(str(i), node["position"], node["velocity"], node["radius"],
                                       color=node["color"], mass=.005*1, fixed=node["fixed"])
            sim.add_node(sim_node)
            sim_nodes.append(sim_node)
        for i in range(len(links)):
            link = links[i]
            if link["elasticity"] > 200:
                link["elasticity"] = 0 # is rod
                link["mass"] = 0.035
            else:
                link["mass"] = 0.005
            sim_link = sim.create_link(sim_nodes[link["nodes"][0]], sim_nodes[link["nodes"][1]],
                                         radius=link["radius"], elasticity=link["elasticity"], rest_length=link["length"],
                                         color=link["color"],  mass=link["mass"], fixed=link["fixed"])
            sim_links.append(sim_link)
            sim.add_link(sim_link)
            if link["elasticity"] > 0:
                modifier = link_modifiers.String(sim_link)
                sim_link_modifiers.append(modifier)


        rand_ids = range(len(sim_link_modifiers))
        random.shuffle(rand_ids)
        for i in range(24):
            active_link_id = rand_ids[i]
            print("active_link_id=", active_link_id)
            #sim_link_modifiers.append(link_modifiers.SineString(sim_link_modifiers[active_link_id], 0.3, 1, 0.0, .5))
            ampl = 0.0 + 0.1 * (params[i] - 0.5)
            freq = .25 * 1.5 * params[i + 1]
            phase = 0.0 + 1.75 * params[i + 2]
            offset = 0.3 + 0.2 * params[i + 3]
            sim_link_modifiers[active_link_id] = link_modifiers.SineString(sim_link_modifiers[active_link_id], ampl, freq, phase, offset)


        sim.add_surface(sim.create_surface())

        self.sim = sim
        self.sim_link_modifiers = sim_link_modifiers
        self.nodes = sim_nodes
        self.links = sim_links

        self.initial_pos = self.get_position()


    def get_position(self):
        ave_pos = [0, 0, 0]
        for i in range(len(self.nodes)):
            for j in range(len(ave_pos)):
                ave_pos[j] += self.nodes[i].body.getPosition()[j]
        return ave_pos

    def get_delta_x(self):
        curr_pos = self.get_position()
        dist = math.sqrt(sum([(curr_pos[i] - self.initial_pos[i])**2 for i in range(3)]))
        return dist

    step_count = 0

    def sim_step(self):

        for link_modifier in self.sim_link_modifiers:
            link_modifier.modify_link(0.005)
        self.sim.step(.005)

        if self.step_count % 200 == 0:
            print("step_count=", self.step_count)
        self.step_count += 1
        #print("delta x=", self.get_delta_x())

    def start_vis(self):
        ntrtx_visualizer.ntrtx_visualizer(self.sim, self.sim_step, -0.28)

def sine_tens_sim(params):

    sim =  ntrtx.NTRTX(-9.8/1.0)


    nodes, links = spr.loads('t_sphere_6mod.spr', scale = 0.000005)
    sim_nodes = []
    sim_links = []
    sim_link_modifiers = []
    for node in nodes:
        sim_node = sim.create_node(node["position"], node["velocity"], node["radius"],
                                   color=node["color"], mass=.005*1, fixed=node["fixed"])
        sim.add_node(sim_node)
        sim_nodes.append(sim_node)
    for i in range(len(links)):
        link = links[i]
        if link["elasticity"] > 200:
            link["elasticity"] = 0 # is rod
            link["mass"] = 0.035
        else:
            link["mass"] = 0.005
        sim_link = sim.create_link(sim_nodes[link["nodes"][0]], sim_nodes[link["nodes"][1]],
                                     radius=link["radius"], elasticity=link["elasticity"], rest_length=link["length"],
                                     color=link["color"],  mass=link["mass"], fixed=link["fixed"])
        sim_links.append(sim_link)
        sim.add_link(sim_link)
        if link["elasticity"] > 0:
            modifier = link_modifiers.String(sim_link)
            sim_link_modifiers.append(modifier)


    rand_ids = range(len(sim_link_modifiers))
    random.shuffle(rand_ids)
    for i in range(24):
        active_link_id = rand_ids[i]
        print("active_link_id=", active_link_id)
        #sim_link_modifiers.append(link_modifiers.SineString(sim_link_modifiers[active_link_id], 0.3, 1, 0.0, .5))
        ampl = 0.0 + 0.1 * (params[i] - 0.5)
        freq = 0.5 + 0.1 * (params[i + 1] - 0.5)
        phase = 0.0 + 0.1 * (params[i + 2] - 0.5)
        offset = 0.4 + 0.1 * (params[i + 3] - 0.5)
        sim_link_modifiers[active_link_id] = link_modifiers.SineString(sim_link_modifiers[active_link_id], ampl, freq, phase, offset)


    sim.add_surface(sim.create_surface())


    def idle_callback():

        for link_modifier in sim_link_modifiers:
            link_modifier.modify_link(0.005)
        sim.step(.005)


    vis = ntrtx_visualizer.ntrtx_visualizer(sim, idle_callback, -0.28)




def test():
    import ntrtx, spr, link_modifiers
    import math, random
    sim =  ntrtx.NTRTX(-9.8/1.0)


    #nodes, links = spr.loads('spring_platform.spr', scale = 0.00001)
    nodes, links = spr.loads('t_sphere_6mod.spr', scale = 0.000005)
    #nodes, links = spr.loads('t_sphere_6payload.spr', scale = 0.000005)
    #nodes, links = spr.loads('t_sphere_32.spr', scale = 0.000005)
    sim_nodes = []
    sim_links = []
    sim_link_modifiers = []
    for node in nodes:
        sim_node = sim.create_node(node["position"], node["velocity"], node["radius"],
                                   color=node["color"], mass=.005*1, fixed=node["fixed"])
        sim.add_node(sim_node)
        sim_nodes.append(sim_node)
    for i in range(len(links)):
        link = links[i]
        if link["elasticity"] > 200:
            link["elasticity"] = 0 # is rod
            link["mass"] = 0.035
        else:
            link["mass"] = 0.005
        sim_link = sim.create_link(sim_nodes[link["nodes"][0]], sim_nodes[link["nodes"][1]],
                                     radius=link["radius"], elasticity=link["elasticity"], rest_length=link["length"],
                                     color=link["color"],  mass=link["mass"], fixed=link["fixed"])
        sim_links.append(sim_link)
        sim.add_link(sim_link)
        if link["elasticity"] > 0:
            modifier = link_modifiers.String(sim_link)
            sim_link_modifiers.append(modifier)



    for i in range(3):
        active_link_id = random.randrange(20)
        print("active_link_id=", active_link_id)
        sim_link_modifiers.append(link_modifiers.SineString(sim_link_modifiers[active_link_id], 0.3, 1, 0.0, .5))

    # sim_link_modifiers.append(link_modifiers.SineString(sim_link_modifiers[20], 0.3, 1, 0.0, .5))
    # sim_link_modifiers[20].log = True
    #
    # sim_link_modifiers.append(link_modifiers.SineString(sim_link_modifiers[4], 0.3, 1, 0.0, .5))
    # sim_link_modifiers.append(link_modifiers.SineString(sim_link_modifiers[12], 0.3, 1, 0.0, .5))

    sine_modifiers = {sim_link_modifiers[-1], sim_link_modifiers[-2], sim_link_modifiers[-3]}
    #sine_modifiers = {sim_link_modifiers[-1], sim_link_modifiers[-2]}

    sim.add_surface(sim.create_surface())
    sim_time = [0]

    def get_ave_pos():
        ave_pos = [0, 0, 0]
        for i in range(len(sim_nodes)):
            for j in range(len(ave_pos)):
                ave_pos[j] += sim_nodes[i].body.getPosition()[j]
        ave_pos = [x / len(sim_nodes) for x in ave_pos]
        return ave_pos

    def idle_callback():

        for link_modifier in sim_link_modifiers:
            if link_modifier in sine_modifiers:
                link_modifier.modify_link(0.005)
            else:
                link_modifier.modify_link()
        sim.step(.005)




        #sim_time[0] += 0.005
        #print("torque=", [node.body.getTorque() for node in sim_links[25].nodes])
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
    initial_pos = get_ave_pos()
    max_dist = 0.0
    for i in range(500):
        idle_callback()
        pos = get_ave_pos()
        dist = math.sqrt(sum([(pos[i] - initial_pos[i])**2 for i in range(3)]))
        print("ave_pos=", list(get_ave_pos()))
        print("dist=", dist)
        if dist > max_dist:
            max_dist = dist
    return max_dist

max_dists = []
params = []
for j in range(10):
    param = [0.5 + random.random() / 2.0 for i in range(24 * 4)]
    #param = [0.662223493428432, 0.7813838625323505, 0.9330389102632499, 0.7684422463807685, 0.8510238212119625, 0.619875907881509, 0.5210881311279618, 0.6977229564579455, 0.6472245400200847, 0.9478032108739023, 0.7356781375636705, 0.5443712961902234, 0.5221214588536188, 0.6649847057719231, 0.5370984833122681, 0.6270085520360638, 0.7482306962257406, 0.5894208193373318, 0.9302631684574554, 0.7568952938774911, 0.5300047514625433, 0.6879507985374731, 0.5783698230598622, 0.7527585337006757, 0.9087974184892224, 0.7403373263487045, 0.7922431640780787, 0.705748284852659, 0.5679020702305606, 0.6311392170688153, 0.5083905297152799, 0.9081060418413416, 0.832815140193632, 0.9649818202330797, 0.6345300110807544, 0.9528212980112722, 0.6301849843342363, 0.8232234701832417, 0.8497331744375645, 0.9342616660194716, 0.6650857538219128, 0.7760109912001123, 0.5504085637056836, 0.7279175017150281, 0.6119279970703352, 0.565093312208702, 0.533694349742379, 0.766103974330999, 0.584267126421977, 0.9521385345937323, 0.9345923377604597, 0.7891971549473975, 0.5652095602681673, 0.6712518180336393, 0.781898516247169, 0.8821898229487378, 0.9820591606334228, 0.5293718883939278, 0.6245276022764308, 0.5128781608085609, 0.5373585605909945, 0.6016281802590554, 0.649811072058946, 0.9376075074743466, 0.8485458759257885, 0.5442838006656618, 0.940054712232051, 0.6711100692291194, 0.7675792243052162, 0.8346077397181046, 0.6822281063431879, 0.7322384548024059, 0.6386899564178041, 0.7814855181379305, 0.5426945653328028, 0.8975634176686005, 0.542157074208635, 0.6646613532482344, 0.6761340044008601, 0.854401916616327, 0.9576465676629236, 0.8406583633614837, 0.6915239669617237, 0.7228902177056928, 0.6410355549969069, 0.8499679225933265, 0.9147215427726691, 0.7009025010462617, 0.6454497154543568, 0.9323667671119484, 0.535742422014502, 0.6020412537469251, 0.5015339955129243, 0.7817687461890235, 0.6981972161429846, 0.527936376094744]
    #param = [0.8785941257299421, 0.5729163943130581, 0.8262062350699801, 0.9084161432539011, 0.6349535116026115, 0.803825365564003, 0.6780331167324568, 0.6896259676968594, 0.97764571620257, 0.9693610078726818, 0.734068823837, 0.6243503032986775, 0.6396587550537722, 0.8252791501088412, 0.6885126532956182, 0.528564292745583, 0.8961721702213624, 0.611480861485348, 0.5613635265862245, 0.6922756299527112, 0.6474478056146364, 0.46278858671567885, 0.80287979719229, 0.827635669772365, 0.9910643043062318, 0.6089650489626833, 0.6222182904744303, 0.8250902825335504, 0.8233541410555574, 0.7073170354963658, 0.9241352736217642, 0.597992866461782, 0.7356226547713263, 0.648379576749832, 0.6590979471774283, 0.6993344727975765, 0.640812274182262, 0.760816960586574, 0.7556033708273111, 0.7014944619931067, 0.8768241544737921, 0.7827606732166412, 0.948511848085869, 0.5488655293906309, 0.823319746329947, 0.9651935857343054, 0.8487331682315736, 0.9231302321112016, 0.7195076438027335, 0.8116309194098182, 0.7219422379586843, 0.5373753264921802, 0.8593712595162911, 0.6786773120690097, 0.8092893764553434, 0.8475919875818819, 0.8661103367357389, 0.5306790963226156, 0.8146939653691117, 0.46254136867244744, 0.8534306460817443, 0.9201054188365244, 0.5954448386254161, 0.5551908261126078, 0.8111028404032439, 0.7812738081864066, 0.4943763411952, 1.0, 0.78485118472316, 0.7875973864942939, 0.8945464330298357, 0.9429371567497595, 0.8540665046563497, 1.0, 0.9377914514076681, 0.6203744265206891, 0.8420889965659735, 0.604023412767239, 0.6093511965207925, 0.760494765041904, 0.6447012982637021, 0.9478371422382673, 0.6365246810983951, 0.7601991185786656, 0.5979090982681642, 0.8755509068578996, 0.576529336023542, 0.9465050177776982, 0.6440580713004854, 0.8553501094338107, 0.5024847158689506, 0.545216258401965, 0.5686114893583107, 0.752063534539, 0.692356424882362, 0.6349467143031269]
    param = [0.8439564735149954, 0.5883860812357817, 0.5185284925515526, 0.5923471840068564, 0.8941152802994558, 0.7531687339647243, 0.8606916537355492, 0.8962345309470796, 0.6501830582346159, 0.9942244341462897, 0.8937916461043804, 0.8266090800282366, 0.4939331589670679, 0.7165709339009839, 0.5784386705143383, 0.9285837383970171, 0.799389511694155, 0.6557457520268901, 0.9211703007387463, 0.7839759177436232, 0.73074171379367, 0.608646570086163, 0.9424261413850228, 0.9528828586653785, 0.8909494786780342, 0.7666811741392083, 0.7934507741890314, 0.7555231406768336, 0.6320764094145681, 0.6374057062627168, 0.6916859077932038, 0.5829752924529249, 0.8568155747776366, 0.5723654738837746, 0.8001595105488141, 0.6071916733745453, 0.9742743813242953, 0.8815194666408126, 0.8146109521061649, 0.925519095137486, 0.6096573478486049, 0.9073588171856178, 0.6173550003974636, 0.6186184950570184, 0.7353115588792843, 0.9425691121286004, 0.7973775593452224, 0.5125000241715756, 0.707565067101714, 0.7919628008283508, 0.6083741898862682, 0.8574109873693985, 0.4969627946999456, 0.6413711874033834, 0.6307818999150685, 0.7323257549524372, 0.8510700125574976, 0.6753337579353861, 0.8164774111542352, 0.645498392031659, 0.6069502654072252, 0.5345517925734535, 0.8255916446233257, 0.9243764121228039, 0.8808507810984165, 0.7325607381979609, 0.9096483487128798, 0.947722261517991, 0.5374306284541679, 0.6172886928925511, 0.8536329868038026, 0.8078719700440757, 0.8245136855846004, 0.9023406206567051, 0.6564144731804858, 0.5217413893568199, 0.8687451296702547, 0.9206427420013061, 0.7777683719112506, 0.77655827605652, 0.6106409473273048, 0.6652776123238394, 0.7295968755523201, 0.9115448777442694, 0.5696851205266956, 0.7226563834831735, 0.9475594512009818, 0.7549331076860787, 0.9960318280453815, 0.5619144338881373, 0.7991905370201468, 0.9224709917509575, 0.6653937862225847, 0.7542374091414488, 0.8956954203452222, 0.5539167490353556]
    for i in range(len(param)):
        param[i] += (random.random() - 0.5) * .1
        param[i] = max(0.0, param[i])
        param[i] = min(1.0, param[i])

    #param = [0.0] * (24 * 4)
    sine_sim = SineTensSim(-9.8 / 6.0, param)
    dist = []
    sine_sim.start_vis()
    for i in range(12000):
        sine_sim.sim_step()
        dist.append(sine_sim.get_delta_x())

    max_dists.append(max(dist))
    params.append(param)


max_index = max_dists.index(max(max_dists))
print(max_dists[max_index])
print(max_dists)
print(params[max_index])
#sine_tens_sim([0.5 + random.random() / 2.0 for i in range(24 * 4)])
# max_dist = 0.0
# for i in range(10):
#     dist = test()
#     if dist > max_dist:
#         max_dist = dist
# print(max_dist)