import ConfigParser, pyfirmata
from vision import Vision
import propulsion, landmap
class Robot():
    '''
        class qui rassemble l'ensemble des modules du robot
    '''
    def __init__( self ):
        self.config = ConfigParser.RawConfigParser()
        self.config.read( 'RobotConf.cfg' )
        self.board = pyfirmata.ArduinoMega( config.get( 'Arduino', 'device' ) )
        self.prop = propulsion.Propulsion( self.config, self.board )
        self.tourel = propulsion.Propulsion( self.config, self.board )
        self.vue = Vision( self.config, self.board )
        self.land = landmap.LandMap()
