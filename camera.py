from pyglfw.glfw import *
import vectormath
from OpenGL.GLU import gluLookAt
from math import atan2, pi
from sound import sounds

class Camera: 
  def __init__(self, x0, y0, z0, angleA0, angleB0): 
    self.setCameraView(x0, y0, z0, angleA0, angleB0)
    self.target = None
    self.oldTargetPos = None
    self.delta = 10
    
  def setTarget(self, target):
    self.target = target
  def setCameraView(self, x, y, z, angleX, angleY): 
    self.x = x 
    self.y = y 
    self.z = z 
    self.angleX = angleX 
    self.angleY = angleY 

  def applyInputs(self, performance): 
    moveSpeed = 5
    turnSpeed = 100
    mouseSPEEDmultiplier = 0.4
    deltaY = 0
    deltaX = 0

    if glfwGetKey(GLFW_KEY_UP):
      deltaX = +moveSpeed * performance 
    if glfwGetKey(GLFW_KEY_DOWN): 
      deltaX = -moveSpeed * performance 
    if glfwGetKey(GLFW_KEY_LEFT): 
      deltaY = -moveSpeed * performance 
    if glfwGetKey(GLFW_KEY_RIGHT): 
      deltaY = +moveSpeed * performance
    self.x += deltaX
    self.z += deltaY
  def draw(self):
    #set listener position at camera
    sounds.setListenerPosition((self.x, self.y, self.z))

    #target coord
    tx, ty, tz = self.target.body.getPosition()

    if self.oldTargetPos==None:
      self.oldTargetPos = tx, ty, tz
    
    gluLookAt(self.x, self.y, self.z, (tx+self.oldTargetPos[0])/2, (self.y+self.oldTargetPos[1])/2/3, (tz+self.oldTargetPos[2])/2, 0, 1, 0)
    self.oldTargetPos = tx, ty, tz

    v = vectormath.getVector((self.x, 0.0, self.z), (tx, 0.0, tz))
    self.angleY = -(atan2(v[2], v[0]) + pi/2)*180.0/pi