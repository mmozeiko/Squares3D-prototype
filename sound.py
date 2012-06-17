import pyopenal
from vectormath import multiply
from random import randint

soundOn = 1

taunts = [[r"DATA\TAUNTS\GE_%s_taunt_0%s.wav" % (j,i+1) for j in [0,3,4]] for i in range(7)] 
tauntsBuf = []
tauntsMsg = [
  "What's wrong, did you wet your pants?!",
  "Go to hell, you Russian bastards!",
  "Die, that makes it easier for both of us!",
  "Give up, we both know that you don't stand a chance!",
  "You yankees are weak and your president is lame!",
  "Die you yankee bastard!",
  "You fight like a bunch of girls!"
]

snd = {
  "AreYouCrazy" : r"DATA\TAUNTS\GE_AreYouCrazy.wav",
  "Fallback" : r"DATA\TAUNTS\GE_Fallback.wav",
  "FollowMe" : r"DATA\TAUNTS\GE_FollowMe.wav",
  "Granade" : r"DATA\TAUNTS\GE_Granade.wav",
  "GreatShot" : r"DATA\TAUNTS\GE_GreatShot.wav",
  "HoldPosition" : r"DATA\TAUNTS\GE_HoldPosition.wav",
  "InPosition" : r"DATA\TAUNTS\GE_InPosition.wav",
  "MoveIn" : r"DATA\TAUNTS\GE_MoveIn.wav",
  "No" : r"DATA\TAUNTS\GE_No.wav",
  "OnMyWay" : r"DATA\TAUNTS\GE_OnMyWay.wav",
  "Regroup" : r"DATA\TAUNTS\GE_Regroup.wav",
  "Sorry" : r"DATA\TAUNTS\GE_Sorry.wav",
  "SuppresingFire" : r"DATA\TAUNTS\GE_SuppresingFire.wav",
  "TookLongEnough" : r"DATA\TAUNTS\GE_TookLongEnough.wav",
  "Yes" : r"DATA\TAUNTS\GE_Yes.wav"
}
sndBuf = {}

def scaleDown(coords):
  #we scale down position coords to decrease "distance" effects
  return multiply(coords, 0.1) #by 10
   
class Source(pyopenal.Source):
  def __init__(self, buffer):
    pyopenal.Source.__init__(self)
    self.buffer = buffer
    self.position = (0.0, 0.0, 0.0)
    self.velocity = (0.0, 0.0, 0.0)

class Sounds:
  def __init__(self):
      pyopenal.init()
      self.l = pyopenal.Listener(22050)


      self.l.position = (0.0, 0.0, 0.0)
      self.l.at = (0.0, 0.0, 1.0)
      self.l.up = (0.0, 1.0, 0.0)

      self.buffers = {"BallPlayer":pyopenal.WaveBuffer("DATA\\SND\\ballplayer.wav"),
                      "BallGround":pyopenal.WaveBuffer("DATA\\SND\\ballground.wav"),
                      "Player":pyopenal.WaveBuffer("DATA\\SND\\playercollision.wav"),
                      "GameOver":pyopenal.WaveBuffer("DATA\\SND\\gameover.wav"),
                      "Menu":pyopenal.WaveBuffer("DATA\\SND\\menu.wav"),}

      for taunt in taunts:
        buf = []
        for t in taunt:
          buf.append(pyopenal.WaveBuffer(t))
        tauntsBuf.append(buf)
      for s in snd.keys():
        sndBuf[s] = pyopenal.WaveBuffer(snd[s])

      self.sources = {}
      for bName, buffer in self.buffers.items():
        self.sources[bName] = Source(buffer)

      
  def playSound(self, name, position):
    if soundOn:
      try:
        sound = self.sources[name]
        position = scaleDown(position)
        #we change signs because of the ankward world coordinate system
        sound.position = (-position[0], position[1], -position[2])
        sound.play()
      except:
        pass
    else:
      pass

  def setListenerPosition(self, position):
    try:
      position = scaleDown(position)
      #we change signs because of the ankward world coordinate system
      self.l.position = (-position[0], position[1], -position[2])
    except:
      pass

  def playTaunt(self, src, position):
    try:
      if soundOn:
        position = scaleDown(position)
        i = randint(0, len(taunts))
        src.buffer = tauntsBuf[i][randint(0, len(taunts[i]))]
        src.position = (-position[0], position[1], -position[2])
        src.play()
        return tauntsMsg[i]
      else:
        return ""
    except:
      return ""

  def playTauntMsg(self, src, msg, position):
    if soundOn:
      position = scaleDown(position)
      src.source.stop()
      src.source.buffer = sndBuf[msg]
      src.source.position = (-position[0], position[1], -position[2])
      src.source.play()

    

sounds = Sounds()
