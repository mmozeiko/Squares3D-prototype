from math import sqrt, asin, acos, atan2, pi
from OpenGL.GL import * 

def isPointInSquare(point, squareMin, squareMax):
  if point[0] >= squareMin[0] and point[0] <= squareMax[0]\
     and point[2] >= squareMin[1] and point[2] <= squareMax[1]:
    return True
  return False

def getBallAndSquareIntersection(position, velocity, min, max):
  adjust = 1.0 #how far can we exceed own square border

  min0 = min[0]
  min1 = min[1]
  max0 = max[0]
  max1 = max[1]

##  min0 = max0 / 10 * adjust
##  min1 = max1 / 10 * adjust
##  max0 = min0 / 10 * adjust
##  max1 = min1 / 10 * adjust
  
  t = position[2] / (velocity[2] + 1e-06)
  if t >= 0:
    x = position[0] + velocity[0] * t
    if x > min0 and x < max0:
      return (x, 0.0, 0.0)
  t = position[0] / (velocity[0] + 1e-06)
  if t >= 0:
    y = position[2] + velocity[2] * t
    if y > min1 and y < max1:
      return (0.0, 0.0, y)
  return ((max[0] + min[0])/2, 0.0, (max[1] + min[1])/2)

def negate(v):
  return (-v[0], -v[1], -v[2])

def extractMatrix(geom):
  x, y, z = geom.getPosition()
  rot = geom.getRotation()
  return (rot[0], rot[3], rot[6], 0.0,
          rot[1], rot[4], rot[7], 0.0,
          rot[2], rot[5], rot[8], 0.0,
          x,      y,      z,      1.0)

def rotationMatrix(angle, x, y, z):
  glPushMatrix()
  glLoadIdentity()
  glRotated(angle, x, y, z)
  m = glGetFloatv(GL_MODELVIEW_MATRIX)
  glPopMatrix()
  return (m[0][0], m[0][1], m[0][2], 
          m[1][0], m[1][1], m[1][2],
          m[2][0], m[2][1], m[2][2])

def getVector(v0, v1):
  x = v1[0] - v0[0]
  y = v1[1] - v0[1]
  z = v1[2] - v0[2]
  return (x, y, z)
  
def getMagnitude(x, y, z):
  return sqrt(x * x + y * y + z * z)

def getMagnitudeV(V):
  return getMagnitude(V[0], V[1], V[2])

def normalize(x, y, z):
  #magnitude = getMagnitude(x, y, z)
  magnitude = sqrt(x * x + y * y + z * z + 1e-06)
  if magnitude != 0:
    x /= magnitude
    y /= magnitude
    z /= magnitude
  else:
    raise Exception, 'division by zero'
  return (x, y, z)

def normalizeV(v):
  return normalize(v[0], v[1], v[2])

def multiply(v, nr):
  return (v[0] * nr, v[1] * nr, v[2] * nr)

def getCrossProduct(v0, v1):
  x = v0[1] * v1[2] - v0[2] * v1[1]
  y = v0[2] * v1[0] - v0[0] * v1[2]
  z = v0[0] * v1[1] - v0[1] * v1[0]
  return (x, y, x)

def getDotProduct(v0, v1):
  return v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2]

def pseudoScalarMulXY(v0, v1):
  return v0[0] * v1[2] - v0[2] * v1[0]

def getAngleBetweenVectors(v0, v1):
  asinAngle = pseudoScalarMulXY(v0, v1)
  acosAngle = getDotProduct(v0, v1)
  #return atan2(asinAngle, acosAngle)
  return atan2(acosAngle, asinAngle) + pi/2

def getAngleFromVector(v):
  return atan2(v[2], v[0])-pi/2

