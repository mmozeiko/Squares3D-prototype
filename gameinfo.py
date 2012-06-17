#Various information of the game

version = "v0.51"

rules = """Rules of the game:
 
  The player with most points loses the game (pointlimit is 21).
The points are incremented with each additional hit of the ball
while in the air (the ball must not hit the ground, otherwise,
the point counting is restarted). These are called "combo" points.
  Faults:
    * The ball hits the ground outside field:
      - if the last thing the ball touched is one of the players,
        the player gets as many points as he has hit the ball,
        while it was in the air (only own points before fault
        are counted)
      - the player who owns the square from which the ball left
        the field gets the gathered "combo" points from all players
        summed together
      - if the ball has left the field from one of the middle lines
        (lines between players squares), the game is continued with
        the drop of the ball in field center.
    * Player has touched the ball second time in his square (you may
      not touch the ball second time in your square of field, if it
      has touched the ground in your square after your first touch).
  In case of the fault, the game is continued with the drop of the
ball in center of the players square who got the fault."""

developer = "Kristaps Straupe, 2006"

controls = """Game controls:
 
Use your mouse to move the player around and kick the ball.
Press mouse button 1 to make the player jump.
Hold down mouse button 2 and move the mouse to make the player rotate."""

about = """Developed by Kristaps Straupe, 2006.
Project leader Atis Straujums."""

credits = """Credits:
 
Thanks to Atis Straujums, you`ve been a great leader!
Special thanks to colleague Martins Mozeiko,
 - without your help, knowledge and advice it would have been so much harder.."""

info = """3D game Squares is developed using following technologies:
 
  ODE       - Open Dynamics Engine
  OpenGL - Open Graphics Library
  OpenAL - Open Audio Library
  GLFW    - OpenGL FrameWork
  Powered by Python"""