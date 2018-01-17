__author__ = 'aagogino'

# !/usr/bin/env python

# http://pyode.sourceforge.net/tutorials/tutorial3.html

# pyODE example 3: Collision detection

# Originally by Matthias Baas.
# Updated by Pierre Gay to work without pygame or cgkit.

import sys, os, random, time
from xml.etree import ElementTree
from math import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import ode


class Node:
    velocity = (0., 0., 0.)
    position = (0., 0., 0.)


class Link:
    nodes = []
    length = "0"
    radius = "0"
    elasticity = "0"
    damping = "0"


def load_spr():
    tree = ElementTree.parse('t_sphere_6.spr')
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
                    new_node = Node()
                    new_node.position = [int(position.attrib.get(i, 0)) for i in ["x", "y", "z"]]
                    new_node.velocity = [int(velocity.attrib.get(i, 0)) for i in ["x", "y", "z"]]
                    new_node.radius = node_type.attrib["radius"]
                    nodes.append(new_node)
                    print(position.attrib)
                    print(list(new_node.position))

    for link_section in root.iter("links"):
        for link_class in link_section.iter("class"):
            for link_type in link_class.iter("type"):
                for link in link_type.iter("link"):
                    new_link = Link()
                    new_link.nodes = [int(x) for x in link.attrib["nodes"].split()]
                    new_link.length = int(link_type.attrib["length"])
                    new_link.radius = int(link_type.attrib["radius"])
                    new_link.elasticity = int(link_type.attrib["elasticity"])
                    new_link.damping = int(link_type.attrib["damping"])
                    links.append(new_link)
                    print(new_link.elasticity)

    return nodes, links


# prepare_GL
def prepare_GL():
    """Prepare drawing.
    """

    # Viewport
    glViewport(0, 0, 640, 480)

    # Initialize
    glClearColor(0.8, 0.8, 0.9, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_FLAT)

    # Projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.3333, 0.2, 20)

    # Initialize ModelView matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Light source
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 1, 0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])
    glEnable(GL_LIGHT0)

    # View transformation
    gluLookAt(2.4 * 2, 3.6 * 2, 4.8 * 2, 0.4, 0.5, 0, 0, 1, 0)


# draw_body
def draw_body(body):
    """Draw an ODE body.
    """

    #	  x, y, z = body.getPosition()
    #	  u, v, w = body.getLinearVel()
    #	  print "%1.2fsec: pos=(%6.3f, %6.3f, %6.3f)  vel=(%6.3f, %6.3f, %6.3f)" % \
    #		  (0, x, y, z, u, v, w)

    x, y, z = body.getPosition()
    R = body.getRotation()
    rot = [R[0], R[3], R[6], 0.,
           R[1], R[4], R[7], 0.,
           R[2], R[5], R[8], 0.,
           x, y, z, 1.0]
    glPushMatrix()
    glMultMatrixd(rot)
    if body.shape == "box":
        sx, sy, sz = body.boxsize
        glScalef(sx, sy, sz)
        glutSolidCube(1)
    #glutSolidSphere(0.5, 10, 10)
    elif body.shape == "sphere":
        r = body.radius

        glScalef(r, r, r)
        glutSolidSphere(1, 10, 10)
    #glutSolidSphere(0.5, 10, 10)
    glPopMatrix()


# create_box
def create_box(world, space, density, lx, ly, lz):
    """Create a box body and its corresponding geom."""

    # Create body
    body = ode.Body(world)
    M = ode.Mass()
    M.setBox(density, lx, ly, lz)
    body.setMass(M)

    # Set parameters for drawing the body
    body.shape = "box"
    body.boxsize = (lx, ly, lz)

    # Create a box geom for collision detection
    geom = ode.GeomBox(space, lengths=body.boxsize)
    geom.setBody(body)

    return body, geom


# create_sphere
def create_sphere(world, space, density, radius):
    """Create a box body and its corresponding geom."""

    # Create body
    body = ode.Body(world)
    M = ode.Mass()
    M.setSphereTotal(density, radius)
    body.setMass(M)

    # Set parameters for drawing the body
    body.shape = "sphere"
    body.radius = radius


    # Create a box geom for collision detection
    geom = ode.GeomSphere(space, radius=body.radius)
    geom.setBody(body)

    return body, geom


