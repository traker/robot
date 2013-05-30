from Adafruit_I2C import Adafruit_I2C
import time
class I2c_arduino():
    CMDG = 0x00
    TOUREXE = 0x01
    PROPAR = 0x02
    PROPAV = 0x06
    TOURNG = 0x08
    TOURND = 0x18
    LASERON = 0x20
    RAZ = 0x40

    CMDC = 0x01
    DCG = 0x01
    DCD = 0x02

    CMDX = 0x01
    CMDY = 0x02
    CMD = 0x00
    def __init__( self ):
        self.i2c = Adafruit_I2C( 0x20 )

    def __list_bytes_to_int__( self, barray ):
       return sum( barry[i] << ( i * 8 ) for i in range( 4 ) )

    def regarde( self, x, y ):
        self.i2c.write8( self.CMDX, x )
        time.sleep( 0.020 )
        self.i2c.write8( self.CMDY, y )
        time.sleep( 0.020 )
        #self.i2c.write8( self.CMDG, self.TOUREXE )

    def avance( self, avar ):
        if( avar ):
            #self.i2c.write8( CMDG, PROPAV )
            self.CMD + self.PROPAV
        else:
            #self.i2c.write8( CMDG, PROPAR )
            self.CMD + self.PROPAR

    def tourne( self, dg ):
        if( dg ):
            #self.i2c.write8( CMDG, TOURND )
            self.CMD + self.TOURND
        else:
            #self.i2c.write8( CMDG, TOURNG )
            self.CMD + self.TOURNG

    def laser( self, onoff ):
        if onoff:
            #self.i2c.write8( CMDG, LASERON )
            self.CMD + self.LASERON
    def raz( self ):
        self.CMD + self.RAZ

    def execute( self ):
        self.i2c.write8( self.CMDG, self.CMD )
        self.CMDG = 0x00

    def get_Compteur( self ):
        #compteur droite
        self.i2c.write8( self.CMDC, self.DCD )
        time.sleep( 0.020 )
        tmpDar = self.i2c.readList( self.CMDG, 4 )
        tmpD = self.__list_bytes_to_int__( tmpDar )
        #compteur gauche
        self.i2c.write8( self.CMDC, self.DCG )
        time.sleep( 0.020 )
        tmpGar = self.i2c.readList( self.CMDG, 4 )
        tmpG = self.__list_bytes_to_int__( tmpGar )
        return tmpD, tmpG



