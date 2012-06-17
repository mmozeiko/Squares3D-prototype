#read config file and return values

#available options
res = {"512":[512, 384],
       "640":[640, 480],
       "800":[800, 600],
       "1024":[1024, 768],
       "1280":[1280, 1024]}
vsync = [0, 1]
sound = [0, 1]
fullscreen = [0, 1]

readSequence = [{"res":res}, {"vsync":vsync}, {"sound":sound}, {"fullscreen":fullscreen}]

#default options
default = {"res":res["640"],
           "vsync":vsync[1],
           "sound":sound[1],
           "fullscreen":fullscreen[1]}

def readCfg():
  path = "DATA\\config.cfg"
  try:
    cfgFile = file("DATA\\config.cfg", "r")
    line = cfgFile.readline()
    while line[0] == '#':
      line = cfgFile.readline()
    cfgFile.close()
    options = line.split(" ")[:4]
    options = [option.strip("\n") for option in options]
    current = default
    for val in res.values():
      if int(options[0]) == val[0]:
        current.update({"res":res[options[0]]})
        break
    if int(options[1]) in vsync: current.update({"vsync":int(options[1])})
    if int(options[2]) in sound: current.update({"sound":int(options[2])})
    if int(options[3]) in fullscreen: current.update({"fullscreen":int(options[3])})
    return current
  except Exception, e:
    print "unable to parse file " + path
    print e
    return default