nodes = []
node_bodies = []
link_bodies = []
links = []


def dot(v1, v2):
    return sum([v1[i] * v2[i] for i in range(len(v1))])


def normalize(v):
    length = sqrt(dot(v, v))
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


def create_tensegrity():
    global nodes, links, node_bodies
    nodes, links = load_spr()

    for node in nodes:
        endcap, geom = create_sphere(world, space, 10, .2)
        endcap.setPosition([val / 50000.0 for val in node.position])
        node_bodies.append(endcap)
        bodies.append(endcap)

    print("link length=", len(links))
    for link in links:
        is_strut = link.elasticity > 200
        if link.elasticity > 100:
            end_points = [nodes[node_id].position for node_id in link.nodes]
            dx = end_points[0][0] - end_points[1][0]
            dy = end_points[0][1] - end_points[1][1]
            dz = end_points[0][2] - end_points[1][2]
            length = sqrt(dx * dx + dy * dy + dz * dz)
            if is_strut:
                bar, geom = create_box(world, space, 1, .2, length / 50000.0, .2)
            else:
                bar, geom = create_box(world, space, 1, .05, length / 50000.0, .05)
            center = [(end_points[0][i] + end_points[1][i]) / 100000.0 for i in range(3)]
            bar.setPosition(center)
            c1 = sqrt(dx * dx + dy * dy);
            s1 = dz;
            c2 = dx / c1 if c1 != 0 else 1.0
            s2 = dy / c1 if c1 != 0 else 0.0

            quat = rotation_quat([0, 1, 0], normalize([dx, dy, dz]))
            bar.setQuaternion(quat)
            bodies.append(bar)
            link_bodies.append(bar)

            if is_strut:
                joint = ode.FixedJoint(world)
                joint.attach(bar, node_bodies[link.nodes[0]])
                joint.setFixed()
                joints.append(joint)

                joint = ode.FixedJoint(world)
                joint.attach(bar, node_bodies[link.nodes[1]])
                joint.setFixed()
                joints.append(joint)

                geoms.append(geom)



            #bodies[0].setForce((0, 100, 100))


# 	joint = ode.FixedJoint(world)
# 	joint.attach(bodies[0], ode.environment)
# 	joint.setFixed()
# 	joints.append(joint)

def set_forces(nodes):
    #print("len=", len(links))
    #for link in links:
    for inc in range(len(links)):
        link = links[inc]
        is_string = link.elasticity < 200
        if is_string:
            end_points = [node_bodies[node_id].getPosition() for node_id in link.nodes]
            dx = end_points[0][0] - end_points[1][0]
            dy = end_points[0][1] - end_points[1][1]
            dz = end_points[0][2] - end_points[1][2]
            #print("link.nodes", link.nodes)
            #scale = 50000.0 / sqrt(dx*dx + dy*dy + dz*dz)
            scale = .5

            force_dir = normalize((dx, dy, dz))
            magnitude = 100.0 * (dot((dx, dy, dz), (dx, dy, dz)))

            node_bodies[link.nodes[0]].addForce([-force_dir[i] * magnitude for i in range(len(force_dir))])
            node_bodies[link.nodes[1]].addForce([force_dir[i] * magnitude for i in range(len(force_dir))])

            center = [(end_points[0][i] + end_points[1][i]) / 2 for i in range(3)]
            #if inc == 1:
            #	print("center=", center)
            link_bodies[inc].setPosition(center)
            link_bodies[inc].setLinearVel((0, 0, 0))
            quat = rotation_quat([0, 1, 0], normalize([dx, dy, dz]))
            link_bodies[inc].setQuaternion(quat)


