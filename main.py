##import psyco
from OpenGL.GL import * 
from OpenGL.GLU import gluPerspective
import sys 
import objects
from pyglfw.glfw import *

from menu import GameMenu
from world import GameWorld
from ball import Ball
from players import HumanPlayer, AiPlayer
import gameglobals
import sound
import file

# new window size or exposure
def reshape(width, height):
  if 0 in [width, height]:
    return
  h = float(height) / float(width);
  glViewport(0, 0, width, height) 
  glMatrixMode(GL_PROJECTION) 
  glLoadIdentity() 
  #glFrustum(-1.0, 1.0, -h, h, 1.1, 100.0) 
  gluPerspective(45.0, 1.0/h, 0.1, 100.0)
  glMatrixMode(GL_MODELVIEW) 
  glLoadIdentity() 
  glTranslatef(0.0, 0.0, 0.0)

if __name__ == '__main__':
  #set configuration
  cfg = file.readCfg()
  res, vsync, soundOn, FULLSCREEN  = cfg["res"], cfg["vsync"], cfg["sound"], cfg["fullscreen"]

  sound.soundOn = soundOn

  WIDTH, HEIGHT = res[0], res[1]
  W, H = WIDTH, HEIGHT
  #store the scaling value for fonts
  gameglobals.fontScale = float(W) / 640 #640 is the smallest supported in game resolution

  #init glfw
  if not glfwInit():
    print "Failed to initialize glfw!"
    sys.exit()

  #create game window
  if not glfwOpenWindow(WIDTH, HEIGHT, 
                        8, 8, 8, 8, 24, 8, [GLFW_WINDOW, GLFW_FULLSCREEN][FULLSCREEN]):
    print "Failed to open %sx%sx32 %s!" % (WIDTH, HEIGHT, ["window", "video mode"][FULLSCREEN])
    sys.exit()
  glfwSetWindowTitle("3D game Squares")

  if FULLSCREEN:
    glfwDisable(GLFW_SYSTEM_KEYS)
  else:
    dm = glfwGetDesktopMode()
    glfwSetWindowPos((dm.Width-W)/2, (dm.Height-H)/2)

  glfwSetWindowSizeCb(reshape)

  #set the constants
  glfwSwapInterval(vsync)# - uncomment to disable VSync
  glfwDisable(GLFW_AUTO_POLL_EVENTS)
  glfwDisable(GLFW_KEY_REPEAT)
  glfwDisable(GLFW_MOUSE_CURSOR)

  glShadeModel(GL_SMOOTH)  
  glEnable(GL_CULL_FACE)
  glEnable(GL_LIGHT0)
  glEnable(GL_DEPTH_TEST)
  glEnable(GL_NORMALIZE)
  glEnable(GL_LIGHTING)

  #create the game world object
  gameWorld = GameWorld()
  #add ball to game world
  ball = Ball(gameWorld)
  gameWorld.addObject(ball)

  #add bounds to game world  
  gameWorld.addObject(objects.BoundingBox(gameWorld, 20, 20))
  gameWorld.addObject(objects.Field())

  #add players to game world
  player = HumanPlayer(gameWorld, (-5.0, 1.1, 5.0))
  player.camera = gameWorld.camera
  gameWorld.addObject(player)
  gameWorld.addObject(AiPlayer(gameWorld, ball.body, (-5.0, 1.1, -5.0)))
  gameWorld.addObject(AiPlayer(gameWorld, ball.body, (5.0, 1.1, -5.0)))
  gameWorld.addObject(AiPlayer(gameWorld, ball.body, (5.0, 1.1, 5.0)))

  glClearColor(0.5, 0.7, 0.9, 1.0)
  #create game menu object
  gameMenu = GameMenu()

  #add the background objects to menu
  gameMenu.addObject(objects.Field())
  gameMenu.addObject(objects.BoundingBox(gameMenu, 10.0, 10))
  crazyCubes = [objects.Cube(gameMenu, (-5.0, 1.001, -5.0), 200, (2.0, 2.0, 2.0), (1,1,0)),
                objects.Cube(gameMenu, (-5.0, 3.002, -5.0), 200, (2.0, 2.0, 2.0), (0,0,1)),
                objects.Cube(gameMenu, (-5.0, 5.003, -5.0), 200, (2.0, 2.0, 2.0), (1,0,0)),
                objects.Cube(gameMenu, (-5.0, 7.004, -5.0), 200, (2.0, 2.0, 2.0), (0,1,0))]

  for cube in crazyCubes: gameMenu.addObject(cube)
  crazyBall = objects.Sphere(gameMenu, (-4,4,4), 200, 2.0, (0,0,1))
  crazyBall.body.addForce((5515, 3515, -454451))
  gameMenu.addObject(crazyBall)
  gameMenu.camera.setTarget(crazyBall)

  #set the mouse to center of screen
  glfwSetMousePos(WIDTH/2, HEIGHT/2)

  #game menu and world list
  state = [gameMenu, gameWorld] 

  #gameglobals.gameState: 0 - main menu, 1 - game, 2 - options, 3 - quit
  gameMenu.launchClock()
  previousState = gameglobals.gameState
  
  while True:
    glfwPollEvents()
    if (not glfwGetWindowParam(GLFW_OPENED)) or (gameglobals.gameState == 3):
      break
    if gameglobals.gameState == 2: #world, but needs restart
      gameglobals.gameState = 1 #back into game
      state[gameglobals.gameState].coach.restart() #null the game result
    if previousState != gameglobals.gameState:
      #if the state has changed, we start the clock again
      state[gameglobals.gameState].launchClock()
    previousState = gameglobals.gameState
    state[gameglobals.gameState].idle() #call the idle method of the active object

  glfwCloseWindow()
  glfwTerminate()
