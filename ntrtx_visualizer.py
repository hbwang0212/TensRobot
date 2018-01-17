import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import time



class ntrtx_visualizer:

    rotate_x = 0.0
    rotate_y = 0.0
    zoom = 2.0
    origin = (0., 0., 0.)

    def __init__(self, ntrtx, idle_callback, grid_height=0.0):
        self.ntrtx = ntrtx
        self.idle_callback = idle_callback
        self.grid_height = grid_height
        self.pause = True
        self.inc = False

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
        glutCreateWindow("NTRTx Visualizer")

        glutKeyboardFunc(self._keyfunc)
        glutSpecialFunc(self._keyfunc)
        glutMouseFunc(self.mouse_button_func)
        glutMotionFunc(self.mouse_move_func)
        glutDisplayFunc(self._drawfunc)
        glutIdleFunc(self._idlefunc)

        glutMainLoop()

    # prepare_GL
    def prepare_GL(self):
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
        glEnable(GL_COLOR_MATERIAL)
        glShadeModel(GL_FLAT)

        # Projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.3333, 0.2, 20)

        # Initialize ModelView matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Light source
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, -1, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
        #glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])
        glEnable(GL_LIGHT0)

        glRotatef(self.rotate_x, 1.0, 0.0, 0.0 )
        glRotatef(self.rotate_y, 0.0, 1.0, 0.0 )
        # View transformation
        #gluLookAt(2.4 * .5, 3.6 * .5, 4.8 * .5, 0.4 , 0.5, 1, 0, 1, 0)
        gluLookAt(self.origin[0], self.origin[1], self.origin[2] + self.zoom, self.origin[0] , self.origin[1], self.origin[2], 0, 1, 0)



    def set_camera_position(self, origin):
        self.origin = origin

    def draw_grid(self, size=10, y=-1.0):
        glColor3f(.8,.8,.8)
        glBegin(GL_QUADS)
        glVertex3f( -size,-0.001 + y, -size)
        #glNormal3f(.0, 1., .0)
        glVertex3f( -size,-0.001 + y,size)
        #glNormal3f(.0, 1., .0)
        glVertex3f(size,-0.001 + y,size)
        #glNormal3f(.0, 1., .0)
        glVertex3f(size,-0.001 + y, -size)
        #glNormal3f(.0, -1., .0)
        glEnd()

        glBegin(GL_LINES)
        for i in range(-size, size):
            if i==0:
                glColor3f(.6,.3,.3)
            else:
                glColor3f(.25,.25,.25)
            glVertex3f(i,y,-size)
            glVertex3f(i,y,size)
            if i==0:
                glColor3f(.3,.3,.6)
            else:
                glColor3f(.25,.25,.25)
            glVertex3f(-size,y,i)
            glVertex3f(size,y,i)
        glEnd()

    # draw_body
    def draw_body(self, body, color=(0.9, 0.9, 0.9)):
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
        glColor(color[0], color[1], color[2], 0)
        if body.shape == "box":
            sx, sy, sz = body.boxsize
            glScalef(sx, sy, sz)


            glutSolidCube(1)
        #glutSolidSphere(0.5, 10, 10)
        elif body.shape == "sphere":
            r = body.radius
            #print("radius=", body.radius)
            glScalef(r, r, r)
            #glutSolidSphere(1, 10, 10)
            glRasterPos2i(0, 0)
            for c in body.name:
                glutBitmapCharacter(OpenGL.GLUT.GLUT_BITMAP_TIMES_ROMAN_24, ord(c));
            glutSolidSphere(0.5, 10, 10)
        glPopMatrix()

    # keyboard callback
    def _keyfunc(self, key, x, y):
        #print("GLUT_KEY_RIGHT", str(OpenGL.GLUT.GLUT_KEY_RIGHT), key==OpenGL.GLUT.GLUT_KEY_RIGHT)
        if key == GLUT_KEY_LEFT:
            self.rotate_y += 10
        elif key == GLUT_KEY_RIGHT:
            print("here 2")
            self.rotate_y -= 10
        elif key == GLUT_KEY_UP:
            self.rotate_x += 10
        elif key == GLUT_KEY_DOWN:
            self.rotate_x -= 10
        elif key == ' ':
            self.pause = not self.pause
        elif key == 'n':
            self.inc = True

        print(key, self.rotate_x)


        glutPostRedisplay()

    isDragging = False
    def mouse_move_func(self, x, y):
        if self.isDragging:
            self.rotate_y = self.start_rotate_y + (x - self.xDragStart) * 0.25
            self.rotate_x = self.start_rotate_x + (y - self.yDragStart) * 0.25
            self.deltaAngle = (x - self.xDragStart) * 0.005


            glutPostRedisplay()
        elif self.isZooming:
            self.zoom = self.start_zoom + (x - self.xDragStart) * 0.01


    def mouse_button_func(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN: # left mouse button pressed
                self.isDragging = 1 # start dragging
                self.xDragStart = x # save x where button first pressed
                self.yDragStart = y # save x where button first pressed
                self.start_rotate_y = self.rotate_y
                self.start_rotate_x = self.rotate_x
            else: # (state = GLUT_UP)
               # self.rotate_x += self.deltaAngle # update camera turning angle
                self.isDragging = 0 # no longer dragging
        if button == GLUT_RIGHT_BUTTON:
            if state == GLUT_DOWN: # left mouse button pressed
                self.isZooming = True
                self.xDragStart = x # save x where button first pressed
                self.yDragStart = y # save x where button first pressed
                self.start_zoom = self.zoom
            else:

                self.isZooming = False


    # draw callback
    def _drawfunc(self):
        # Draw the scene

        self.prepare_GL()

        self.draw_grid(y=self.grid_height)
        for node in self.ntrtx.nodes:
            self.draw_body(node.body, node.color)
        for link in self.ntrtx.links:
            self.draw_body(link.body, link.color)

        glutSwapBuffers()

    step_count = 0
    last_time = 0.0
    def _idlefunc(self):


        if not self.pause or self.inc:

            if self.step_count % 10 == 0:
                glutPostRedisplay()
            self.idle_callback()

            print("Time=", time.clock())
            curr_time = time.clock()
            print("Delta Time=", curr_time - self.last_time)
            self.last_time = curr_time

        else:
            glutPostRedisplay()

        self.step_count += 1
        self.inc = False





