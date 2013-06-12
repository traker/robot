from Adafruit_I2C import Adafruit_I2C
import time, struct
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
    NIVBATT = 0x10

    CMDX = 0x01
    CMDY = 0x02

    def __init__( self ):
        self.i2c = Adafruit_I2C( 0x20 )

    def regarde( self, x, y ):
        self.i2c.write8( self.CMDX, x )
        time.sleep( 0.020 )
        self.i2c.write8( self.CMDY, y )
        time.sleep( 0.020 )
        self.i2c.write8( self.CMDG, self.TOUREXE )
        time.sleep( 0.020 )

    def avance( self, avar ):
        if( avar ):
            self.i2c.write8( self.CMDG, self.PROPAV )
        else:
            self.i2c.write8( self.CMDG, self.PROPAR )
        time.sleep( 0.020 )

    def tourne( self, dg ):
        if( dg ):
            self.i2c.write8( self.CMDG, self.TOURND )
        else:
            self.i2c.write8( self.CMDG, self.TOURNG )
        time.sleep( 0.020 )

    def laser( self ):
        self.i2c.write8( self.CMDG, self.LASERON )
        time.sleep( 0.020 )
    def raz( self ):
        self.i2c.write8( self.CMDG, self.RAZ )
        time.sleep( 0.020 )

    def get_Compteur( self ):
        try:
            #compteur droite
            self.i2c.write8( self.CMDG, self.DCD )
            time.sleep( 0.020 )
            tmpDar = self.i2c.readList( self.CMDG, 4 )
            if tmpDar != -1:
                tmpD = chr( tmpDar[0] ) + chr( tmpDar[1] ) + chr( tmpDar[2] ) + chr( tmpDar[3] )
                resD = struct.unpack( 'l', tmpD )
            else:
                resD = -1
            time.sleep( 0.020 )
            #compteur gauche
            self.i2c.write8( self.CMDG, self.DCG )
            time.sleep( 0.020 )
            tmpGar = self.i2c.readList( self.CMDG, 4 )
            if tmpGar != -1:
                tmpG = chr( tmpGar[0] ) + chr( tmpGar[1] ) + chr( tmpGar[2] ) + chr( tmpGar[3] )
                resG = struct.unpack( 'l', tmpG )
            else:
                resG = -1
            time.sleep( 0.020 )
            return resD, resG
        except ValueError:
            pass

    def get_batt( self ):
        self.i2c.write8( self.CMDG, self.NIVBATT )
        time.sleep( 0.020 )
        tmp = self.i2c.readList( self.CMDG, 4 )
        time.sleep( 0.020 )
        cha = chr( tmp[0] ) + chr( tmp[1] ) + chr( tmp[2] ) + chr( tmp[3] )
        return struct.unpack( 'f', cha )

