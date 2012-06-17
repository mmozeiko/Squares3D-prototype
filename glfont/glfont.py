from struct import unpack
from OpenGL.GL import *
from OpenGL.GLU import gluOrtho2D
              
class GLFont:
  """class GLFont
  usage example:

    # setup
    font = GLFont("my_font.glf")

    # rendering
    font.begin()
    glColorf(1.0, 0.0, 0.0)
    font.render("blabla\nThis is Second line!", 100.0, 100.0) # red text
    glColorf(0.0, 0.0, 1.0)
    font.renderShadowed("Another text!", 50.0, 400.0, (1.0, 1.0, 1.0)) # blue text with white shadow
    font.end()
    
  """
  def __init__(self, fileName, mode=GL_LINEAR): # or mode=GL_NEAREST
    """__init__(fileName, mode=GL_LINEAR
    Initializes GLFont from font in fileName file.
    mode sets speed (GL_NEAREST) or nicer look (GL_LINEAR)
    """
    f = file(fileName, "rb")

    f.seek(4, 1)
    self.tex        = glGenTextures(1)

    self.tex_width  = self._readInt(f)
    self.tex_height = self._readInt(f)
    self.start_char = self._readInt(f)
    self.end_char   = self._readInt(f)
    f.seek(4, 1)

    self.num_chars = self.end_char-self.start_char+1
    self.list_base = glGenLists(self.end_char+1)

    self.chars = [
      dict( (key,self._readFloat(f)) 
        for key in ["dx","dy","tx1","ty1","tx2","ty2"] )
      for idx in range(self.num_chars)
    ]

    tex_bytes = f.read(self.tex_width*self.tex_height*2)
    f.close()

    glBindTexture(GL_TEXTURE_2D, self.tex)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mode)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, mode)
    glTexImage2D(GL_TEXTURE_2D, 0, 2, self.tex_width, self.tex_height, 0, 
      GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE, tex_bytes)

    for ch in range(self.start_char, self.end_char+1):
      glNewList(self.list_base + ch, GL_COMPILE)

      glfont_char = self.chars[ch-self.start_char]

      w = glfont_char["dx"] * self.tex_width

      if ch!=32:
        h = glfont_char["dy"] * self.tex_height
        glPushMatrix()
        glBegin(GL_QUADS)
        glTexCoord2f(glfont_char["tx1"], glfont_char["ty1"]), glVertex2f(0,  0)
        glTexCoord2f(glfont_char["tx1"], glfont_char["ty2"]), glVertex2f(0, -h)
        glTexCoord2f(glfont_char["tx2"], glfont_char["ty2"]), glVertex2f(w, -h)
        glTexCoord2f(glfont_char["tx2"], glfont_char["ty1"]), glVertex2f(w,  0)
        glEnd()
        glPopMatrix()

      glTranslatef(w, 0.0, 0.0)

      glEndList()

  def __del__(self):
    try:
      glDeleteLists(self.list_base, self.end_char+1)
      glDeleteTextures(self.tex)
    except:
      pass

  def _readInt(self, f):
    return unpack("i", f.read(4))[0]

  def _readFloat(self, f):
    return unpack("f", f.read(4))[0]
                    
  def begin(self):
    """begin()
    Call when you want to render text. This sets orthogonal projection,
    font texture, and some other msic attributes. All OpenGL states are
    restored in end() call.
    """
    glBindTexture(GL_TEXTURE_2D, self.tex)

    glPushAttrib(GL_TRANSFORM_BIT)
    viewport = glGetIntegerv(GL_VIEWPORT)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(viewport[0], viewport[2], viewport[1], viewport[3])
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glPushAttrib(GL_LIST_BIT | GL_CURRENT_BIT  | GL_ENABLE_BIT | GL_TRANSFORM_BIT | GL_TEXTURE_BIT)
    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glDepthFunc(GL_NEVER)

  def end(self):
    """end()
    Call when you are done with text rendering. This restores all saved state
    in begin() call.
    """
    glPopAttrib()

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glPopAttrib()
    glDepthFunc(GL_LESS)

  def getSize(self, text):
    """size(text) -> (width, height)
    Returns text width and height in pixels.
    """
    height = self.chars[0]["dy"]
    widths = [
      self.chars[ord(c)-self.start_char]["dx"] 
        for c in text 
          if self.start_char<=ord(c)<=self.end_char
    ]
    return sum(widths)*self.tex_width, height*self.tex_height

  def render(self, text, x, y, scale = 1.0):
    """render(text, x, y)
    Renders text on screen starting at positions x and y (both in pixels).
    0,0 point is at lower left corner of screen. text can contain newlines.
    """
    glListBase(self.list_base)

    h = self.chars[0]["dy"]*self.tex_height * scale
    for i, line in enumerate(text.split("\n")):
      glPushMatrix()

      glTranslatef(x, y-h*i, 0.0);

      glBegin(GL_QUADS);
##      glNormal3f( 0.0,  0.0, 1.0)
      L = 10
      glVertex3f(-L, -L, 0)
      glVertex3f( L, -L, 0)
      glVertex3f( L,  L, 0)
      glVertex3f(-L,  L, 0)
      glEnd()
      
      glScalef(scale, scale, 0.0)
      
      #for c in line: glCallList(self.list_base + ord(c))
      glCallLists(line)
      glPopMatrix()

  def renderShadowed(self, text, x, y, shadowColor=(1.0, 1.0, 1.0), scale = 1.0):
    """renderShadowed(text, x, y, color, shadow, shadowColor)
    Renders text on screen starting at positions x and y (both in pixels).
    0,0 point is at lower left corner of screen. text can contain newlines.
    """
    color = glGetFloatv(GL_CURRENT_COLOR)

    glColor3fv(shadowColor)
    self.render(text, x+1.0, y-1.0, scale)

    glColor4fv(color)
    self.render(text, x, y, scale)

  def renderOutlined(self, text, x, y, outlineColor=(1.0, 1.0, 1.0), scale = 1.0):
    """renderShadowed(text, x, y, color, shadow, shadowColor)
    Renders text on screen starting at positions x and y (both in pixels).
    0,0 point is at lower left corner of screen. text can contain newlines.
    """
    color = glGetFloatv(GL_CURRENT_COLOR)

    glColor3fv(outlineColor)
    self.render(text, x+1.5, y-1.5, scale)
    self.render(text, x-1.5, y+1.5, scale)

    glColor4fv(color)
    self.render(text, x, y, scale)
    