# def create_example1():
# 	SPHERE_RADIUS = 0.25
# 	SPHERE_MASS = 1.0
# 	SPHERE_START_POS = (1, 2.5, 0)
# 	JOINT1_ANCHOR = (0, 2.5, 0)
# 	BAR1_POS= (0.5, 2.5, 0)
#
# 	# Create a spherical body inside the world
# 	body = ode.Body(world)
#
# 	mass = ode.Mass()
# 	#mass.setSphereTotal(SPHERE_MASS, SPHERE_RADIUS)
# 	mass.setBoxTotal(SPHERE_MASS, SPHERE_RADIUS, SPHERE_RADIUS*2, SPHERE_RADIUS)
# 	body.setMass(mass)
# 	body.shape = "box"
# 	body.radius = SPHERE_RADIUS
# 	body.boxsize = (.2, 1, .2)
# 	body.setPosition((0, 2.0, 0))
# 	theta = -pi/4
# 	ct = cos (theta)
# 	st = sin (theta)
# 	#body.setRotation([ct, 0., -st, 0., 1., 0., st, 0., ct])
# 	#body.setRotation([ct, st, 0., -st, ct, 0., 0., 0., 1.])
#
#
#  	pivot_sphere, geom = create_sphere(world, space, SPHERE_MASS, SPHERE_RADIUS)
#  	pivot_sphere.setPosition((0, 1.5, 0))
#  	#pivot_sphere.setForce((1, 0, 0))
# # 	#pivot_sphere.disable()
#  	bodies.append(pivot_sphere)
#
# 	bar_1, geom = create_box(world, space, SPHERE_MASS, 1, .2, .2)
# 	bar_1.setPosition(BAR1_POS)
# 	#bar_1.setRotation([ct, 0., -st, 0., 1., 0., st, 0., ct])
# 	bar_1.setRotation([2, 1, 0, 0., 0., 0., 0., 0., 0.])
# 	bodies.append(bar_1)
# 	j3 = ode.FixedJoint(world)
# 	j3.attach(bar_1, ode.environment)
# 	j3.setFixed()
# 	joints.append(j3)
#
# 	j2 = ode.FixedJoint(world)
# 	j2.attach(pivot_sphere, body)
# 	j2.setFixed()
# 	joints.append(j2)
#
# 	pivot_sphere.setForce((10, 0, 0))
#
# # 	j2 = ode.BallJoint(world)
# # 	j2.attach(pivot_sphere, ode.environment)
# # 	j2.setAnchor(JOINT1_ANCHOR)
# # 	joints.append(j2)
#
# 	#body.addForce(SPHERE_FORCE)
# 	j1 = ode.BallJoint(world)
# 	j1.attach(body, bar_1)
# 	j1.setParam(ode.ParamStopCFM, 50)
# 	j1.setParam(ode.ParamCFM, 50)
# 	j1.setParam(ode.ParamStopERP, .1)
# 	j1.setAnchor(JOINT1_ANCHOR)
#
#
# 	jtest = ode.HingeJoint(world)
# 	jtest.setParam(ode.ParamCFM, .9)
# 	print(j1.getParam(ode.ParamStopCFM))
#
# 	#j1.attach(body, ode.environment)
#
#
#
# 	bodies.append(body)
# 	joints.append(j1)


# Collision callback
def near_callback(args, geom1, geom2):
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


######################################################################

# Initialize Glut
glutInit([])

# Open a window
glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)

x = 0
y = 0
width = 640
height = 480
glutInitWindowPosition(x, y);
glutInitWindowSize(width, height);
glutCreateWindow("testode")

# Create a world object
world = ode.World()
space = ode.Space()
world.setGravity((0, -9.81, 0))

#world.setGravity( (0,-1,0) )
#world.setCFM(1)
world.setERP(.5)

# Create a plane geom which prevent the objects from falling forever
floor = ode.GeomPlane(space, (0, 1, 0), -1)

contactgroup = ode.JointGroup()

# A list with ODE bodies
bodies = []

# A list with ODE joints
joints = []

# The geoms for each of the bodies
geoms = []


# Some variables used inside the simulation loop
fps = 50
dt = 1.0 / fps
running = True



# keyboard callback
def _keyfunc(c, x, y):
    sys.exit(0)


glutKeyboardFunc(_keyfunc)

# draw callback
def _drawfunc():
    # Draw the scene
    prepare_GL()
    for b in bodies:
        draw_body(b)

    glutSwapBuffers()


glutDisplayFunc(_drawfunc)


def _idlefunc_sim():
    glutPostRedisplay()

    # Simulate
    n = 1

    space.collide((world, contactgroup), near_callback)
    #for i in range(n):

    #for body in bodies:
    #body.addForce([0, 1, 0])
    set_forces(nodes)
    # Simulation step
    world.step(0.04)

    contactgroup.empty()


create_tensegrity()
glutIdleFunc(_idlefunc_sim)

glutMainLoop()
load_spr()

