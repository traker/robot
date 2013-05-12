'''
    collection de classe qui gere diffferent organe du robot
        Accel
        Moteur
        Propultion
        Tourelle
'''
import pyfirmata, time
import ConfigParser, numpy
import commands



#===============================================================================
# Moteur
#===============================================================================
class Moteur():
    '''
        objet pernettant de manipuler un servo
    '''
    etat = 90
    def __init__( self, board, pin , posgauche=True ):
        '''
        @param board: objet pyfirmata
        @type board: pyfirmata
        @param pin: pin arduino
        @type pin: pyfirmata.Pin
        '''
        board.servo_config( pin, angle=90 )
        self.servo = board.digital[pin]
        self.compteur = 0
        self.poschassis = posgauche

    def step( self, sens ):
        if self.poschassis:
            if sens:
                self.write( 180 )
                self.compteur += 1
            else:
                self.write( 0 )
                self.compteur -= 1
        else:
            if sens:
                self.write( 0 )
                self.compteur += 1
            else:
                self.write( 180 )
                self.compteur -= 1
        time.sleep( 0.01 )
        self.write( 90 )

    def write( self, angle ):
        '''
        @param angle: envoi l'angle au servomoteur
        @type angle: int
        '''
        self.servo.write( angle )
        self.etat = angle

    def get_etat( self ):
        '''
        @return: revoi l'angle actuel
        @rtype: int
        '''
        return self.etat

    def get_compteur( self ):
        return self.compteur

    def reset_compteur( self ):
        self.compteur = 0

#===============================================================================
# Propulsion
#===============================================================================
class Propulsion():
    '''
        class permettant de gerer la propusion du robot
    '''
    neutre = 90
    def __init__( self, config, board ):
        '''
        @param board: objet pyfirmata
        @type board: pyfirmata
        @param config: objet configparser contenant les configurations du robot
        @type config: configparser.RawConfigParser()
        '''
        self.pinMotGauche = config.getint( 'Propulsion', 'pin_moteurgauche' )
        self.pinMotDroite = config.getint( 'Propulsion', 'pin_moteurdroit' )
        self.motGauche = Moteur( board, self.pinMotGauche )
        self.motDroit = Moteur( board, self.pinMotDroite, False )
        #dictionnaire vitesse = (servoG, servoD)

    def avancer_mm( self, mm , vitesse ):
        if mm > 0:
            for i in range( 0, mm ):
                self.motGauche.step( True )
                self.motDroit.step( True )
                if not vitesse: time.sleep( 0.005 )
        elif mm < 0:
            for i in range( 0, mm ):
                self.motGauche.step( False )
                self.motDroit.step( False )
                if not vitesse: time.sleep( 0.005 )

    def tourner_mm( self, deg ):
        if deg < 180:
            for i in range( 0, ( 180 - deg ) * 2 ):
                self.motDroit.step( True )
                self.motGauche.step( False )
        elif deg == 180:
            pass
        elif deg > 180:
            for i in range( 0, ( deg - 180 ) * 2 ):
                self.motGauche.step( True )
                self.motDroit.step( False )

    def get_compteurs( self ):
        return self.motGauche.get_compteur(), self.motDroit.get_compteur()

    def reset_compteurs( self ):
        self.motGauche.reset_compteur()
        self.motDroit.reset_compteur()

#===============================================================================
# Tourelle
#===============================================================================
class Tourelle():
    '''
        class permetant de faire fonctionner la tourelle
    '''
    def __init__( self, config, board ):
        '''
        @param board: objet pyfirmata
        @type board: pyfirmata
        @param config: objet configparser contenant les configurations du robot
        @type config: configparser.RawConfigParser()
        '''
        self.pinMotHorizontal = config.getint( 'Tourelle', 'pin_tourelle_h' )
        self.pinMotVertical = config.getint( 'Tourelle', 'pin_tourelle_v' )
        self.motHorizontal = Moteur( board, self.pinMotHorizontal )
        self.motVertical = Moteur( board, self.pinMotVertical )

    def depl_tour( self, hori=90, vert=90 ):
        """
            permet de faire des deplacements selon un axe de rotation
        @param hori: angle rotation horizontal
        @type hori: int
        @param vert: angle rotation vertical
        @type vert: int
        """
        flag_h = 0
        flag_v = 0
        index = 0
        if hori <= self.motHorizontal.get_etat(): flag_h = 0
        else: flag_h = 1
        if vert <= self.motVertical.get_etat(): flag_v = 0
        else: flag_v = 1
        waitrottmp = self.motHorizontal.get_etat() - hori
        waithbtmp = self.motVertical.get_etat() - vert
        diffrot = abs( waitrottmp )
        diffhb = abs( waithbtmp )
        arrh = numpy.array( [] )
        arrv = numpy.array( [] )
        if diffrot >= diffhb:
            if self.motHorizontal.get_etat() == hori :
                #print "egal"
                arrh = numpy.array( [hori] )
            elif flag_h == 1 :
                arrh = numpy.arange( self.motHorizontal.get_etat(), hori )
            else:
                arrh = numpy.arange( hori, self.motHorizontal.get_etat() )
                arrh = arrh[::-1]

            ratio = float( diffhb ) / float( arrh.size )
            index = arrh.size - 1
            if self.motVertical.get_etat() == vert :
                arrv = numpy.arange( arrh.size )
                arrv.fill( vert )
            elif flag_v == 1 :
                arrv = numpy.arange( self.motVertical.get_etat(), vert, ratio )
            else:
                arrv = numpy.arange( vert, self.motVertical.get_etat(), ratio )
                arrv = arrv[::-1]
        else:
            if self.motVertical.get_etat() == vert :
                arrv = numpy.array( [vert] )
            elif flag_v == 1 :
                arrv = numpy.arange( self.motVertical.get_etat(), vert )
            else:
                arrv = numpy.arange( vert, self.motVertical.get_etat() )
                arrv = arrv[::-1]
            ratio = float( diffrot ) / float( arrv.size )
            index = arrv.size - 1
            if self.motHorizontal.get_etat() == hori :
                arrh = numpy.arange( arrv.size )
                arrh.fill( hori )
            elif flag_h == 1 :
                arrh = numpy.arange( self.motHorizontal.get_etat(), hori, ratio )
            else:
                arrh = numpy.arange( hori, self.motHorizontal.get_etat(), ratio )
                arrh = arrh[::-1]

        for n in range( index ):
            self.motHorizontal.write( arrh[n] )
            self.motVertical.write( arrv[n] )
            time.sleep( 0.002 )

    def get_etat( self ):
        '''
        @return: retourne la position des axes [axe_horizontal, axe_vertical]
        @rtype: [int,int]
        '''
        return self.motHorizontal.get_etat(), self.motVertical.get_etat()

