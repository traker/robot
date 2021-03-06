#edited by Norbert (mjpeg part) from a file from Copyright Jon Berg , turtlemeat.com,
#MJPEG Server for the webcam
import string, cgi, time
from os import curdir, sep
import BaseHTTPServer
import SocketServer
import cv
import re

cameraQuality = 75
#===============================================================================
# MyHandler
#===============================================================================
class MyHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    def do_GET( self ):
        global cameraQuality
        try:
            self.path = re.sub( '[^.a-zA-Z0-9]', "", str( self.path ) )
            if self.path == "" or self.path == None or self.path[:1] == ".":
                return
            if self.path.endswith( ".html" ):
                f = open( curdir + sep + self.path )
                self.send_response( 200 )
                self.send_header( 'Content-type', 'text/html' )
                self.end_headers()
                self.wfile.write( f.read() )
                f.close()
                return
            if self.path.endswith( ".mjpeg" ):
                self.send_response( 200 )
                self.wfile.write( "Content-Type: multipart/x-mixed-replace; boundary=--aaboundary" )
                self.wfile.write( "\r\n\r\n" )
                while 1:
                    img = self.server.imgl.image_actuel
                    cv2mat = cv.EncodeImage( ".jpeg", img, ( cv.CV_IMWRITE_JPEG_QUALITY, cameraQuality ) )
                    JpegData = cv2mat.tostring()
                    self.wfile.write( "--aaboundary\r\n" )
                    self.wfile.write( "Content-Type: image/jpeg\r\n" )
                    self.wfile.write( "Content-length: " + str( len( JpegData ) ) + "\r\n\r\n" )
                    self.wfile.write( JpegData )
                    self.wfile.write( "\r\n\r\n\r\n" )
                    time.sleep( 0.05 )
                return
            if self.path.endswith( ".jpeg" ):
                f = open( curdir + sep + self.path )
                self.send_response( 200 )
                self.send_header( 'Content-type', 'image/jpeg' )
                self.end_headers()
                self.wfile.write( f.read() )
                f.close()
                return
            return
        except IOError:
            self.send_error( 404, 'File Not Found: %s' % self.path )
    def do_POST( self ):
        global rootnode, cameraQuality
        try:
            ctype, pdict = cgi.parse_header( self.headers.getheader( 'content-type' ) )
            if ctype == 'multipart/form-data':
                query = cgi.parse_multipart( self.rfile, pdict )
            self.send_response( 301 )

            self.end_headers()
            upfilecontent = query.get( 'upfile' )
            print "filecontent", upfilecontent[0]
            value = int( upfilecontent[0] )
            cameraQuality = max( 2, min( 99, value ) )
            self.wfile.write( "<HTML>POST OK. Camera Set to<BR><BR>" );
            self.wfile.write( str( cameraQuality ) );

        except :
            pass

#===============================================================================
# HTTPServer
#===============================================================================
class HTTPServer( SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer ):
    """Handle requests in a separate thread."""
    def __init__( self, server_address, img ):
        SocketServer.TCPServer.__init__( self, server_address, MyHandler )
        self.imgl = img

