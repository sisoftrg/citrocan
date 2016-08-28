from decoder.base import Decoder


class BSIDecoder(Decoder):
    funcs = 0
    rpm = 0
    speed = 0
    odometer = 0
    power = 0
    economy = 0
    lighting = 0
    brightness = 0
    ignition = 0
    lamps = {}
    out_temp = 0
    show_message = False
    message_id = 0
    vin1 = ""
    vin2 = ""
    vin3 = ""

    msgs = {0x00: 'Diagnosis ok', 0x01: 'Engine temperature too high', 0x03: 'Coolant circuit level too low', 0x04: 'Check engine oil level', 0x05: 'Engine oil pressure too low',
            0x08: 'Braking system faulty', 0x0A: 'Air suspension ok (picture)', 0x0B: 'Door, boot, bonnet and fuel tank open', 0x0D: 'Tyre puncture(s) detected',
            0x0F: 'Risk of particle filter blocking', 0x11: 'Suspension faulty: max.speed 90 km/h', 0x12: 'Suspension faulty', 0x13: 'Power steering faulty', 0x14: '10km/h!',
            0x61: 'Handbrake on', 0x62: 'Handbrake off', 0x64: 'Handbrake control faulty: auto handbrake activated', 0x67: 'Brake pads worn', 0x68: 'Handbrake faulty',
            0x69: 'Mobile deflector faulty', 0x6A: 'ABS braking system faulty', 0x6B: 'ESP / ASR system faulty', 0x6C: 'Suspension faulty', 0x6D: 'Power steering faulty',
            0x6E: 'Gearbox faulty', 0x6F: 'Cruise control system faulty', 0x73: 'Ambient brightness sensor faulty', 0x74: 'Sidelamp bulb(s) faulty',
            0x75: 'Automatic headlamp adjustment faulty', 0x76: 'Directional headlamps faulty', 0x78: 'Airbag faulty', 0x79: 'Active bonnet faulty', 0x7A: 'Gearbox faulty',
            0x7B: 'Apply foot on brake and lever in position "N"', 0x7D: 'Presence of water in diesel fuel filter', 0x7E: 'Engine management system faulty',
            0x7F: 'Depollution system faulty', 0x81: 'Particle filter additive level too low', 0x83: 'Electronic anti-theft faulty', 0x86: 'Right hand side door faulty',
            0x87: 'Left hand side door faulty', 0x89: 'Space measuring system faulty', 0x8A: 'Battery charge or electrical supply faulty', 0x8D: 'Tyre pressure(s) too low',
            0x92: 'Warning!', 0x95: 'Info!', 0x96: 'Info!', 0x97: 'Anti-wander system lane-crossing warning device faulty', 0x9D: 'Foglamp bulb(s) faulty',
            0x9E: 'Direction indicator(s) faulty', 0xA0: 'Sidelamp bulb(s) faulty', 0xA1: 'Parking lamps active', 0xCD: 'Cruise control not possible: speed too low',
            0xCE: 'Control activation not possible: enter the speed', 0xD1: 'Active bonnet deployed', 0xD2: 'Front seat belts not fastened',
            0xD3: 'Rear right hand passenger seat belts fastened', 0xD7: 'Place automatic gearbox in position "P"', 0xD8: 'Risk of ice', 0xD9: 'Handbrake!',
            0xDE: 'Door, boot, bonnet and fuel tank open', 0xDF: 'Screen wash fluid level too low', 0xE0: 'Fuel level too low', 0xE1: 'Fuel circuit deactivated',
            0xE3: 'Remote control battery flat', 0xE4: 'Check and re-initialise tyre pressure', 0xE5: 'Tyre pressure(s) not monitored',
            0xE7: 'High speed, check tyre pressures correct', 0xE8: 'Tyre pressure(s) too low', 0xEA: 'Hands-free starting system faulty',
            0xEB: 'Starting phase has failed (consult handbook)', 0xEC: 'Prolonged starting in progress', 0xED: 'Starting impossible: unlock the steering',
            0xEF: 'Remote control detected', 0xF0: 'Diagnosis in progress...', 0xF1: 'Diagnosis completed', 0xF7: 'Rear LH passenger seatbelt unfastened',
            0xF8: 'Rear center passenger seatbelt unfastened', 0xF9: 'Rear RH passenger seatbelt unfastened'}


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
        """
        Status of functions
        """
        self.funcs = (data[0] << 16) + (data[1] << 8) + data[2]

    def id_0x361(self, data):
        """
        Car settings
        """
        pass

