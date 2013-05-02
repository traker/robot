import ConfigParser, pyfirmata
from vision import Vision
import propulsion, landmap, collections, time, thread, numpy, stream
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
        self.pile = collections.deque()
        #self.pilevar = collections.deque()
        self.pile_resultat = collections.deque()
        self.running = False
        self.orientation = 0.0
        self.x = 0.0
        self.y = 0.0
        self.stream = stream.HTTPServer( ( 192, 168, 1, 7 ), self )


    def start( self ):
        self.running = True
        thread.start_new_thread( self.coeur, () )

    def stop( self ):
        self.running = False

    def add_to_pile( self, exe, var=None ):
        objexe = ( exe, var )
        self.pile.append( objexe )
        #self.pilevar.append( var )

    def __exec_next__( self ):
        exe, var = self.pile.popleft()
        if var == None:
            self.pile_resultat.append( exe() )
        else:
            self.pile_resultat.append( exe( *var ) )

    def coeur( self ):
        '''
            coeur se compose de differente pile avec different priorite
        '''
        while self.running:
            if self.pile.__len__() <= 0:
                time.sleep( 0.1 )
            else:
                self.__exec_next__()
                #print self.pile_resultat.popleft()
            #thread.start_new_thread(gcode.get(ref[0],nullcomm),(ref[1:],))

    def balayage( self, depart , arrive ):
        lis = numpy.arange( depart, arrive )
        listd = []
        self.tourel.depl_tour( depart )
        for i in lis:
            self.tourel.depl_tour( i )
            listd.append( ( i, self.vue.get_range() ) )
        return listd
