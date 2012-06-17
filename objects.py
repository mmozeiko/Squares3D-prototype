import ode
from OpenGL.GL import * 
from OpenGL.GLU import *
from math import sin, cos, sqrt, asin, acos, pi, atan2
from pyglfw.glfw import *
import vectormath
from Image import *
from random import random
def loadTexture(file):
  #global texture
  image = open(file)

  ix = image.size[0]
  iy = image.size[1]
  if image.mode=="RGBA":
    image = image.tostring("raw", "RGBA", 0, -1)
    chans=4
  else:                      
    image = image.tostring("raw", "RGBX", 0, -1)
    chans=3

  # Create Texture
  textureID = glGenTextures(1)
  glBindTexture(GL_TEXTURE_2D, textureID)   # 2d texture (x and y size)

  glPixelStorei(GL_UNPACK_ALIGNMENT,1)
  glTexImage2D(GL_TEXTURE_2D, 0, chans, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
  glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
  glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
  gluBuild2DMipmaps(GL_TEXTURE_2D, chans, ix, iy, GL_RGBA, GL_UNSIGNED_BYTE, image) 

  return textureID

class CommonInterface:
  def __init__(self):
    pass
  def draw(self):
    pass
  def applyInputs(self, speed):
    pass

class Interactive(CommonInterface):
  def applyInputs(self, performance):
    dx, dy, dz, rotationAngle = self.getMovement()
    dx *= performance
    dy *= performance
    dz *= performance
    rotationAngle *= performance
    
    ax, ay, az = self.body.getAngularVel()

    brake = 1.5

    self.body.setAngularVel((0.0, ay/brake, 0.0))
##    if az*az < 50*50 and rotationAngle != 0.0:
    self.body.setTorque((0.0,rotationAngle,0.0))

    vx, vy, vz = self.body.getLinearVel()

    if dy != 0: vy = 0
    
    if vy > 15.0: vy = 14.0
    self.body.setLinearVel((vx/brake, vy, vz/brake))

    self.body.setForce((dx, dy, dz))

    a = self.body.getAngularVel()
    q = self.body.getQuaternion()
    L = 1.0/sqrt(q[0]*q[0] + q[2]*q[2])
    self.body.setQuaternion((q[0]*L, 0.0, q[2]*L, 0.0))
    self.body.setAngularVel((0.0, a[1], 0.0))

  def getMovement(self):
    return 0.0, 0.0, 0.0, 0.0

class HumanInteractive(Interactive):
  def getMovement(self):
    dx, dy, dz, rotationAngle = (0,0,0,0)
    
    mouseSPEED = 50000.0 * self.body.getMass().mass

    #if mousebutton2 is pressed, jump
    if glfwGetMouseButton(GLFW_MOUSE_BUTTON_1) == GLFW_PRESS:
      if self.body.getPosition()[1] < self.geom.getLengths()[1] / 2 + 0.1:
        dy = 0.2

    W, H = glfwGetWindowSize()
    mx0, my0 = W/2, H/2
    if W==0 or H==0: return
    mx, my = glfwGetMousePos()

    #if mousebutton2 is pressed, rotate    
    if glfwGetMouseButton(GLFW_MOUSE_BUTTON_2) == GLFW_PRESS:
      rotationAngle = float(mx0-mx) / (mx0)
    elif mx0 != mx or my0 != my:
      #move around
      if mx0 != 0.0: dx = float(mx0 - mx) / mx0
      if my0 != 0.0: dz = float(my0 - my) / my0
      if abs(mx0 - mx) > 5: dx*=1.5
      if abs(my0 - my) > 5: dz*=1.5
    glfwSetMousePos(mx0, my0)
    
    a = self.camera.angleY*pi/180.0
    _dx = dx*cos(a) + dz*sin(a)
    _dy = dy
    _dz = -dx*sin(a) + dz*cos(a)

    return _dx * (-mouseSPEED), _dy * mouseSPEED, _dz * (-mouseSPEED), rotationAngle * mouseSPEED

class ComputerInteractive(Interactive):
  def getMovement(self):
    dx, dy, dz, rotationAngle = (0,0,0,0)

    #move to ball/square border intersection
    currentPosition = self.body.getPosition()
    target = self.target.getPosition()

    if (target[0]-currentPosition[0]) * (target[0]-currentPosition[0]) +  \
       (target[2]-currentPosition[2]) * (target[2]-currentPosition[2]) < 2.0 and \
       currentPosition[1]<1.1:
      dy = 2.0
      
    if vectormath.isPointInSquare(target, self.min, self.max):
      targetPosition = target
    else:
      targetPosition = vectormath.getBallAndSquareIntersection(target,
                                                               self.target.getLinearVel(),
                                                               self.min,
                                                               self.max)  
    targetPosition = (targetPosition[0] + random() - 0.5, targetPosition[1], targetPosition[2] + random() - 0.5)
    
    vectorAB = vectormath.getVector(currentPosition, targetPosition)

    #to make oponents run to ball coords - self length
    vABAngle = atan2(vectorAB[2], vectorAB[0])

    vABMagnitude = vectormath.getMagnitudeV(vectorAB)

    newVABMagnitude = vABMagnitude - 2.0 #malas garums/2

    newVABX = [cos(vABAngle) * newVABMagnitude, vectorAB[1], sin(vABAngle) * newVABMagnitude]

    vectorAB = newVABX
    
    if vABMagnitude<1.8:
      moveSpeed = 700 * self.body.getMass().mass
    else:
      moveSpeed = 4000 * self.body.getMass().mass
    
    currentRotationTuple = self.body.getRotation()
    currentRotation = currentRotationTuple[2], currentRotationTuple[5], currentRotationTuple[8]

    vectorAB = vectormath.normalize(vectorAB[0], 0, vectorAB[2])    

    rotationAngle = vectormath.getAngleBetweenVectors(currentRotation, vectorAB)

    currentRotation = vectormath.negate(currentRotation)

    dx = currentRotation[0]
    dz = currentRotation[2]


    #/------------------

    return dx * moveSpeed, dy * moveSpeed, dz * moveSpeed, rotationAngle * moveSpeed

class Cube: 
  def __init__(self, world, position = (0.0, 0.51, 0.0), mass = 1.0, size = (1.0, 1.0, 1.0), color = (0,0,0)): 
    # Create a body inside the world
    self.body = ode.Body(world)
    self.m = ode.Mass()
    self.m.setBox(mass, size[0], size[1], size[2])
    self.body.setMass(self.m)
    self.body.setPosition(position)

    self.geom = ode.GeomBox(world.space, lengths=size)
    self.geom.setBody(self.body)
    self.geom.name = 'Cube'
    self.q = gluNewQuadric()
    self.color = color

  def draw(self):
    glMultMatrixd(vectormath.extractMatrix(self.body))
    sx, sy, sz = self.geom.getLengths()
    glScalef(sx, sy, sz)

##    glPushMatrix()
##    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1, 0, 0))
##    
##    glTranslate(0.0, 0.5, 0.0)
##    glRotatef(180.0, 0.0, 1.0, 0.0)
##    gluCylinder(self.q, 0.2, 0.0, 1.0, 32, 32)
##    glRotatef(180.0, 0.0, 1.0, 0.0)
##    gluDisk(self.q, 0.0, 0.2, 32, 32)
##    glPopMatrix()
    
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.color)
    renderCube(1.0)

