import math

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

def matrix_vector_mult(m, v, transpose=False):
    result = []
    size = len(v)
    for i in range(size):
        val = 0.0
        for j in range(size):
            if transpose:
                val += m[j + size*i] * v[j]
            else:
                val += m[i + size*j] * v[j]
        result.append(val)
    return result

class String:
    string_force = 100.0
    log = False
    max_force = 2.0
    t = 0

    def __init__(self, link):
        self.link = link


    def set_string_force(self, force):
        self.string_force = force

    last_length = 1.0
    last_force = 0.0


    def modify_link(self, delta_t = 0.005):

        k_table = [[0., 0.], [0.250825, 16.18590359131938],
           [0.381, 20.109759007396804], [0.485775, 94.80314960629924],
           [0.508, 109.57480314960594], [0.5207, 438.29921259843525], [1000000, 438.29921259843525]]

        #k_table[1][0] = 0.250825 * (self.link.rest_length / 0.3)

        nodes = self.link.nodes

        # if self.t % 10 != 0:
        #     print("Link Velocity=",  self.link.body.getLinearVel())
        #     print("Link Angular Velocity=",  self.link.body.getAngularVel())
        #     print("Force=",  self.link.body.getForce())
        #     for node in nodes:
        #         print(" Node Velocity=",  node.body.getLinearVel())
        #         print("Node Force=",  node.body.getForce())
        #         node.body.setLinearVel((0, 0, 0))
        #     self.link.body.setLinearVel((0, 0, 0))
        #     self.t += 1
        #     self.link.update()
        #     return

        positions = [node.get_position() for node in nodes]
        velocities = [node.get_linear_vel() for node in nodes]
        relative_vel = [(velocities[1][i] - velocities[0][i]) for i in range(len(positions[0]))]

        if self.log:
            print("center before=", self.link.body.getPosition())


        center = [(positions[0][i] + positions[1][i])/2 for i in range(len(positions[0]))]
        lengths = [(positions[1][i] - positions[0][i]) for i in range(len(positions[0]))]
        length = math.sqrt(dot(lengths, lengths))

        old_vel_projection = max(-10, min(10, dot(relative_vel, normalize(lengths))))



        vel_projection = length - self.last_length
        #vel_projection = old_vel_projection


        force_dir = normalize(lengths)

        #self.link.rest_length = 0
        damping = max(-50, min(50, 1000 * vel_projection))
        #magnitude = 100.0 * (length * length) + damping
        dlength = length - self.link.rest_length * 0.5
        dlength = max(0, dlength)
        #magnitude = 100.0 * (length * length)

        k_force = 0.
        length_scale = self.link.rest_length / 0.3
        for i in range(0, len(k_table) - 1):
            delta = min(length- k_table[i][0] * length_scale, k_table[i + 1][0] * length_scale )
            if delta > 0.:
                k_force += delta * k_table[i][1]

        #print("k_force=", k_force, " length=", length)

        #magnitude = 10 * 2.5 * (dlength) + 2.5 * vel_projection
        if vel_projection < 0.0:
            magnitude = k_force + 10 * vel_projection
        else:
            magnitude = k_force
        #magnitude = min(100, max(0, magnitude))
        #magnitude = 200.0 * (dlength)
        #magnitude = self.string_force * (length * length) + 10 * vel_projection
        #magnitude = self.string_force * (dlength * dlength * dlength) + 10 * vel_projection
        #magnitude = 2 * self.string_force * (dlength * dlength) + 10 * vel_projection
        if dlength < 0:
            magnitude = 0.

        magnitude = max(0, min(self.max_force, magnitude))

        #magnitude *= 0.5
        # if magnitude > self.last_force + .01:
        #     magnitude = self.last_force + .01

        # if magnitude < self.last_force - .01:
        #     magnitude = self.last_force - .01
        self.last_force = magnitude

        if self.log:
            print("magnitude", magnitude, " length=", length, " k_force=", k_force)
        if self.link.color[1] > 0.0:
            pass
            #print("rotational=", self.link.nodes[0].body.getAngularVel())
            #print("rest length=", self.link.rest_length )
            # print("length=", length)
            # #print("dlength=", dlength)
            # #print("damping=", damping)
            # #print("last_length", self.last_length)

            # print("vel_projection", vel_projection)
            # print("old vel projectin=", old_vel_projection)
            #print("vel_projection", 1000* vel_projection, " magnitude=", magnitude)

            # if vel_projection != 0:
            #     print("l - ll / vel_proj", (length - self.last_length)/ vel_projection)
            # else:
            #     print("NO Velocity")
            #print("dlength=", dlength)
            #print("rest length=", self.link.rest_length )
            #print("magnitude=", magnitude)

        self.last_length = length



        nodes[0].add_force([force_dir[i] * magnitude for i in range(len(force_dir))])
        nodes[1].add_force([-force_dir[i] * magnitude for i in range(len(force_dir))])

        for node in nodes:
            pass
            #node.body.setForce([0.99 * v for v in node.body.getForce()])
        #self.link.body.setTorque([.99 * v for v in self.link.body.getTorque()])
            #node.body.addForce([-.001 * v for v in node.body.getLinearVel()])
            #node.body.setLinearVel((0, 0, 0))

        self.link.body.setLinearVel([0.5 * (velocities[0][i] + velocities[1][i]) for i in range(len(velocities[0]))])

        self.link.update()

        if self.log:
            pass
            #print("positions=", positions)
            #print("center=", self.link.body.getPosition())
            print("force=", [math.sqrt(sum([x * x for x in node.body.getForce()])) for node in nodes])
        self.t += 1



