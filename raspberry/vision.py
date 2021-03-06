import ConfigParser, time, cv2, cv
import numpy
from math import *

#===============================================================================
# Vision
#===============================================================================
class Vision():
	'''
		class permetant de traiter differente information sur la vision du robot
	'''
	def __init__( self, config, bus ):
		'''
		@param board: objet pyfirmata
		@type board: pyfirmata
		@param config: objet configparser contenant les configurations du robot
		@type config: configparser.RawConfigParser
		'''
		self.timexe = 0
		self.cam_width = config.getint( 'Camera', 'width' ) #largeur camera
		self.cam_height = config.getint( 'Camera', 'height' ) #hauteur camera
		self.device = config.getint( 'Camera', 'device' ) # lien vers la webcam 
		self.size = ( self.cam_width, self.cam_height ) # tuple (largeur, hauteur)
		self.bitimage = None # image noir et blanc
		self.matriximg = None
		self.laplaceim = None
		self.numpy_array = None
		self.image_actuel = None
		self.image_brut = None #image capture
		self.vmin = config.getint( 'Camera', 'tresholdmin' ) #valeur minimum treshold
		self.vmax = config.getint( 'Camera', 'tresholdmax' ) #valeur maximum treshold
		self.cam = cv.CaptureFromCAM( 0 )
		# configuration pour le lrf
		self.laser = bus.laser
		self.laser_pos = False
		self.listplage = ( ( 144, 128 ), ( 128, 96 ), ( 96, 48 ), ( 64, 48 ), ( 48, 24 ), ( 24, 0 ) )
		self.plage_rech = ( 0, 0 ) #nby, nbx
		self.point = []
		self.BETA = config.getfloat( 'Lrf', 'beta' )
		self.L = config.getfloat( 'Lrf', 'lfocus' )


	def __capture_im__( self ):
		'''
			capture une image et la stocke dans self.image_brut
		'''
		self.image_brut = cv2.cv.QueryFrame( self.cam )
		#self.cam.read()
		#bitmap = cv.CreateImageHeader( ( source.shape[1], source.shape[0] ), cv.IPL_DEPTH_8U, 3 )
		#cv.SetData( bitmap, source.tostring(),
        #source.dtype.itemsize * 3 * source.shape[1] )
		#self.image_brut = cv.CloneImage( bitmap )


	def __img_filter__( self ):
		'''
			tranforme l'image capturer en une image filtre puis la stocke dans self.matriximg
		'''
		self.__capture_im__()
		self.__lazer_filter__()
		dilatedimg = cv.CloneImage( self.image_brut )
		cv.Dilate( self.image_brut, dilatedimg )
		blurim = cv.CloneImage( dilatedimg )
		#cv.Smooth(dilatedimg, blurim,cv.CV_GAUSSIAN, 5, 5)
		imgg = cv.CreateImage( self.size, 8, 1 )
		#cv.CvtColor( blurim, imgg, cv.CV_BGR2HSV )
		cv.CvtColor( blurim, imgg, cv.CV_RGB2GRAY )
		cv.Threshold( imgg, self.bitimage, self.vmin, self.vmax, cv.CV_THRESH_BINARY )
		cv.Copy( self.bitimage, self.image_actuel )
		self.matriximg = self.__im_to_numpy_arr__( self.bitimage )

	def __im_to_numpy_arr__( self, img ):
		matpygame = surfarray.array2d( self.__cvimage_to_pygame__( img ) )
		return numpy.asarray( matpygame )

	def __lazer_filter__( self ):
		#self.__capture_im__()
		hsv_image = cv.CreateImage( self.size, 8, 3 )
		cv.CvtColor( self.image_brut, hsv_image, cv.CV_BGR2HSV )
		#cv.Copy( self.image_brut, hsv_image )
		h_img = cv.CreateImage( self.size, 8, 1 )
		s_img = cv.CreateImage( self.size, 8, 1 )
		v_img = cv.CreateImage( self.size, 8, 1 )
		cv.Split( hsv_image, h_img, s_img, v_img, None )
		cv.SaveImage( "img.jpg", hsv_image )
		cv.SaveImage( "imgh.jpg", h_img )
		cv.SaveImage( "imgs.jpg", s_img )
		cv.SaveImage( "imgv.jpg", v_img )

	def __laplace_filter__( self ):
		'''
			filtre l'image avec l'algo laplace puis la stocke dans self.laplacehim
		'''
		self.__capture_im__()
		laplaceim = cv.CreateImage( self.size, 8, 3 )
		cv.Laplace( self.image_brut, laplaceim )
		cv.CvtColor( laplaceim, self.laplaceim, cv.CV_RGB2GRAY )
		cv.Copy( self.laplaceim, self.image_actuel )

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
				#print "point trouve " + str( n )
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
		self.laser()
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

	def estimateLux( self ):
		self.__capture_im__()
		img = cv.CloneImage( self.image_brut )
		img = cv.GetMat( img, allowND=0 ) # iplImage -> CvMat
		#initialize placeholders for BGR values
		# get a CvScalar (tuple) with the sum of each of the 3 channels
		resultsTuple = cv.Sum( img )
		#return results as a list in RGB order for simplicty's sake
		pixels = self.cam_height * self.cam_width
		statsRGB = list( [resultsTuple[2] / pixels, resultsTuple[1] / pixels, resultsTuple[0] / pixels] )
		#calculate the light index using formula found at autohotkey.com
		red = statsRGB[0]
		green = statsRGB[1]
		blue = statsRGB[2]
		lux = ( red * .229 ) + ( green * .587 ) + ( blue * .114 )
		statsRGB.insert( 0, lux )
		return statsRGB


	def __del__( self ):
		print 'Goodbye'
		self.cam.stop()
		camera.quit()
