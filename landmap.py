# -*- coding: utf-8 -*-
import astar, numpy


#===============================================================================
# LandMap
#===============================================================================
class LandMap():
    """
        module contenant les information de position du robot
    """
    size_square = ( 20, 20 ) #taille d'un carres en cm
    path = []
    def __init__( self ):
        """
        initialisation 
        """
        self.land = astar.Maze.from_array_2d( self.__land_init__() )
        self.robot_pos = self.get_square( 0, 0 )

    def __land_init__( self ):
        """
        @return: renvoi un tableau 2d de hauteur 50 et largeur 50
        remplis de "."
        @rtype: numpy.array
        """
        templand = numpy.empty( ( 50, 50 ), str )
        templand.fill( '.' )
        return templand

    def __scale__( self, x, y ):
        """
        @param x: valeur de x en cm
        @param y: valeur de y en cm
        @type x: float
        @type y: float
        @return: un point x,y a l'echelle du tableau
        """
        return x / self.size_square[0], y / self.size_square[1]

    def get_land( self ):
        '''
        @return: retourne la map
        @rtype: astar.Maze
        '''
        return self.land

    def set_pos_robot( self, x, y ):
        '''
            assigne la position du robot dans la map
        @param x: position x en cm
        @type x: float
        @param y: position y en cm
        @type y: float
        '''
        self.robot_pos = self.get_square( self.__scale__( x, y ) )

    def get_pos_robot( self ):
        '''
        @return: renvoi la position du robot
        @rtype: astar.Square
        '''
        return self.robot_pos

    def get_square( self, x, y ):
        '''
            renvoi un Square 
        @param x: position x dans la map
        @type x: int
        @param y: position y dans la map
        @type y: int
        @return: renvoi l'Objet Square de la position x,y 
        @rtype: astar.Square
        '''
        return self.land.get( x, y )

    def set_wall( self, x, y, bool ):
        '''
            si vrai ajoute un mur a la position x,y
            si faux enleve le mur a la position x,y
        @type x: int
        @type y: int
        @type bool: boolean
        '''
        self.get_pos( x, y ).set_walkable( bool )

    def get_size_square( self ):
        '''
        @return: taille reel d'un square x,y en cm
        @rtype: list
        '''
        return self.size_square

    def search_path( self, x, y ):
        '''
         recherche le meilleur chemin vers le point x,y
        @type x: int
        @type y: int
        @return: liste de point de passage
        @rtype: list
        '''
        self.path = astar.astar( self.land, self.robot_pos, self.get_square( x, y ) )
        return self.path

