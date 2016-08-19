from decoder.base import Decoder


class BSIDecoder(Decoder):
    funcs = 0
    lamps = {}

    def id_0x036(self, data):
        """
        Ignition
        """
        self.economy = bool(data[2] & 0x80)
        self.lighting = bool(data[3] & 0x20)
        self.brightness = data[3] & 0x0f
        self.ignition = data[4] & 0x07

    def id_0x0b6(self, data):
        """
        Speed info
        """
        self.rpm = data[0] * 256 + (data[1] >> 3)
        self.speed = data[2] * 256 + data[3]

    def id_0x0e6(self, data):
        """
        Voltage
        """
        self.power = data[5] / 20 + 7.2
    
    def id_0x0f6(self, data):
        """
        Info
        """
        self.odometer = data[2] * 65536 + data[3] * 256 + data[4]
        self.out_temp = data[6] / 2 - 39.5
        self.lamps['reverse'] = bool(data[7] & 0x80)
        self.lamps['right'] = bool(data[7] & 0x02)
        self.lamps['left'] = bool(data[7] & 0x01)
    
    def id_0x120(self, data):
        """
        Warning log
        """
        pass
    
    def id_0x128(self, data):
        """
        Lamps 
        """
        self.lamps['belt_fl'] = bool(data[0] & 0x40)
        self.lamps['doors'] = bool(data[1] & 0x10)
        self.lamps['sidelight'] = bool(data[4] & 0x80)
        self.lamps['beam_l'] = bool(data[4] & 0x40)
        self.lamps['beam_h'] = bool(data[4] & 0x20)
        self.lamps['fog_f'] = bool(data[4] & 0x10)
        self.lamps['fog_r'] = bool(data[4] & 0x08)
        self.lamps['lefti'] = bool(data[4] & 0x04)
        self.lamps['righti'] = bool(data[4] & 0x02)

    def id_0x1a1(self, data):
        """
        Message
        """
        self.show_message = bool(data[2] & 0x80)
        if data[0] == 0x80:
            self.message_id = data[1]

    def id_0x276(self, data):
        """
        Date & Time
        """
        pass

    def id_0x336(self, data):
        """
        First 3 vin digits
        """
        self.vin1 = bytes(data[:3]).decode()

    def id_0x3b6(self, data):
        """
        Middle 6 vin digits
        """
        self.vin2 = bytes(data[:6]).decode()

    def id_0x2b6(self, data):
        """
        Last 8 vin digits
        """
        self.vin3 = bytes(data[:8]).decode()

    def id_0x2e1(self, data):
        self.funcs = (data[0] << 16) + (data[1] << 8) + data[2]

    def id_0x361(self, data):
        """
        Car settings
        """
        pass

