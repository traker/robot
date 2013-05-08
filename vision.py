import pygame.camera as camera
import pygame.surface as surface
import cv, ConfigParser, time
import pygame.image as pymage
import pygame.surfarray as surfarray
import pygame.transform as transform
import numpy
from math import *

class Vision():
	'''
		class permetant de traiter differente information sur la vision du robot
	'''
	#cam = Camera(ConfigParser objet)
	def __init__( self, config, board ):
		'''
		@param board: objet pyfirmata
		@type board: pyfirmata
		@param config: objet configparser contenant les configurations du robot
		@type config: configparser.RawConfigParser
		'''
		self.timexe = 0
		self.cam_width = config.getint( 'Camera', 'width' ) #largeur camera
		self.cam_height = config.getint( 'Camera', 'height' ) #hauteur camera
		self.device = config.get( 'Camera', 'device' ) # lien vers la webcam 
		self.size = ( self.cam_width, self.cam_height ) # tuple (largeur, hauteur)
		self.bitimage = cv.CreateImage( self.size, 8, 1 ) # image noir et blanc
		self.matriximg = None
		self.laplaceim = cv.CreateImage( self.size, cv.IPL_DEPTH_8U, 1 )
		self.image_actuel = cv.CreateImage( self.size, cv.IPL_DEPTH_8U, 1 )
		self.image_brut = cv.CreateImageHeader( self.size, 8, 3 ) #image capture
		self.snapshot = surface.Surface( self.size )	# tampon image
		self.vmin = config.getint( 'Camera', 'tresholdmin' ) #valeur minimum treshold
		self.vmax = config.getint( 'Camera', 'tresholdmax' ) #valeur maximum treshold
		camera.init()
		self.cam = camera.Camera( self.device, self.size, "RGB" )
		self.cam.start()
		print "chargement webcam"
		while not self.cam.query_image():
			print "chargement webcam"
			time.sleep( 0.5 )
		self.snapshot = self.cam.get_image( self.snapshot )
		# configuration pour le lrf
		self.laser_pin = config.getint( 'Lrf', 'pin_laser' )
		self.laser = board.get_pin( 'd:' + str( self.laser_pin ) + ':o' )
		self.laser_pos = False
		self.listplage = ( ( 144, 128 ), ( 128, 96 ), ( 96, 48 ), ( 64, 48 ), ( 48, 24 ), ( 24, 0 ) )
		self.plage_rech = ( 0, 0 ) #nby, nbx
		self.point = []
		self.BETA = config.getfloat( 'Lrf', 'beta' )
		self.L = config.getfloat( 'Lrf', 'lfocus' )

	def __surface_to_string__( self, surface ):
		'''
			Converti une Surface pygame en String
		@param surface: surface pygame
		@type surface: pygame.Surface
		'''
		return pymage.tostring( surface, 'RGB' )

	def __pygame_to_cvimage__( self, surface ):
		'''
			Converti une Surface pygame au format opencv
		@param surface: surface pygame
		@type surface: pygame.Surface
		'''
		cv_image = cv.CreateImageHeader( surface.get_size(), 8, 3 )
		image_string = self.__surface_to_string__( surface )
		cv.SetData( cv_image, image_string )
		return cv_image

	def __cvimage_to_pygame__( self, image ):
		'''
			converti une image opencv en surface pygame 1 canal gris
		@param image: image opencv
		@type image: IPLimage
		@return: gray Surface image pygame
		@rtype: pygame.Surface
	 	
		'''
		#image_rgb = cv.CreateMat(image.height, image.width, cv.CV_8UC3)
		#cv.CvtColor(image, image_rgb, cv.CV_BGR2RGB)
		return pymage.frombuffer( image.tostring(), cv.GetSize( image ), "P" )

	def __capture_im__( self ):
		'''
			capture une image et la stocke dans self.image_brut
		'''
		if ( time.time() - self.timexe ) > 0.2:
			if self.cam.query_image():
				self.snapshot = self.cam.get_image( self.snapshot )
				self.snapshot = self.cam.get_image( self.snapshot )
				self.snapshot = self.cam.get_image( self.snapshot )
				self.image_brut = self.__pygame_to_cvimage__( self.snapshot )
			else:
				self.image_brut = self.snapshot
		else:
			if self.cam.query_image():
				self.snapshot = self.cam.get_image( self.snapshot )
				self.image_brut = self.__pygame_to_cvimage__( self.snapshot )
			else:
				self.image_brut = self.snapshot


	def __img_filter__( self ):
		'''
			tranforme l'image capturer en une image filtre puis la stocke dans self.matriximg
		'''
		self.__capture_im__()
		dilatedimg = cv.CloneImage( self.image_brut )
		cv.Dilate( self.image_brut, dilatedimg )
		blurim = cv.CloneImage( dilatedimg )
		#cv.Smooth(dilatedimg, blurim,cv.CV_GAUSSIAN, 5, 5)
		imgg = cv.CreateImage( self.size, 8, 1 )
		#cv.CvtColor( blurim, imgg, cv.CV_BGR2HSV )
		cv.CvtColor( blurim, imgg, cv.CV_RGB2GRAY )
		cv.Threshold( imgg, self.bitimage, self.vmin, self.vmax, cv.CV_THRESH_BINARY )
		cv.Copy( self.bitimage, self.image_actuel )
		matpygame = surfarray.array2d( self.__cvimage_to_pygame__( self.bitimage ) )
		self.matriximg = numpy.asarray( matpygame )


	def __laplace_filter__( self ):
		'''
			filtre l'image avec l'algo laplace puis la stocke dans self.laplacehim
		'''
		self.__capture_im__()
		laplaceim_jpg = transform.laplacian( self.snapshot )
		tempim = self.__pygame_to_cvimage__( laplaceim_jpg )
		cv.CvtColor( tempim, self.laplaceim, cv.CV_RGB2GRAY )
		self.image_actuel = self.laplaceim
		cv.Copy( self.laplaceim, self.image_actuel )
		#cv.SaveImage( "img.jpg", self.laplaceim )
		#imgcl = cv.CloneImage( self.image_brut )
		#dst_16s2 = cv.CreateImage( self.size, cv.IPL_DEPTH_16S, 1 )
		#cv.Laplace( imgcl, dst_16s2, 3 )
		#cv.Convert( dst_16s2, self.laplaceim )

	def __find_centroid_faster_numpy__( self, arr, rez ):
		'''
			recherche le centre du point laser si possible
		@param arr:	un tableau 2d 
		@type arr:	numpy.array
		@param rez: resolution de recherche
		@type rez: int
		'''
		listf = self.listplage #arr_rez = arr[::rez,::rez]
		tempflag = 0
		for n in listf:
			arr_rez = arr[136:184:rez, n[1]:n[0]:rez]
			testcarr = numpy.sum( arr_rez )
			if testcarr < ( 10 * self.vmax ):
				#print "pas assez de lumiere "+str(n)
				self.point = 0.0, 0.0
				tempflag = 0
			elif testcarr > ( 300 * self.vmax ):
				#print "trop de lumiere "+str(n)+" "+str(testcarr)
				self.point = 0.0, 0.0
				tempflag = 2
			else:
				self.point = 0.0, 0.0
				tempflag = 1
				self.plage_rech = ( n[1], n[0] )
				print "point trouve " + str( n )
				break
		if tempflag == 1:
			#ygrid, xgrid  = numpy.mgrid[0:cam_width:rez, 0:cam_height:rez]
			ygrid, xgrid = numpy.mgrid[136:184:rez, self.plage_rech[0]:self.plage_rech[1]:rez]
			xcen, ycen = xgrid[arr_rez == self.vmax].mean(), ygrid[arr_rez == self.vmax].mean()
			try:
				self.point = ycen, xcen
			except ValueError:
				self.point = 0.0, 0.0

	def __camera_corrected_fx__( self, posX ):
		return 351.123#1456.138

	def __calculate_distance__( self, vc ):
		'''
			calcule la distance entre le robot et l'obstacle
		@param vc: point x
		@type vc: float
		@return: retourne une distance en cm
		@rtype: float
		'''
		#print "vc:"+str(vc)
		#print "beta:"+str(beta)
		#print "L:"+str(L)
		#print "CW:"+str(cam_height)
		vx = vc - ( self.cam_height / 2.0 )
		if vx == 0:
			vx = 0.0001 #a sort of laplacian smoothing
		#print "vx:"+str(vx)
		delta = atan( self.__camera_corrected_fx__( vc ) / abs( vx ) )
		if vx > 0:
			delta = pi - delta
		#print "delta:"+str(delta)
		lambd = pi - radians( self.BETA ) - delta
		#print "lambda:"+str(lambd)
		Dc = self.L * sin( radians( self.BETA ) ) / sin( lambd )
		#print "Dc:" + str( Dc )
		return Dc

	def set_laser( self, _bool_ ):
		time.sleep( 0.05 )
		self.laser_pos = _bool_
		self.laser.write( _bool_ )
		time.sleep( 0.05 )

	def get_capture( self ):
		'''

		@return: retourne l'image brut de la webcam
		@rtype: cvimage
		'''
		self.__capture_im__()
		return self.image_brut

	def get_image_filtered( self ):
		'''

		@return: retourne une image filtre en niveau de gris
		@rtype: cvimage
		'''
		self.__img_filter__()
		return self.bitimage

	def get_laplace_image( self ):
		'''

		@return: retourne une image filtre laplace en niveau de gris
		@rtype: cvimage
		'''
		self.__laplace_filter__()
		return self.laplaceim

	def get_range( self ):
		'''

		@return: retourne la distance en cm de l'obstacle si possible
		@rtype: float
		'''
		etat = 0
		if self.laser_pos == False :
			self.set_laser( True )
			etat = 1
		self.__img_filter__()
		if etat == 1:
			self.set_laser( False )
		self.__find_centroid_faster_numpy__( self.matriximg, 1 )
		return abs( self.__calculate_distance__( self.point[1] ) )

	def get_etat_laser( self ):
		'''

		@return: retourne l'etat du laser allumer,eteind
		@rtype: bool
		'''
		return self.laser_pos

	def __del__( self ):
		print 'Goodbye'
		self.cam.stop()
		camera.quit()
