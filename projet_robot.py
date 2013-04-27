"""
robot 0.1

composant, capteur, etc ...

2 servo a rotation continue pour la propultion , 1 servo gauche et un droit.
2 servo de commande tourelle 
1 webcam
1 emeteur laser
1 accelerometre 
1 carte wifi
1 carte ArduinoMega
1 carte chumby hacker board

assemblage

les servos sont branche sur la carte arduino ils ont une alimentation externe.
motG = pwm pin 2
motD = pwm pin 3
tourR = pwm pin 4
tourHB = pwm pin 5

webcam, wifi et arduino sur la chumby .

accelerometre integre a chumby 

but du robot.

le robot explore son environement et evolue a travers.
il se cree une carte qu il remplit au fur et a mesure de son exploration.

a l aide de la webcam et du laser il evalue la distance des obstacle 
"""
import pyfirmata, cv, numpy
import pygame.camera as camera
from pygame.locals import *
import pygame.image
import time
from math import *

BETA = 89.762#86.49#70.568#Laser angle [degrees]
L = 6.43#Distance from focus to laser [cm]
# Estimate of radians from center.
#rfc: 0.001068
# Radian offset (accounts for error in rfc).
#ro: -0.031859
angle_vue_rot = numpy.arange( 45, 135, 10 )
#angle_vue_rot.fill(90)
angle_vue_HB = numpy.arange( 75, 105, 3 )

pin_motG = 2
pin_motD = 3
pin_tourR = 4
pin_tourHB = 5
pin_lazer = 52

nby = 192
nbx = 220
# This should be the size of the image coming from the camera.
cam_width = 320
cam_height = 240
camsize = ( cam_width, cam_height )
# HSV color space Threshold values for a RED laser pointer. If the dot from the
# laser pointer doesn't fall within these values, it will be ignored.
ang_actu_rotx = 90
ang_actu_roty = 90

# value
vmin = 220
vmax = 250

#initialise la camera
camera.init()
cam = camera.Camera( "/dev/video0", ( cam_width, cam_height ), "RGB" )
snapshot = pygame.surface.Surface( camsize )
cam.start()
print "chargement webcam"
while not cam.query_image():
	print "chargement webcam"
	time.sleep( 0.5 )
snapshot = cam.get_image( snapshot )

# set up the arduino
board = pyfirmata.ArduinoMega( "/dev/ttyACM0" )
print "Setting up Arduino..."
time.sleep( 0.5 )
it = pyfirmata.util.Iterator( board )
it.start()

#initialise les servos
board.servo_config( pin_motG, angle=90 )
board.servo_config( pin_motD, angle=90 )
board.servo_config( pin_tourR, angle=90 )
board.servo_config( pin_tourHB, angle=90 )
motG = board.digital[pin_motG]
motD = board.digital[pin_motD]
tourVe = board.digital[pin_tourHB]
tourRot = board.digital[pin_tourR]
laser = board.get_pin( 'd:' + str( pin_lazer ) + ':o' )
tourVe.write( ang_actu_roty )
tourRot.write( ang_actu_rotx )

# set laser True = on
def set_laser( _bool_ ):
    """Allume/eteint le Laser"""
    #chb.write('D0',_bool_)
    laser.write( _bool_ )
    return _bool_

def surface_to_string( surface ):
    """Convert a pygame surface into string"""
    return pygame.image.tostring( surface, 'RGB' )


def pygame_to_cvimage( surface ):
    """Convert a pygame surface into a cv image"""
    cv_image = cv.CreateImageHeader( surface.get_size(), cv.IPL_DEPTH_8U, 3 )
    image_string = surface_to_string( surface )
    cv.SetData( cv_image, image_string )
    return cv_image

def cvimage_to_pygame( image ):
    """Convert cvimage into a pygame image"""
    #image_rgb = cv.CreateMat(image.height, image.width, cv.CV_8UC3)
    #cv.CvtColor(image, image_rgb, cv.CV_BGR2RGB)
    return pygame.image.frombuffer( image.tostring(), cv.GetSize( image ), "P" )

def cvimage_grayscale( cv_image ):
    """Converts a cvimage into grayscale"""
    grayscale = cv.CreateImage( cv.GetSize( cv_image ), 8, 1 )
    cv.CvtColor( cv_image, grayscale, cv.CV_RGB2GRAY )
    return grayscale

