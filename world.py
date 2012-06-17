import ode
from OpenGL.GL import *
from camera import Camera
from pyglfw.glfw import glfwGetTime, glfwSwapBuffers,\
                        GLFW_STICKY_MOUSE_BUTTONS,\
                        glfwDisable, glfwGetKey, GLFW_KEY_ESC
import gameglobals

from Image import *
from coach import Coach
from sound import sounds

CLOCK = glfwGetTime

t0 = CLOCK()
frames = 0

def framerate(): 
  global t0, frames 
  t = CLOCK() 
  frames += 1 
  if t - t0 >= 5.0: 
    seconds = t - t0 
    fps = frames/seconds 
    print "%.0f frames in %3.1f seconds = %6.3f FPS" % (frames,seconds,fps) 
    t0 = t
    frames = 0

def near_callback(args, geom1, geom2):
  """Callback function for the collide() method.

  This function checks if the given geoms do collide and
  creates contact joints if they do.
  """

  # Check if the objects do collide

  friction = 100.0
  bounce = 0.7

  contacts = ode.collide(geom1, geom2)
  geoms = [geom1, geom2]
  geomNames = [g.name for g in geoms]
  
  if len(contacts) > 0:
    world, contactgroup = args
    #coach must track ball and register events
    if 'Ball' in geomNames:
      ball = [g for g in geoms if g.name == 'Ball'][0]
      for g in geoms:
        if g.name != 'Ball' and g.name != 'Bound':
          world.coach.objectList.append(g)
        elif g.name == 'Bound':
          sounds.playSound("BallGround", ball.getPosition())
      friction = 600.0
    if 'Player' in geom1.name and 'Player' in geom2.name:
      sounds.playSound("Player", geom1.getPosition())

  # Create contact joints
  if 'Trigger' not in geomNames:
    for c in contacts:
      c.setBounce(bounce)
      c.setMu(friction)
      j = ode.ContactJoint(world, contactgroup, c)
      j.attach(geom1.getBody(), geom2.getBody())
      break
       
class GameWorld(ode.World): 
  def __init__(self): 
    self.objectList = [] 
    self.performance = 0
    ode.World.__init__(self)
    self.coach = Coach()
    self.camera = Camera(0.0, 14.0, 19.5, -30.0, 0.0) 
    self.objectList.append(self.camera)
    self.setGravity((0.0, -9.81, 0.0))

    self.contactgroup = ode.JointGroup()
    self.space = ode.Space()
    
    self.accum = 0.0
    self.time0 = 0
    self.startTime = 0

  def launchClock(self):
    self.time0 = CLOCK()

  def applyInputs(self): 
    glfwDisable(GLFW_STICKY_MOUSE_BUTTONS)
    if not self.coach.gameOver:
      for object in self.objectList: 
        object.applyInputs(self.performance)
    if (gameglobals.gameState == 1 or gameglobals.gameState == 2) and glfwGetKey(GLFW_KEY_ESC):
      gameglobals.gameState = 0

  def draw(self): 
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    self.camera.draw()
    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 17.0, 10.0, 1.0))
    for part in self.objectList:
      glPushMatrix() 
      part.draw() 
      glPopMatrix()
    self.coach.draw(self.performance)

  def addObject(self, object):
    if 'Player' in object.geom.name:
      self.coach.register(object)
    if 'Ball' in object.geom.name:
      self.camera.setTarget(object)
      self.coach.ball = object
    self.objectList.append(object)
    

  def idle(self): 
    gameWorld = self
    newTime = CLOCK()
    deltaTime = newTime - gameWorld.time0
    
    self.accum += deltaTime

    p = deltaTime

    while self.accum >= 1.0/60.0:
      gameWorld.performance = 1.0/60.0 #deltaTime
      gameWorld.applyInputs()
      c = gameWorld.coach
      c.objectList = []
      gameWorld.space.collide((gameWorld, gameWorld.contactgroup), near_callback)
      c.manageGame()
      
      gameWorld.step(1.0/60.0)
      self.accum -= 1.0/60.0
    
    gameWorld.performance = p
    gameWorld.draw()
    gameWorld.contactgroup.empty()    
    glfwSwapBuffers()
    gameWorld.time0 = newTime
    framerate()