class Sphere(CommonInterface): 
  def __init__(self, world, position = (0.0, 1.1, 0.0), mass = 1.0, size = 1.0, color = (0.0, 1.0, 0.0)): 
    # Create a body inside the world
    self.body = ode.Body(world)
    self.m = ode.Mass()
    self.m.setSphere(mass, size)
    self.body.setMass(self.m)
    self.body.setPosition(position)
    
    self.geom = ode.GeomSphere(world.space, size)
    self.geom.setBody(self.body)
    self.geom.name = 'Sphere'
    self.color = color
    self.q = gluNewQuadric()
    self.textureBall = loadTexture("DATA\\TEX\\football.png")
    gluQuadricTexture(self.q, True) 
    #gluDeleteQuadric(q)

  def draw(self):
    glBindTexture(GL_TEXTURE_2D, self.textureBall)
    glEnable(GL_TEXTURE_2D)
##    glTexEnvfv(GL_TEXTURE_ENV, GL_TEXTURE_ENV_COLOR, self.color)
      
    glMultMatrixd(vectormath.extractMatrix(self.body))
    #glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.color)
    gluSphere(self.q, self.geom.getRadius(), 32, 32)
    glDisable(GL_TEXTURE_2D)

class BoundingBox(CommonInterface):
  def __init__(self, world, xDelta, zDelta): 
    # Create a body inside the world
    self.geom = ode.GeomPlane(world.space, (0,1,0), 0)
    self.geom.name = 'Ground'
    self.geom1 = ode.GeomPlane(world.space, (1.0, 0.0, 0.0), -xDelta)
    self.geom1.name = 'Bound'
    self.geom2 = ode.GeomPlane(world.space, (-1.0, 0.0, 0.0), -xDelta)
    self.geom2.name = 'Bound'
    self.geom3 = ode.GeomPlane(world.space, (0.0, 0.0, 1.0), -zDelta)
    self.geom3.name = 'Bound'
    self.geom4 = ode.GeomPlane(world.space, (0.0, 0.0, -1.0), -zDelta)
    self.geom4.name = 'Bound'
    self.geom5 = ode.GeomPlane(world.space, (0,-1,0), -40)
    self.geom5.name = 'Sky'