def captur_im( _bool_ ):
    global snapshot
    if cam.query_image():
        set_laser( _bool_ )
        time.sleep( 0.1 )
        snapshot = cam.get_image( snapshot )
        ocvimg = pygame_to_cvimage( snapshot )
        time.sleep( 0.1 )
        set_laser( 0 )
        return ocvimg
    else:
        return None

def img_filter( im ):
    dilatedimg = cv.CloneImage( im )
    cv.Dilate( im, dilatedimg )
    blurim = cv.CloneImage( dilatedimg )
    #cv.Smooth(dilatedimg, blurim,cv.CV_GAUSSIAN, 5, 5)
    bitimage = cv.CreateImage( cv.GetSize( im ), cv.IPL_DEPTH_8U, 1 )
    imgg = cv.CreateImage( cv.GetSize( im ), cv.IPL_DEPTH_8U, 1 )
    cv.CvtColor( blurim, imgg, cv.CV_RGB2GRAY )
    cv.Threshold( imgg, bitimage, vmin, vmax, cv.CV_THRESH_BINARY )
    return bitimage

def find_centroid_faster_numpy( arr, rez ):
        #arr_rez = arr[::rez,::rez]
        global nby, nbx
        listf = ( ( 144, 128 ), ( 128, 96 ), ( 96, 48 ), ( 64, 48 ), ( 48, 24 ), ( 24, 0 ) )
        nby = 192
        nbx = 220
        point = []
        for n in listf:
            arr_rez = arr[136:184:rez, n[1]:n[0]:rez]
            testcarr = numpy.sum( arr_rez )
            if testcarr < ( 10 * vmax ):
                #print "pas assez de lumiere "+str(n)
                point = 0.0, 0.0, 0
            elif testcarr > ( 300 * vmax ):
                #print "trop de lumiere "+str(n)+" "+str(testcarr)
                point = 0.0, 0.0, 2
            else:
                point = 0.0, 0.0, 1
                nby = n[1]
                nbx = n[0]
                print "point trouve " + str( n )
                break
        if point[2] == 1:
            #ygrid, xgrid  = numpy.mgrid[0:cam_width:rez, 0:cam_height:rez]
            ygrid, xgrid = numpy.mgrid[136:184:rez, nby:nbx:rez]
            xcen, ycen = xgrid[arr_rez == vmax].mean(), ygrid[arr_rez == vmax].mean()
            try:
                return ycen, xcen, 1
            except ValueError:
                return 0.0, 0.0, 0.0
        print "point non trouve "
        # return y, x, etat de recherche
        return point

def depl_tour( vert, hori ):
    global ang_actu_rotx, ang_actu_roty
    flag_x = 0
    flag_y = 0
    index = 0

    if hori <= ang_actu_rotx: flag_x = 0
    else: flag_x = 1
    if vert <= ang_actu_roty: flag_y = 0
    else: flag_y = 1

    waitrottmp = ang_actu_rotx - hori
    waithbtmp = ang_actu_roty - vert
    diffrot = abs( waitrottmp )
    diffhb = abs( waithbtmp )

    arrx = numpy.array( [] )
    arry = numpy.array( [] )

    if diffrot >= diffhb:
        if ang_actu_rotx == hori :
            print "egal"
            arrx = numpy.array( [hori] )
        elif flag_x == 1 :
            arrx = numpy.arange( ang_actu_rotx, hori )
        else:
            arrx = numpy.arange( hori, ang_actu_rotx )
            arrx = arrx[::-1]

        ratio = float( diffhb ) / float( arrx.size )
        index = arrx.size - 1
        if ang_actu_roty == vert :
            arry = numpy.arange( arrx.size )
            arry.fill( vert )
        elif flag_y == 1 :
            arry = numpy.arange( ang_actu_roty, vert, ratio )
        else:
            arry = numpy.arange( vert, ang_actu_roty, ratio )
            arry = arry[::-1]
    else:
        if ang_actu_roty == vert :
            arry = numpy.array( [vert] )
        elif flag_y == 1 :
            arry = numpy.arange( ang_actu_roty, vert )
        else:
            arry = numpy.arange( vert, ang_actu_roty )
            arry = arry[::-1]

        ratio = float( diffrot ) / float( arry.size )
        index = arry.size - 1
        if ang_actu_rotx == hori :
            arrx = numpy.arange( arry.size )
            arrx.fill( hori )
        elif flag_x == 1 :
            arrx = numpy.arange( ang_actu_rotx, hori, ratio )
        else:
            arrx = numpy.arange( hori, ang_actu_rotx, ratio )
            arrx = arrx[::-1]

    for n in range( index ):
            tourRot.write( arrx[n] )
            tourVe.write( arry[n] )
            time.sleep( 0.002 )
    ang_actu_rotx = hori
    ang_actu_roty = vert

