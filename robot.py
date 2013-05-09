import ConfigParser, pyfirmata
from vision import Vision
import propulsion, landmap, collections, time, thread, numpy, stream, core
#===============================================================================
# Robot
#===============================================================================
class Robot():
    '''
        classe qui rassemble l'ensemble des modules du robot
            les differente fonction principale du robot:
                exploration, decouverte du terrain
                patrouille de point en point
                deplacement d'un point a un autre ,a partir de la carte decouverte
                affchage de la carte complete du terrain
        
    '''
    def __init__( self ):
        self.config = ConfigParser.RawConfigParser()
        self.config.read( 'RobotConf.cfg' )
        self.board = pyfirmata.ArduinoMega( self.config.get( 'Arduino', 'device' ) )
        self.prop = propulsion.Propulsion( self.config, self.board )
        self.tourel = propulsion.Tourelle( self.config, self.board )
        self.vue = Vision( self.config, self.board )
        self.land = landmap.LandMap()
        self.accel = propulsion.Accel( self.config )
        self.pile_vision = core.Core()
        #self.pilevar = collections.deque()
        self.pile_move = core.Core()
        self.running = False
        self.orientation = 0.0
        self.x = 0.0
        self.y = 0.0
        self.stream = stream.HTTPServer( ( "", 8080 ), self.vue )


    def start( self ):
        self.running = True
        thread.start_new_thread( self.__cerveau__, () )
        thread.start_new_thread( self.__mouvement__, () )
        thread.start_new_thread( self.stream.serve_forever, () )

    def stop( self ):
        self.running = False

    def __mouvement__( self ):
        while self.running:
            if self.pile_move.pile.__len__() <= 0:
                time.sleep( 0.1 )
            else:
                self.pile_move.exec_next()

    def __cerveau__( self ):
        '''
            cerveau se compose de differente pile avec different priorite
        '''
        while self.running:
            if self.pile_vision.pile.__len__() <= 0:
                time.sleep( 0.1 )
            else:
                self.pile_vision.exec_next()

    def balayage( self, depart , arrive , pas=1 ):
        if depart <= arrive :
            lis = numpy.arange( depart, arrive, pas )
        else:
            lis = numpy.arange( arrive, depart, pas )
            lis = lis[::-1]
        listd = []
        self.tourel.depl_tour( depart )
        for i in lis:
            self.tourel.depl_tour( i )
            listd.append( ( i, self.vue.get_range() ) )
        return listd
