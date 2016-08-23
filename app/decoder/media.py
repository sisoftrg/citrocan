from decoder.base import Decoder


class RD45Decoder(Decoder):
    __slots__ = ['enabled', 'silence', 'have_changer',
                 'volume', 'vol_change', 'track_intro', 'random', 'repeat',
                 'rds_alt', 'want_rdtxt', 'balance_lr', 'show_balance_lr',
                 'balance_rf', 'show_balance_rf', 'bass', 'show_bass', 'treble',
                 'show_treble', 'loudness', 'show_loudness', 'autovol',
                 'show_autovol', 'ambience', 'ambience_show', 'track_author',
                 'track_name', 'rdtxt', 'pty_scan', 'radio_scan', 'rds_scan',
                 'ast_scan', 'show_radios', 'radio_mem', 'radio_band',
                 'radio_freq', 'cd_disk', 'cd_tracks', 'cd_len', 'cd_mp3',
                 'track_num', 'track_len', 'track_time', 'rkeys']

    source = ''

    sources = ['---', 'Tuner', 'CD', 'CD Changer', 'Input AUX 1', 'Input AUX 2',
               'USB', 'Bluetooth']

    ambs = {0x03: 'None', 0x07: 'Classical', 0x0b: 'Jazz-Blues',
            0x0f: 'Pop-Rock', 0x13: 'Vocal', 0x17: 'Techno'}
    rkeys = {}

    bands = ['---', ' FM1', ' FM2', 'DAB', 'FMAST', 'AM', 'AMLW', '---']

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

    def id_0x0a4(self, data):
        """
        Current cd track, multiframe
        """
        dd = self.parse_mf(0x0a4, len(data), data)
        if not dd:
            return False
        cd = dd[1]
        # cd track info
        # got mf: 0xa4 20009801546865204372616e626572726965730000000000416e696d616c20496e7374696e63740000000000
        # got mf: 0xa4 2000000000

        # radiotext
        # got mf: 0xa4 10000000544154415220524144494f53202020202020202020202020414c4c49202d2052454b4c414d41202838353532292039322d30302d383220202020202020202020
        # got mf: 0xa4 10000000544154415220524144494f53492038372e3520464d204348414c4c49202d2052454b4c414d41202838353532292039322d30302d383220202020202020202020
        # got mf: 0xa4 1000000000

        page = (data[0] >> 4) & 0x0f
        if page == 1:
            self.rdtxt = self.get_str(data[4:])
        elif page == 2:
            ha = bool(data[2] & 0x10)
            self.track_author = ha and self.get_str(data[4:24]) or ''
            self.track_name = self.get_str(ha and data[24:44] or data[4:24])

    def id_0x125(self, data):
        """
        Track list, multiframe
        """
        dd = self.parse_mf(0x125, len(data), data)
        if not dd:
            return False
        cd = dd[1]
        # cd list
        # got mf: 0x125 900100108111524f4f5400000000000000000000000000000000
        # got mf: 0x125 986f5d41f120696c6c5f6e696e6f5f2d5f686f775f63616e5f696b6f726e2d6b6973732d6d73742e6d70330000006d797a756b612e72755f332e5f42756c6c65745f6d797a756b612e72755f372e5f5374617469632d
        # got mf: 0x125 00

        # radio list, band
        # got mf: 0x125 100100103130332e3230000000
        # got mf: 0x125 20500000353331000000000000353331000000000000353331000000000000363330000000000000353331000000000000353331000000000000
        # got mf: 0x125 201000004543484f204d534b90464d2039302e3920903130312e354d485ab0504c555320202020903130362e393000002035392d33342d3233b0
        # got mf: 0x125 20200000464d2039302e39209031363a31363a333790343634375f31335fb03130332e363000000039302e36300000000044414e434520202090
        # got mf: 0x125 40200000464d2039302e39209031363a31363a333790343634375f31335fb03130332e363000000039302e36300000000044414e434520202090
        # got mf: 0x125 00

        page = (data[0] >> 4) & 0x0f

    def id_0x225(self, data):
        """
        Radio freq
        """
        freq = None
        if len(data) == 6:  # b7, from autowp docs
            self.radio_mem = data[0] & 7
            self.radio_band = self.bands[(data[1] >> 5) & 7]
            freq = (data[1] & 0x0f) * 256 + data[2]

        elif len(data) == 5:  # b3/b5
            self.pty_scan = bool(data[0] & 0x01)
            self.radio_scan = bool(data[0] & 0x02)
            self.rds_scan = bool(data[0] & 0x04)
            self.ast_scan = bool(data[0] & 0x08)
            self.show_radios = bool(data[0] & 0x80)
            self.radio_mem = (data[1] >> 4) & 7
            self.radio_band = self.bands[(data[2] >> 4) & 7]
            freq = (data[3] & 0x0f) * 256 + data[4]

        if self.radio_band in ('AMMW', 'AMLW'):
            self.radio_freq = '%d KHz' % freq
        else:
            self.radio_freq = '%.2f MHz' % (freq * 0.05 + 50)

    def id_0x325(self, data):
        """
        CD tray info
        """
        self.cd_disk = data[1] & 0x83

    def id_0x365(self, data):
        """
        CD disk info
        """
        self.cd_tracks = data[0]
        self.cd_len = '%02d:%02d' % (data[1], data[2]) if data[1] != 0xff else \
            '--:--'
        self.cd_mp3 = bool(data[3] & 0x01)

    def id_0x3a5(self, data):
        """
        CD tarck info
        """
        self.track_num = data[0]
        self.track_len = '%02d:%02d' % (data[1], data[2]) if data[1] != 0xff \
            else '--:--'
        self.track_time = '%02d:%02d' % (data[3], data[4]) if data[3] != 0xff \
            else '--:--'

    def id_0x21f(self, data):
        """
        Remote keys under wheel
        """
        self.rkeys['fwd'] = bool(data[0] & 0x80)
        self.rkeys['rew'] = bool(data[0] & 0x40)
        self.rkeys['volup'] = bool(data[0] & 0x08)
        self.rkeys['voldn'] = bool(data[0] & 0x04)
        self.rkeys['src'] = bool(data[0] & 0x02)
        self.rkeys['scroll'] = data[1]