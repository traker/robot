"""
Webcam Streamer

Uses Pygame and HTTPServer to stream USB Camera images via HTTP (Webcam)

HTTP Port, camera resolutions and framerate are hardcoded to keep it
simple but the program can be updated to take options.

Default HTTP Port 8080, 320x240 resolution and 6 frames per second.
Point your browser at http://localhost:8080/

http://www.madox.net/
"""

import signal
import sys
import tempfile
import threading
import time

import BaseHTTPServer
import SocketServer

class HTTPServer( SocketServer.ThreadingMixIn,
                 BaseHTTPServer.HTTPServer ):
  def __init__( self, server_address, bot ):
    SocketServer.TCPServer.__init__( self, server_address, HTTPHandler )

class HTTPHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
  """
  HTTP Request Handler
  """
  def do_GET( self ):
    if self.path == "/":
      response = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title>Webcam Streamer</title>
</head>
<body onload="get_new_image();">Select a streaming option below :<br>
<a href="/GetStream">Multipart:
Preferred for fast connections, supported by most browsers.</a><br>
</body>
</html>
"""
      self.send_response( 200 )
      self.send_header( "Content-Length", str( len( response ) ) )
      self.send_header( "Cache-Control", "no-store" )
      self.end_headers()
      self.wfile.write( response )

    elif self.path[:9] == "/JSStream":
      #HTML with Javascript streaming for browsers that don't support
      #multipart jpeg (Android!!!)
      response = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title>Webcam Stream (Javascript)</title>
<script type="text/javascript">
function get_new_image(){
  var img = new Image();
  var d = new Date();
  img.style.zIndex = 0;
  img.style.position = "absolute";
  img.onload = got_new_image;
  //Generate unique URL to bypass caching on mobile browsers that ignore
  //cache-control
  img.src = "/GetImage&n=" + d.getTime(); 
  var webcam = document.getElementById("images");
  webcam.insertBefore(img, webcam.firstChild);
}

function got_new_image() {
  var d = new Date();
  this.style.zIndex = d.getTime()
  //Kill the earlier siblings (previous images)
  while(this.parentNode.childNodes[1]) {
    this.parentNode.removeChild(this.parentNode.childNodes[1]);
  }
  get_new_image();
}
</script>
</head>
<body onload="get_new_image();">
<div id="images"></div>
</body>
</html>
"""
      self.send_response( 200 )
      self.send_header( "Content-Length", str( len( response ) ) )
      self.send_header( "Cache-Control", "no-store" )
      self.end_headers()
      self.wfile.write( response )

    elif self.path[:10] == "/GetStream":
      #Boundary is an arbitrary string that should not occur in the
      #data stream, using own website address here
      boundary = "www.madox.net"
      self.send_response( 200 )
      self.send_header( "Access-Control-Allow-Origin", "*" )
      self.send_header( "Content-type",
                       "multipart/x-mixed-replace;boundary=%s"
                       % boundary )
      self.end_headers()


      while True:
        response = "Content-type: image/jpeg\n\n"
        response = response + self.server.bot.get_laplace_image()
        response = response + "\n--%s\n" % boundary
        self.wfile.write( response )

    elif self.path[:9] == "/GetImage":
      response = self.server.bot.get_laplace_image()
      self.send_response( 200 )
      self.send_header( "Content-Length", str( len( response ) ) )
      self.send_header( "Content-Type", "image/jpeg" )
      self.send_header( "Content-Disposition",
                       "attachment;filename=\"snapshot.jpg\"" )
      self.send_header( "Cache-Control", "no-store" )
      self.end_headers()
      self.wfile.write( response )

    else:
      self.send_error( 404, "Banana Not Found." )
      self.end_headers()

  do_HEAD = do_POST = do_GET
