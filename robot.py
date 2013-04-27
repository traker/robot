import ConfigParser, pyfirmata
from vision import Vision
import propulsion, landmap, collections, time, thread
class Robot():
    '''
        classe qui rassemble l'ensemble des modules du robot
    '''
    def __init__( self ):
        self.config = ConfigParser.RawConfigParser()
        self.config.read( 'RobotConf.cfg' )
        self.board = pyfirmata.ArduinoMega( self.config.get( 'Arduino', 'device' ) )
        self.prop = propulsion.Propulsion( self.config, self.board )
        self.tourel = propulsion.Propulsion( self.config, self.board )
        self.vue = Vision( self.config, self.board )
        self.land = landmap.LandMap()
        self.accel = propulsion.Accel( self.config )
        self.pile = collections.deque()
        self.pilevar = collections.deque()
        self.running = False


    def start( self ):
        self.running = True
        thread.start_new_thread( self.coeur, () )

    def stop( self ):
        self.running = False

    def add_to_pile( self, exe, var=() ):
        self.pile.append( exe )
        self.pilevar( var )

    def __exec_next__( self ):
        self.pile.popleft()( self.pilevar.popleft() )

    def coeur( self ):
        while self.running:
            if self.pile > 0:
                self.__exec_next__()
            else:
                time.sleep( 0.1 )
            #thread.start_new_thread(gcode.get(ref[0],nullcomm),(ref[1:],))
