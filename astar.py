#!/usr/bin/python
# -*- coding: utf-8 -*-

import collections, sys

MOVEMENT_COST = 10

class Square( object ):
    '''
        represente un carre dans une grille
    '''
    x = 0
    y = 0
    parent = None
    f_cost = 0
    g_cost = 0
    h_cost = None
    walkable = True

    def update_parent( self, new_parent ):
        self.parent = new_parent
        self.g_cost = self.calculate_cost_from_start_with_parent( self.parent )
        self.f_cost = self.h_cost + self.g_cost

    def calculate_cost_from_start_with_parent( self, parent ):
        return parent.g_cost + MOVEMENT_COST

    def estimate_cost_to_target( self, target ):
        horizontal_cost = abs( target.x - self.x ) * MOVEMENT_COST
        vertical_cost = abs( target.y - self.y ) * MOVEMENT_COST

        return horizontal_cost + vertical_cost

    def __lt__( self, other ):
        return self.f_cost < other.f_cost

    def set_walkable( self, bool ):
        '''
            definie si le carre est accessible pour le robot
        @param bool: si True alors il est accessible
        @type bool: boolean
        '''
        self.walkable = bool

class Maze( object ):
    '''
        represente une grille constituer de carre
    '''
    squares = []
    width = 0
    height = 0

    def __init__( self, squares ):
        self.squares = squares
        self.width = len( squares[0] )
        self.height = len( squares )

    def get( self, x, y ):
        '''
            retourne un carre
        @param x: pos x sur la grille
        @type x: int
        @param y: pos y sur la grille
        @type y: int
        @return: retourne le carre de la position x,y
        @rtype: square
        '''
        return self.squares[y][x]

    def initialize_estimated_cost_to_target_for_all_nodes( self, target ):
        for row in self.squares:
            for square in row:
                square.h_cost = square.estimate_cost_to_target( target )

    def adjacent_squares( self, square ):
        '''
        @param square: un carre qui appartient a la grille
        @type square: Square
        @return: list de carre qui se situe autour du carre entre en param
        @rtype: list
        
        '''
        adjacent_squares = set()

        for delta in [( 1, 0 ), ( -1, 0 ), ( 0, 1 ), ( 0, -1 )]:
            x_delta, y_delta = delta
            adjacent_x = square.x + x_delta
            adjacent_y = square.y + y_delta

            if adjacent_x >= 0 and adjacent_x < self.width and adjacent_y >= 0 and adjacent_y < self.height:
                adjacent_squares.add( self.get( adjacent_x, adjacent_y ) )

        return adjacent_squares

    def print_path( self, path ):
        '''
            affiche le chemin ce trouvant dans le param
        @param path: liste de point generer par astar()
        @type path: list
        '''
        for row in self.squares:
            for square in row:
                if square == path[0]:
                    sys.stdout.write( 'A' )
                elif square == path[-1]:
                    sys.stdout.write( 'B' )
                elif square in path:
                    sys.stdout.write( '*' )
                elif square.walkable:
                    sys.stdout.write( '.' )
                else:
                    sys.stdout.write( 'X' )

            sys.stdout.write( '\n' )

        sys.stdout.flush()

    @staticmethod
    def from_file( filename ):
        '''
            construit Maze a partir d'un fichier
        @param filename: fichier contenant des information sur la carte
        @type filename: Fichier
        @return: retourne l'objet remplis par les information du fichier
        @rtype: Maze
        '''
        squares = []

        f = open( filename, "r" )
        lines = f.readlines()
        f.close()

        for y in range( len( lines ) - 1 ):
            line = lines[y].strip()
            squares.append( [] )

            for x in range( len( line ) - 1 ):
                square = Square()
                square.x = x
                square.y = y
                square.walkable = line[x] == '.'

                squares[y].append( square )

        return Maze( squares )
    @staticmethod
    def from_array_2d( ar ):
        '''
            construit Maze a partir d'un tableau 2d
        @param ar: array contenant les information sur la carte
        @type ar: numpy.array
        @return: retourne l'objet remplis par les information du tableau
        @rtype: Maze
        '''
        squares = []
        for y in range( len( ar ) ):
            squares.append( [] )
            for x in range( len( ar[0] ) ):
                square = Square()
                square.x = x
                square.y = y
                square.walkable = ar[y][x] == '.'
                squares[y].append( square )
        return Maze( squares )


class OpenList( object ):
    squares = set
    order = list

    def __init__( self ):
        self.squares = set()
        self.order = []

    def __contains__( self, square ):
        return square in self.squares

    def __len__( self ):
        return len( self.squares )

    def add( self, square ):
        self.squares.add( square )
        self.order.append( square )
        self.sort()

    def sort( self ):
        self.order.sort( reverse=True )

    def take_square_with_lowest_f( self ):
        lowest = self.order.pop()
        self.squares.remove( lowest )

        return lowest


def astar( maze, start_node, target_node ):
    '''
        astar recherche le meilleur chemin dans la grille , d'un point A a un point B
    @param maze: grille contenant les information de la map
    @type maze: Maze
    @param start_node: point de depart
    @type start_node: Square
    @param target_node: point d'arrive
    @type target_node: Square
    @return: liste de point pour arrver jusqu'au point B
    @rtype: list
    '''
    maze.initialize_estimated_cost_to_target_for_all_nodes( target_node )

    closed_list = set()

    open_list = OpenList()
    open_list.add( start_node )

    found = False
    while len( open_list ) > 0:
        current = open_list.take_square_with_lowest_f()
        closed_list.add( current )

        if current == target_node:
            found = True
            break

        for adjacent_square in maze.adjacent_squares( current ):
            if not adjacent_square.walkable or adjacent_square in closed_list:
                continue

            if adjacent_square not in open_list:
                adjacent_square.update_parent( current )
                open_list.add( adjacent_square )
            else:
                if adjacent_square.calculate_cost_from_start_with_parent( current ) < adjacent_square.g_cost:
                    adjacent_square.update_parent( current )
                    open_list.sort()

    if found:
        path = []
        current = target_node

        while current is not None:
            path.append( current )
            current = current.parent

        path.reverse()
        return path
    else:
        return None

if __name__ == "__main__":
    import sys

    if len( sys.argv ) != 6:
        print "Usage: %s FILE START_X START_Y TARGET_X TARGET_Y" % sys.argv[0]
        exit( 1 )

    maze = Maze.from_file( sys.argv[1] )
    start_x = int( sys.argv[2] )
    start_y = int( sys.argv[3] )
    target_x = int( sys.argv[4] )
    target_y = int( sys.argv[5] )

    start_node = maze.get( start_x, start_y )
    target_node = maze.get( target_x, target_y )

    if not start_node.walkable or not target_node.walkable:
        print "Start node or target node is not walkable. No solution exists."
        exit( 1 )

    path = astar( maze, start_node, target_node )
    if path:
        maze.print_path( path )

        print "\nA = start node, B = target node, * = path node"
    else:
        print "No path found"