def scan_pos_las( verti, horizo ):
    depl_tour( verti, horizo )
    print "deplacement y:" + str( verti ) + " x:" + str( horizo )
    captur_im( 1 )
    imavlaser = captur_im( 1 )
    imfil = img_filter( imavlaser )
    matpy = pygame.surfarray.array2d( cvimage_to_pygame( imfil ) )
    matr = numpy.asarray( matpy )
    temppoint = find_centroid_faster_numpy( matr, 1 )
    point = temppoint[0], temppoint[1]
    cv.Circle( imavlaser, point, 4, cv.RGB( 255, 0, 0 ) )
    cv.Circle( imavlaser, ( 160, 120 ), 1, cv.RGB( 0, 255, 0 ) )
    cv.Rectangle( imavlaser, ( 136, nby ), ( 184, nbx ), cv.RGB( 0, 255, 0 ) )
    print "le laser se trouve x:" + str( point[1] ) + ", y:" + str( point[0] )
    #return image, y, x
    return imfil, point
"""
try:
    tourRot.write(angle_vue_rot[0])
    time.sleep(0.2)
    captur_im(1)
    captur_im(1)
    tourVe.write(88)
    listim = []
"""

def camera_corrected_fx( posX ):
    return 351.123#1456.138

def calculate_distance( vc, beta, L ):
    #print "vc:"+str(vc)
    #print "beta:"+str(beta)
    #print "L:"+str(L)
    #print "CW:"+str(cam_height)
    vx = vc - ( cam_height / 2.0 )
    if vx == 0:
        vx = 0.0001 #a sort of laplacian smoothing
    #print "vx:"+str(vx)

    delta = atan( camera_corrected_fx( vc ) / abs( vx ) )
    if vx > 0:
        delta = pi - delta
    #print "delta:"+str(delta)
    lambd = pi - radians( beta ) - delta
    #print "lambda:"+str(lambd)
    Dc = L * sin( radians( beta ) ) / sin( lambd )
    print "Dc:" + str( Dc )
    return Dc

i = 0
tmp = scan_pos_las( 100, 90 )
for x in angle_vue_rot:
    imgt, pointt = scan_pos_las( 90, x )
    dst = calculate_distance( pointt[1], BETA, L )
    cv.SaveImage( "img" + str( i ) + ".jpg", imgt )
    i = i + 1

"""      
except Exception, e:
    raise

j = 0
try:
    for n in listim:
        testim = img_filter(n)
        test = pygame.surfarray.array2d(cvimage_to_pygame(testim))
        matr = numpy.asarray(test)
        point = find_centroid_faster_numpy(matr, 1)
        print point, j
        cv.Circle(n,(point[0],point[1]),4, cv.RGB(255, 0, 0))
        cv.Circle(n,(160,120),1, cv.RGB(0, 255, 0))
        cv.Rectangle(n, (136,65),(184,200), cv.RGB(0, 255, 0))
        cv.SaveImage("img"+str(j)+".jpg", n)
        j = j + 1
except Exception, e:
    raise
imgt, pointt = scan_pos_las(100, 45)
imgt0, pointt = scan_pos_las(80, 75)
imgt1, pointt = scan_pos_las(100, 90)
imgt0, pointt = scan_pos_las(80, 115)
imgt1, pointt = scan_pos_las(100, 135)
imgt2, pointt = scan_pos_las(80, 90)
cv.SaveImage("img.jpg", imgt)
cv.SaveImage("img0.jpg", imgt0)
cv.SaveImage("img1.jpg", imgt1)
cv.SaveImage("img2.jpg", imgt2)
"""
cam.stop()
camera.quit()
board.exit()

exit()
