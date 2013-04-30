'''
    collection de classe qui gere diffferent organe du robot
        Accel
        Moteur
        Propultion
        Tourelle
'''
import pyfirmata, time
import ConfigParser, numpy
import accelerometer
import commands

class Accel():
    '''
        renvoi differente information du module accelerometre.
        configuration du module:
        commands.getstatusoutput( 'i2c 58 wb 22 5' )
            00 : standby mode
            01 : measurement mode
            10 : level detection mode
            11 : pulse detection mode
            The next two bits define the sensitivity:
            00 : 8g range, 16 LSB/g
            01 : 2g range, 64 LSB/g
            10 : 4g range, 32 LSB/g
            So put it into measurement mode, 2g range, we write 0000 0101 binary (5 decimal) to register $16 (decimal 22) at bus address 58.
    '''
    def __init__( self, config ):
        self.device = config.get( 'Accelerometre', 'device' )
        commands.getstatusoutput( 'i2c 58 wb 22 5' )
        self.fd = accelerometer.open( self.device )

    def get_pos( self ):
        '''
        @return: retourne les valeurs en liste
        @rtype: list
        '''
        return accelerometer.read( self.fd )

    def get_x( self ):
        '''
        @return: renvoi la valeur pour l'axe x
        @rtype: int
        '''
        return accelerometer.read( self.fd )[0]

    def get_y( self ):
        '''
        @return: renvoi la valeur pour l'axe y
        @rtype: int
        '''
        return accelerometer.read( self.fd )[1]

    def get_z( self ):
        '''
        @return: renvoi la valeur pour l'axe z
        @rtype: int
        '''
        return accelerometer.read( self.fd )[2]

    def __del__( self ):
         commands.getstatusoutput( 'i2c 58 wb 22 1' )


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


class Propulsion():
    '''
        class permettant de gerer la propusion du robot
    '''
    list_vitesse = [0, 0]
    vitesse = 3
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
        for i in range( 0, mm ):
            self.motGauche.step( True )
            self.motDroit.step( True )
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
        return self.compteur_gauche, self.compteur_droit

    def reset_compteurs( self ):
        self.compteur_droit = 0
        self.compteur_gauche = 0

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
                print "egal"
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