class DummyGeom:
  def __init__(self, name):
    self.name = name
    
class Field(CommonInterface): 
  def __init__(self):
    self.geom = DummyGeom('Field')
    self.texturePavement = loadTexture("DATA\\TEX\\pavquarter.png")
    self.textureGrass = loadTexture("DATA\\TEX\\grass.png")
    self.textureWall = loadTexture("DATA\\TEX\\brick.png")
    self.textureSky = loadTexture("DATA\\TEX\\sky.png")
    self.textureSky2 = loadTexture("DATA\\TEX\\sky2.png")

  def draw(self):

    #PAVEMENT SQUARES    
    glBindTexture(GL_TEXTURE_2D, self.texturePavement)
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)

    glTexCoord2f(0.0, 0.0); glVertex3f( -10.0, 0.0,  -10.0)
    glTexCoord2f(0.0, 1.0); glVertex3f(-10.0, 0.0,  0.0)   
    glTexCoord2f(1.0, 1.0); glVertex3f(0.0,  0.0,  0.0)
    glTexCoord2f(1.0, 0.0); glVertex3f(0.0,  0.0,  -10.0) 

    glTexCoord2f(0.0, 0.0); glVertex3f(0.0, 0.0,  -10.0)   
    glTexCoord2f(0.0, 1.0); glVertex3f(0.0, 0.0,  0.0)
    glTexCoord2f(1.0, 1.0); glVertex3f(10.0,  0.0,  0.0)
    glTexCoord2f(1.0, 0.0); glVertex3f(10.0,  0.0,  -10.0)  

    glTexCoord2f(0.0, 0.0); glVertex3f(0.0, 0.0,  0.0) 
    glTexCoord2f(1.0, 0.0); glVertex3f(0.0, 0.0,  10.0)
    glTexCoord2f(1.0, 1.0); glVertex3f(10.0,  0.0,  10.0)
    glTexCoord2f(0.0, 1.0); glVertex3f(10.0,  0.0,  0.0)  

    glTexCoord2f(0.0, 0.0); glVertex3f(-10.0, 0.0,  0.0)
    glTexCoord2f(1.0, 0.0); glVertex3f(-10.0, 0.0,  10.0)
    glTexCoord2f(1.0, 1.0); glVertex3f(0.0,  0.0,  10.0)
    glTexCoord2f(0.0, 1.0); glVertex3f(0.0,  0.0,  0.0)

    glEnd()

    #GRASS
    glPushMatrix()
    glBindTexture(GL_TEXTURE_2D, self.textureGrass)    
    glRotatef(-90.0, 1.0, 0.0, 0.0)    
    glBegin(GL_QUADS)
    length = 5.0
    for x in range(-4, 4):
      for y in range(-4, 4):
        if (x < -2 or x >= 2) or (y < -2 or y >= 2):
          glTexCoord2f(0.0, 0.0); glVertex3f(length*x, length*y, 0.0)          # Top Left
          glTexCoord2f(1.0, 0.0); glVertex3f((length*x + length), length*y, 0.0)           # Top Right
          glTexCoord2f(1.0, 1.0); glVertex3f((length*x + length), (length*y + length), 0.0)          # Bottom Right
          glTexCoord2f(0.0, 1.0); glVertex3f(length*x, (length*y + length), 0.0)         # Bottom Left
    glEnd()
    glPopMatrix()

    #WALLs
    angle = 0
    for i in range(4):
      glPushMatrix()
      glBindTexture(GL_TEXTURE_2D, self.textureWall)    
      glRotatef(angle, 0.0, 1.0, 0.0)
      glTranslate(0, 0, -20)
      glBegin(GL_QUADS)
      length = 5.0
      for x in range(-4, 4):
        glTexCoord2f(0.0, 0.0); glVertex3f(length*x, 0.0, 0.0)          # Top Left
        glTexCoord2f(1.0, 0.0); glVertex3f((length*x + length), 0.0, 0.0)           # Top Right
        glTexCoord2f(1.0, 1.0); glVertex3f((length*x + length), length, 0.0)          # Bottom Right
        glTexCoord2f(0.0, 1.0); glVertex3f(length*x, length, 0.0)         # Bottom Left
      glEnd()
      glPopMatrix()
      angle += 90

    #SKY
      
    #box delta
    delta = 21.0
    glBindTexture(GL_TEXTURE_2D, self.textureSky)
