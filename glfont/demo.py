from OpenGL.GL import *
from OpenGL.GLU import *
from pyglfw.glfw import *
from glFont import GLFont
import sys

if not glfwInit():
  print "Failed to initialize glfw!"
  sys.exit()

if not glfwOpenWindow(640, 480, 8, 8, 8, 8, 24, 8, GLFW_WINDOW):
  print "Failed to open windo!"
  sys.exit()
            
## !!!
font = GLFont("font.glf")
font_aa = GLFont("font_aa.glf")
## !!!

glClearColor(0.0, 0.0, 0.0, 1.0);

running = True
while running:
  W, H = glfwGetWindowSize()
  if W!=0 and H!=0: 
    glViewport(0, 0, W, H)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

  glClear(GL_COLOR_BUFFER_BIT)

## !!!
  font.begin()
  glColor3f(1.0, 0.0, 0.0)
  font.render("blabla\nThis is Second line!", 100.0, 100.0)
  glColor3f(0.0, 0.0, 1.0)
  font.render("Another text!", 50.0, 400.0)
  font.end()

  font_aa.begin()
  glColor3f(0.3, 0.3, 0.3)
  font_aa.renderShadowed("Antialiased text, with shadow!", 200.0, 300.0)
  font_aa.end()
## !!!

  glfwSwapBuffers()

  running = running and glfwGetWindowParam(GLFW_OPENED) and not glfwGetKey(GLFW_KEY_ESC)

glfwCloseWindow()
glfwTerminate()