class ActuatedString:

    actuation_val = 0.0

    def __init__(self, string):
        self.string = string
        x = String(1.0)

    # sets actuation value between 0 and 1
    def set_actuation(self, actuation_val):
        self.actuation_val = actuation_val
        self.string.link.rest_length = actuation_val * 0.8


    def modify_link(self):
        self.string.modify_link()

class SineString:

    t = 0
    amplitude = 1.0
    phase = 0.0
    freq = 1.0
    offset = 0.0

    def __init__(self, string, amplitude=1.0, freq=1.0, phase=0.0, offset=0.0):
        self.act_string = ActuatedString(string)
        self.amplitude = amplitude
        self.phase = phase
        self.freq = freq
        self.offset = offset
        string.link.color = (0., 0., 1.)
        string.log = False
        string.max_force = 2.0


    def modify_link(self, delta_t):
        self.t += delta_t
        self.act_string.set_actuation(self.offset + self.amplitude * math.sin(self.freq * self.t + self.phase))
        self.act_string.modify_link()

class SurfaceString:

    curr_action = 0.5

    def __init__(self, string):
        self.act_string = ActuatedString(string)
        string.log = True
        string.max_force = 2.0


    def modify_link(self):
        nodes = self.act_string.string.link.nodes
        positions = [node.get_position() for node in nodes]
        print("positions=", positions)
        if positions[0][1] < -.2 and  positions[1][1] < -.2:
            self.act_string.string.link.color = (0., 0., 1.)
            if self.curr_action > 0.0:
                self.curr_action -= 0.001
            self.act_string.set_actuation(self.curr_action)
        else:
            self.act_string.string.link.color = (1., 0., 0.)
            if self.curr_action < 0.5:
                self.curr_action += 0.001
        self.act_string.modify_link()



class RocketRod:
    def __init__(self, link):
        self.link = link
        self.curr_dir = (0, 1, 0)
        self.t = 0

    def modify_linkx(self):
        nodes = self.link.nodes
        positions = [node.get_position() for node in nodes]
        lengths = [(positions[1][i] - positions[0][i]) for i in range(len(positions[0]))]
        #print(nodes[0].body.getRotation())
        #print(matrix_vector_mult(nodes[0].body.getRotation(), (0, 1, 0)))


        xp = matrix_vector_mult(nodes[0].body.getRotation(), (1, 0, 0))
        yp = matrix_vector_mult(nodes[0].body.getRotation(), (0, 1, 0))
        zp = matrix_vector_mult(nodes[0].body.getRotation(), (0, 0, 1))


        xv = dot((0, 1, -1), xp)
        yv = dot((0, 1, -1), yp)
        zv = dot((0, 1, -1), zp)
        goal_dir = [xv, yv, zv]

        max_angle = 2 * math.pi / 180.0
        alpha = (math.cos(max_angle) - dot(normalize(self.curr_dir), normalize(goal_dir))) / (1 - dot(normalize(self.curr_dir), normalize(goal_dir)))
        alpha = max(0, alpha)
        print("alpha=", alpha)

        self.curr_dir = [alpha * self.curr_dir[i] + (1 - alpha) * goal_dir[i] for i in range(3)]
        #print(dot(self.curr_dir, goal_dir))
        #print((xv, yv, zv))
        #print(matrix_vector_mult(nodes[0].body.getRotation(), (xv, yv, zv)))


        force = matrix_vector_mult(nodes[0].body.getRotation(), [v * 1.5 for v in self.curr_dir])
        print(force)
        self.link.nodes[1].add_force(force)

    def modify_link(self):
        print("t=", self.t)


        nodes = self.link.nodes
        positions = [node.get_position() for node in nodes]
        lengths = [(positions[1][i] - positions[0][i]) for i in range(len(positions[0]))]
        #print("lengths=", lengths)
        #print("length=", math.sqrt(dot(lengths, lengths)))
        #print("Location=", nodes[0].body.getPosition())
        if self.t < 3000:
            rot_matrix = nodes[0].body.getRotation()
            #print("test=", matrix_vector_mult(rot_matrix, matrix_vector_mult(rot_matrix, normalize((0, 1, 0))), transpose=True))
            #print("curr_rot_abs=", matrix_vector_mult(rot_matrix, normalize((0, 1, 0))))
            #print("curr_dir_pre_abs=", matrix_vector_mult(rot_matrix, normalize(self.curr_dir)))
            goal_dir = matrix_vector_mult(rot_matrix, normalize((0, 1, 1)), transpose=True)
            #print("goal_dir=", goal_dir)
            max_angle = 1 * math.pi / 180.0
            cos_target = dot(normalize(self.curr_dir), normalize(goal_dir))
            #print("cos_target=", cos_target)
            if cos_target < 1.0:
                alpha2 = (math.cos(max_angle) - cos_target) / (1 - cos_target)
                alpha = cos_target / math.cos(max_angle)
            else:
                alpha = 1.0
                alpha2 = 1.0
            alpha = max(0, alpha)
            #print("alpha=", alpha)
            #print("alpha2=", alpha2)
            self.curr_dir = [alpha * self.curr_dir[i] + (1 - alpha) * goal_dir[i] for i in range(3)]
            #self.curr_dir = [(2 - alpha) * self.curr_dir[i] - (1 - alpha) * goal_dir[i] for i in range(3)]
            self.curr_dir = normalize(self.curr_dir)
            #print("curr_dir=", self.curr_dir)
            force = matrix_vector_mult(rot_matrix, [v * 6.5 for v in self.curr_dir])
            #force = (0, 6.5, 0)
            #print("force=", force)
            self.link.nodes[0].add_force(force)

        self.t += 1






