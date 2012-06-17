import objects
from OpenGL.GL import *
from OpenGL.GLU import gluSphere
from vectormath import getVector, multiply

class Ball(objects.Sphere):
  def __init__(self, world):
    objects.Sphere.__init__(self, world, mass = 25.0, size = 0.5)
    self.geom.name = 'Ball'
    self.geom.reset = False
    self.geom.resetCoords = ()
  def resetIfAsked(self):
    aimedForce = (0.0, 0.0, 0.0)
    if abs(self.geom.resetCoords[0])\
       + abs(self.geom.resetCoords[2]) > 1.0: # if we don`t drop the ball in center
      #we drop it in the players field with force
      aimVector = getVector(self.geom.resetCoords, (0.0, 0.0, 0.0))
      aimedForce = multiply(aimVector, 1000)
    
    if self.geom.reset == True:
      self.body.setPosition(self.geom.resetCoords)
      self.body.setAngularVel((0.0, 0.0, 0.0))
      self.body.setLinearVel((0.0, 0.0, 0.0))
      self.body.setForce(aimedForce)
      self.geom.reset = False
      
  def applyInputs(self, performance):
    self.resetIfAsked()

  def draw(self):
    #draw ball
    glPushMatrix()
    objects.Sphere.draw(self)
    glPopMatrix()

    #draw shadow
    shadowPosition = self.body.getPosition()
    glTranslatef(shadowPosition[0], 0.05, shadowPosition[2])
    glColor4f(0.2, 0.2, 0.2, 0.2)
    glScalef(1.0, 0.0, 1.0)
    glDisable(GL_LIGHTING)
    gluSphere(self.q, self.geom.getRadius(), 32, 32)
    glEnable(GL_LIGHTING)
    