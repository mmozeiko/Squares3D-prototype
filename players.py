import ode
from math import sin, cos, pi
from random import randint
import objects
from OpenGL.GL import * 
import vectormath
import pyopenal
import sound

colorNamesColors = {'Blue':(0, 0, 1),
                    'Red':(1, 0, 0),
                    'Green':(0, 1, 0),
                    'Yellow':(1, 1, 0)}

INDEX = 0
def getColor():
  global INDEX
  index = INDEX
  INDEX += 1
  return ['Blue', 'Red', 'Green', 'Yellow'][index]

def getRGBValues(color):
  return colorNamesColors[color]

class TriggerBox(objects.CommonInterface, objects.Cube):
  #TriggerBox is used to determine whether the ball is standing on cube or bouncing up and down
  def __init__(self, world, position, size, owner):
    objects.Cube.__init__(self, world, position, 1, size)
    self.geom.name = 'Trigger'
    self.geom.ownerName = owner

class Player(objects.Cube):
  def __init__(self, world, position = (0.0, 0.0, 0.0)):
    #stores the initial position
    self.initPos = position
    color = getColor()

    #inits the cube with player position, mass, size and color
    objects.Cube.__init__(self, world, position, 50, (2.0, 2.0, 2.0), getRGBValues(color))
    self.geom.name = self.setName(color)

    #inits the trigger with according values
    #trigger box is around player cube
    self.trigger = TriggerBox(world, position, (2.2, 2.2, 2.2), self.geom.name)

    #joins the player body with the trigger
    self.j = ode.FixedJoint(world)
    self.j.attach(self.body, self.trigger.body)
    self.j.setFixed()

    self.min = [0, 0]
    self.max = [0, 0]
    #gets the largest and smallest coordinates of the players square
    a = 10.0*position[0]/abs(position[0])
    b = 10.0*position[2]/abs(position[2])

    #stores the player`s square min and max coordinates
    if a>0:
      self.max[0] = a
    else:
      self.min[0] = a
    if b>0:
      self.max[1] = b
    else:
      self.min[1] = b

    self.camera = None
    self.setAngle()

  def getAngle(self):
    pass

  def setAngle(self):
    angle = self.getAngle()
    #rotates player body to the field center
    self.body.setRotation((cos(angle),        0.0, -sin(angle),
                                  0.0,        1.0,         0.0,
                           sin(angle),        0.0,  cos(angle)))

  def setInitPosition(self):
    self.body.setPosition(self.initPos)
    
  def draw(self):
    glPushMatrix()
    objects.Cube.draw(self)
    glPopMatrix()

  def setName(self, color):
    pass

class HumanPlayer(Player, objects.HumanInteractive):
  def __init__(self, world, position = (0.0, 0.0, 0.0)):
    objects.HumanInteractive.__init__(self)
    Player.__init__(self, world, position)
    
  def getAngle(self):
    #Human player is fixed in lower left square
    return pi/4

  def setName(self, color):
    return 'Player'

class AiPlayer(Player, objects.ComputerInteractive):
  def __init__(self, world, target, position = (0.0, 0.0, 0.0)):
    #init ComputerInteractive superclass
    objects.ComputerInteractive.__init__(self)
    #init Player superclass
    Player.__init__(self, world, position)
    self.target = target
    self.source = pyopenal.Source()
    self.world = world

  def setName(self, color):
    return 'Player_' + color

  def getAngle(self):
    #get angle from player position to the field center
    return vectormath.getAngleFromVector(self.initPos)   

  def getMovement(self):
    if self.source.get_state() != pyopenal.AL_PLAYING:
      if randint(0, 300)==0:
        msg = sound.sounds.playTaunt(self.source, self.body.getPosition())
        if msg!="": self.world.coach.addTaunt(self, msg)
    return objects.ComputerInteractive.getMovement(self)
