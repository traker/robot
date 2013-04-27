import ConfigParser, pyfirmata
from vision import Vision
config = ConfigParser.RawConfigParser()
config.read( 'RobotConf.cfg' )
board = pyfirmata.ArduinoMega( "/dev/ttyACM0" )
print "Setting up Arduino..."
it = pyfirmata.util.Iterator( board )
it.start()
test = Vision( config, board )

import pyfirmata
board = pyfirmata.ArduinoMega( "/dev/ttyACM0" )
pin_motG = 6
pin_motD = 3
board.servo_config( pin_motG, angle=90 )
board.servo_config( pin_motD, angle=90 )
motG = board.digital[pin_motG]
motD = board.digital[pin_motD]

import ConfigParser, pyfirmata
import propulsion
config = ConfigParser.RawConfigParser()
config.read( 'RobotConf.cfg' )
board = pyfirmata.ArduinoMega( "/dev/ttyACM0" )
print "Setting up Arduino..."
it = pyfirmata.util.Iterator( board )
it.start()
tour = propulsion.Tourelle( config, board )
prop = propulsion.Propulsion( config, board )

import astar
list_map = [
        ["X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X"],
        ["X", ".", "X", "X", "X", "X", "X", ".", ".", ".", ".", "X", ".", "X", ".", "X"],
        ["X", ".", "X", ".", ".", ".", "X", ".", ".", ".", ".", "X", ".", "X", ".", "X"],
        [".", ".", "X", ".", ".", ".", "X", ".", ".", ".", ".", "X", ".", "X", ".", "X"],
        ["X", ".", "X", ".", "X", ".", "X", ".", ".", ".", ".", "X", ".", "X", ".", "X"],
        ["X", ".", ".", ".", "X", ".", "X", ".", ".", ".", ".", "X", ".", "X", ".", "X"],
        ["X", "X", "X", "X", "X", ".", ".", ".", ".", ".", ".", "X", ".", "X", ".", "X"],
        ["X", ".", ".", ".", "X", ".", ".", ".", ".", ".", ".", "X", ".", "X", ".", "X"],
        ["X", ".", ".", ".", ".", ".", "X", ".", ".", ".", ".", "X", ".", "X", ".", "X"],
        ["X", ".", ".", "X", "X", "X", "X", ".", ".", ".", ".", "X", ".", "X", ".", "X"],
        [".", ".", ".", ".", ".", ".", "X", ".", "X", "X", ".", "X", ".", "X", ".", "X"],
        ["X", ".", ".", ".", ".", ".", "X", ".", ".", "X", ".", "X", ".", ".", ".", "X"],
        ["X", ".", "X", ".", "X", ".", "X", ".", ".", "X", ".", "X", ".", "X", "X", "X"],
        ["X", ".", "X", ".", "X", ".", "X", ".", ".", "X", ".", "X", ".", "X", ".", "X"],
        ["X", ".", "X", ".", "X", ".", "X", ".", ".", ".", ".", ".", ".", "X", ".", "X"],
        ["X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X"],
        ]
ma_map = astar.Maze.from_array_2d( list_map )
ch = astar.astar( ma_map, ma_map.get( 0, 10 ), ma_map.get( 0, 3 ) )
for n in ch:
    print n.x, n.y

ma_map.print_path( ch )