##    glBindTexture(GL_TEXTURE_2D, self.textureTest)

    glPushMatrix()
    glRotatef(0.0, 0.0, 1.0, 0.0)
    glTranslate(0.0, delta, 0.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(-delta, 0.0,  delta) 
    glTexCoord2f(0.0, 1.0); glVertex3f( -delta, 0.0,  -delta) 
    glTexCoord2f(1.0, 1.0); glVertex3f(delta,  0.0,  -delta)  
    glTexCoord2f(1.0, 0.0); glVertex3f(delta,  0.0,  delta)
    glEnd()
    glPopMatrix()

    glPushMatrix()
    glRotatef(90.0, 1.0, 0.0, 0.0)
    glTranslate(0, delta, 0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0); glVertex3f(-delta, 0.0,  delta) 
    glTexCoord2f(0.0, 0.0); glVertex3f( -delta, 0.0,  -delta) 
    glTexCoord2f(1.0, 0.0); glVertex3f(delta,  0.0,  -delta)  
    glTexCoord2f(1.0, 1.0); glVertex3f(delta,  0.0,  delta)
    glEnd()
    glPopMatrix()    

    glPushMatrix()
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    glTranslate(0, delta, 0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0); glVertex3f(-delta, 0.0,  delta) 
    glTexCoord2f(0.0, 0.0); glVertex3f( -delta, 0.0,  -delta) 
    glTexCoord2f(1.0, 0.0); glVertex3f(delta,  0.0,  -delta)  
    glTexCoord2f(1.0, 1.0); glVertex3f(delta,  0.0,  delta)
    glEnd()
    glPopMatrix() 

    glBindTexture(GL_TEXTURE_2D, self.textureSky2)

    glPushMatrix()
    glRotatef(90.0, 0.0, 0.0, 1.0)
    glTranslate(0, delta, 0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(-delta, 0.0,  delta) 
    glTexCoord2f(0.0, 1.0); glVertex3f( -delta, 0.0,  -delta) 
    glTexCoord2f(1.0, 1.0); glVertex3f(delta,  0.0,  -delta)  
    glTexCoord2f(1.0, 0.0); glVertex3f(delta,  0.0,  delta)
    glEnd()
    glPopMatrix()

    glPushMatrix()
    glRotatef(-90.0, 0.0, 0.0, 1.0)
    glTranslate(0, delta, 0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(-delta, 0.0,  delta) 
    glTexCoord2f(0.0, 1.0); glVertex3f( -delta, 0.0,  -delta) 
    glTexCoord2f(1.0, 1.0); glVertex3f(delta,  0.0,  -delta)  
    glTexCoord2f(1.0, 0.0); glVertex3f(delta,  0.0,  delta)
    glEnd()
    glPopMatrix()   
    
    glDisable(GL_TEXTURE_2D)

def renderCube(size):
  L = size*0.5
  glBegin(GL_QUADS);
  glNormal3f( 0.0,  0.0, 1.0)
  glVertex3f(-L, -L,  L)
  glVertex3f( L, -L,  L)
  glVertex3f( L,  L,  L)
  glVertex3f(-L,  L,  L)

  glNormal3f( 0.0, 0.0,-1.0)
  glVertex3f(-L, -L, -L)
  glVertex3f(-L,  L, -L)
  glVertex3f( L,  L, -L)
  glVertex3f( L, -L, -L)

  glNormal3f( 0.0, 1.0, 0.0)
  glVertex3f(-L,  L, -L)
  glVertex3f(-L,  L,  L)
  glVertex3f( L,  L,  L)
  glVertex3f( L,  L, -L)

  glNormal3f( 0.0,-1.0, 0.0)
  glVertex3f(-L, -L, -L)
  glVertex3f( L, -L, -L)
  glVertex3f( L, -L,  L)
  glVertex3f(-L, -L,  L)

  glNormal3f( 1.0, 0.0, 0.0)
  glVertex3f( L, -L, -L)
  glVertex3f( L,  L, -L)
  glVertex3f( L,  L,  L)
  glVertex3f( L, -L,  L)

  glNormal3f(-1.0, 0.0, 0.0)
  glVertex3f(-L, -L, -L)
  glVertex3f(-L, -L,  L)
  glVertex3f(-L,  L,  L)
  glVertex3f(-L,  L, -L)
  glEnd()

class CoordAxis(CommonInterface):
  def __init__(self):
    self.geom = DummyGeom('CoordAxis')
  def draw(self):
    # asis
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)
    
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-5.0, 0.0, 0.0)
    glVertex3f(100.0, 0.0, 0.0)

    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -5.0, 0.0)
    glVertex3f(0.0, 5.0, 0.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(0.0, 0.0, 5.0)
    glEnd()

    glEnable(GL_LIGHTING)

    # ashu bultinjas
    q = gluNewQuadric()
   
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1.0, 0.0, 0.0))
    glTranslate(5.0, 0.0, 0.0)
    glRotatef(90.0, 0.0, 1.0, 0.0)
    gluCylinder(q, 0.2, 0.0, 1.0, 32, 32)
    glRotatef(180.0, 0.0, 1.0, 0.0)
    gluDisk(q, 0.0, 0.2, 32, 32)
    glPopMatrix()

    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.0, 1.0, 0.0))
    glTranslate(0.0, 5.0, 00.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    gluCylinder(q, 0.2, 0.0, 1.0, 32, 32)
    glRotatef(180.0, 0.0, 1.0, 0.0)
    gluDisk(q, 0.0, 0.2, 32, 32)
    glPopMatrix()

    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.0, 0.0, 1.0))
    glTranslate(0.0, 0.0, 5.0)
    gluCylinder(q, 0.2, 0.0, 1.0, 32, 32)
    glRotatef(180.0, 0.0, 1.0, 0.0)
    gluDisk(q, 0.0, 0.2, 32, 32)
    glPopMatrix()
    
    gluDeleteQuadric(q)
