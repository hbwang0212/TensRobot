__author__ = 'aagogino'

import math

import ode

def dot(v1, v2):
    return sum([v1[i] * v2[i] for i in range(len(v1))])


def normalize(v):
    length = math.sqrt(dot(v, v))
    if length > 0:
        return [val / length for val in v]
    else:
        return [1] + v[1:]


def cross(a, b):
    c = [a[1] * b[2] - a[2] * b[1],
         a[2] * b[0] - a[0] * b[2],
         a[0] * b[1] - a[1] * b[0]]

    return c


def rotation_quat(u, v):
    w = cross(u, v)
    q = [1. + dot(u, v), w[0], w[1], w[2]]
    return normalize(q)

class Node:
    def __init__(self, world, space, name="", position=(0., 0., 0.), velocity=(0., 0., 0.), radius=0.5,
                 mass=1.0, color=(100., 0., 100.), fixed=False):

        radius *= 2
        self.name = name
        self.radius = radius
        self.mass = mass
        self.color = color

        self.joints = []

        self.body = ode.Body(world)
        M = ode.Mass()
        M.setSphereTotal(mass, radius)
        self.body.name = name
        self.body.shape = "sphere"
        self.body.radius = radius
        self.body.setMass(M)
        self.body.setPosition(position)
        self.body.setLinearVel(velocity)

        #self.geom = ode.GeomSphere(space, radius=self.body.radius)
        #self.geom = ode.GeomBox(space, lengths=(1, 1, 1))
        #self.geom.setBody(self.body)

        if fixed:
            joint = ode.FixedJoint(world)
            joint.attach(self.body, ode.environment)
            joint.setFixed()
            self.joints.append(joint)

    def add_force(self, force):
        self.body.addForce(force)

    def set_force(self, force):
        self.body.setForce(force)

    def get_position(self):
        return self.body.getPosition()

    def get_linear_vel(self):
        return self.body.getLinearVel()



class Link:
    def __init__(self, world, space, node1, node2, radius=0.1, mass=1.0, rest_length=1, elasticity=0, color=(100., 0., 100.), fixed=False):
        self.nodes = [node1, node2]
        self.radius = radius
        self.mass = mass
        self.rest_length = rest_length
        self.elasticity = elasticity
        self.color = color
        self.joints = []

        is_strut = elasticity == 0

        self.body = ode.Body(world)

        positions = [node.get_position() for node in self.nodes]
        center = [(positions[0][i] + positions[1][i])/2 for i in range(len(positions[0]))]
        lengths = [(positions[1][i] - positions[0][i]) for i in range(len(positions[0]))]
        length = math.sqrt(dot(lengths, lengths))

        self.update()

        print("lengths=", lengths)
        print("center=", center)


        if is_strut:
            geom_length = 0.9 * (length - (node1.radius + node2.radius))
            self.geom = ode.GeomBox(space, lengths=[radius, geom_length, radius])
            self.geom.setBody(self.body)

            for node in self.nodes:
                joint = ode.FixedJoint(world)
                joint.attach(self.body, node.body)
                joint.setFixed()
                self.joints.append(joint)

        if fixed:
            joint = ode.FixedJoint(world)
            joint.attach(self.body, ode.environment)
            joint.setFixed()
            self.joints.append(joint)

    def update(self):



        positions = [node.get_position() for node in self.nodes]
        center = [(positions[0][i] + positions[1][i])/2 for i in range(len(positions[0]))]
        lengths = [(positions[1][i] - positions[0][i]) for i in range(len(positions[0]))]
        length = math.sqrt(dot(lengths, lengths))

        box_dims = [self.radius, length, self.radius]
        M = ode.Mass()
        M.setBoxTotal(self.mass, box_dims[0], box_dims[1], box_dims[2])
        self.body.setMass(M)
        self.body.shape = "box"
        self.body.boxsize = box_dims
        self.body.setPosition(center)
        self.body.setQuaternion(rotation_quat([0, 1, 0], normalize(lengths)))


    def add_force(self, force):
            positions = [node.getPosition() for node in self.nodes]
            length = math.sqrt(dot(positions[0], positions[1]))
            lengths = [(positions[1][i] - positions[0][i]) for i in range(len(positions[0]))]

            force_dir = normalize(lengths)
            magnitude = 100.0 * length * length

            self.nodes[0].addForce([-force_dir[i] * magnitude for i in range(len(force_dir))])
            self.nodes[1].addForce([force_dir[i] * magnitude for i in range(len(force_dir))])

    def set_force(self, force):
        pass

class BasicSurface:
    def __init__(self, space):
        self.floor = ode.GeomPlane(space, (0, 1, 0), -.25)


class NTRTX:

    nodes = []
    links = []
    link_modifiers = []
    surfaces = []

    def __init__(self, gravity=-9.81):
        # Create a world object
        self.world = ode.World()
        self.space = ode.Space()
        self.contactgroup = ode.JointGroup()
        self.world.setGravity((0, gravity, 0))

        #self.world.setCFM(0.000001)
        self.world.setERP(.99)

    def create_node(self, name="",position=(0., 0., 0.),  velocity=(0., 0., 0.), radius=0.5,
                 mass=1.0, color=(100., 0., 100.), fixed=False):
        return Node(self.world, self.space, name, position, velocity, radius, mass, color, fixed)

    def create_link(self, node1, node2, radius=0.1, mass=1.0, rest_length=1, elasticity=0, color=(100., 0., 100.), fixed=False):
        return Link(self.world, self.space, node1, node2, radius, mass, rest_length, elasticity, color, fixed)


    def add_node(self, node):
        self.nodes.append(node)

    def add_link(self, link):
        self.links.append(link)

    def add_link_modifier(self, link_modifier):
        self.link_modifiers.append(link_modifier)

    def create_surface(self):
        return BasicSurface(self.space)

    def add_surface(self, surface):
        self.surfaces.append(surface)

    def init_sim(self):
        pass

    index = 0

    def step(self, t):
        if self.index >= 0:

            if self.index % 1 == 0:
                self.space.collide((self.world, self.contactgroup), self.near_callback)


            for node in self.nodes:
                pass
                #print("sim node vel=", node.body.getLinearVel())
            self.world.quickStep(t)
            #self.world.step(t)
            for node in self.nodes:
                pass
                #print("after sim node vel=", node.body.getLinearVel())
            self.contactgroup.empty()
        self.index += 1

    # Collision callback
    def near_callback(self, args, geom1, geom2):
        """Callback function for the collide() method.

        This function checks if the given geoms do collide and
        creates contact joints if they do.
        """

        # Check if the objects do collide
        contacts = ode.collide(geom1, geom2)

        # Create contact joints
        world, contactgroup = args
        for c in contacts:
            c.setBounce(0.2)
            c.setMu(5000)
            j = ode.ContactJoint(world, contactgroup, c)
            j.attach(geom1.getBody(), geom2.getBody())
