import smbus
class I2c_arduino():
    AV = 0b11      #0x3
    AR = 0b1       #0x1
    G = 0b100     #0x4
    D = 0b1100    #0xc
    L = 0b10000   #0x10
    RAZ = 0b100000  #0x20

    def __init__( self, address ):
        self.bus = smbus.SMBus( 0 )
        self.address = address
        self.command = 0

    def envoi( self ):
        self.bus.write_byte_data( self.address, 0, low )

    def get( self ):
        pass
