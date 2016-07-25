from decoder.base import Decoder


class RD45Decoder(Decoder):
    __slots__ = ['enabled', 'silence', 'source', 'have_changer',
                 'volume', 'vol_change', 'track_intro', 'random', 'repeat',
                 'rds_alt', 'want_rdtxt', 'balance_lr', 'show_balance_lr',
                 'balance_rf', 'show_balance_rf', 'bass', 'show_bass', 'treble',
                 'show_treble', 'loudness', 'show_loudness', 'autovol',
                 'show_autovol', 'ambience', 'ambience_show']

    sources = ['---', 'Tuner', 'CD', 'CD Changer', 'Input AUX 1', 'Input AUX 2',
               'USB', 'Bluetooth']

    ambs = {0x03: 'None', 0x07: 'Classical', 0x0b: 'Jazz-Blues',
            0x0f: 'Pop-Rock', 0x13: 'Vocal', 0x17: 'Techno'}

    def id_0x165(self, data):
        """
        Radio status
        """
        self.enabled = bool(data[0] & 0x80)
        self.silence = bool(data[0] & 0x20)
        self.source = self.sources[(data[2] >> 4) & 7]
        self.have_changer = bool(data[1] & 0x10)

    def id_0x1a5(self, data):
        """
        Volume
        """
        self.volume = data[0] & 0x1f
        self.vol_change = bool(data[0] & 0x80)

    def id_0x1e0(self, data):
        """
        Radio settings
        """
        self.track_intro = bool(data[0] & 0x20)
        self.random = bool(data[0] & 0x04)
        self.repeat = bool(data[1] & 0x80)
        self.rds_alt = bool(data[2] & 0x20)
        self.want_rdtxt = bool(data[4] & 0x20)

    def id_0x1e5(self, data):
        """
        Audio settings
        """
        self.balance_lr = ((data[0] + 1) & 0x0f) - (data[0] ^ 0x40 & 0x40) >> 2
        self.show_balance_lr = bool(data[0] & 0x80)
        self.balance_rf = ((data[1] + 1) & 0x0f) - (data[1] ^ 0x40 & 0x40) >> 2
        self.show_balance_rf = bool(data[1] & 0x80)
        self.bass = ((data[2] + 1) & 0x0f) - (data[2] ^ 0x40 & 0x40) >> 2
        self.show_bass = bool(data[2] & 0x80)
        self.treble = ((data[4] + 1) & 0x0f) - (data[4] ^ 0x40 & 0x40) >> 2
        self.show_treble = bool(data[4] & 0x80)
        self.loudness = bool(data[5] & 0x40)
        self.show_loudness = bool(data[5] & 0x80)
        self.autovol = data[5] & 7
        self.show_autovol = bool(data[5] & 0x10)
        self.ambience = self.ambs.get(data[6] & 0x1f,
                                      "Unk: %s" % hex(data[6] & 0x1f))
        self.ambience_show = bool(data[6] & 0x40)