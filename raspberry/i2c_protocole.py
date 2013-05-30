from Adafruit_I2C import Adafruit_I2C
import time
class I2c_arduino():
    CMDG = 0x00
    TOUREXE = 0x01
    PROPAR = 0x02
    PROPAV = 0x03
    TOURNG = 0x04
    TOURND = 0x05
    LASERON = 0x06
    RAZ = 0x07
    DCG = 0x08
    DCD = 0x09

    CMDX = 0x01
    CMDY = 0x02
    CMD = 0x00
    def __init__( self ):
        self.i2c = Adafruit_I2C( 0x20 )

    def __list_bytes_to_int__( self, barray ):
       return sum( barray[i] << ( i * 8 ) for i in range( 4 ) )

    def regarde( self, x, y ):
        self.i2c.write8( self.CMDX, x )
        time.sleep( 0.020 )
        self.i2c.write8( self.CMDY, y )
        time.sleep( 0.020 )
        #self.i2c.write8( self.CMDG, self.TOUREXE )
        self.CMD += self.TOUREXE

    def avance( self, avar ):
        if( avar ):
            self.i2c.write8( self.CMDG, self.PROPAV )
            #self.CMD += self.PROPAV
        else:
            self.i2c.write8( self.CMDG, self.PROPAR )
            #self.CMD += self.PROPAR

    def tourne( self, dg ):
        if( dg ):
            self.i2c.write8( self.CMDG, self.TOURND )
            #self.CMD += self.TOURND
        else:
            self.i2c.write8( self.CMDG, self.TOURNG )
            #self.CMD += self.TOURNG

    def laser( self ):
        self.i2c.write8( self.CMDG, self.LASERON )
        #self.CMD += self.LASERON
    def raz( self ):
        self.i2c.write8( CMDG, self.RAZ )
        self.CMD += self.RAZ

    def get_Compteur( self ):
        #compteur droite
        self.i2c.write8( self.CMDG, self.DCD )
        time.sleep( 0.020 )
        tmpDar = self.i2c.readList( self.CMDG, 4 )
        tmpD = self.__list_bytes_to_int__( tmpDar )
        time.sleep( 0.020 )
        #compteur gauche
        self.i2c.write8( self.CMDG, self.DCG )
        time.sleep( 0.020 )
        tmpGar = self.i2c.readList( self.CMDG, 4 )
        tmpG = self.__list_bytes_to_int__( tmpGar )
        time.sleep( 0.020 )
        return tmpD, tmpG



