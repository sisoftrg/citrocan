# Citrocan
# Copyright (c) 2016 sisoftrg
# The MIT License (MIT)


class Decoder(object):

    cb = {}
    mfs = {}
    enabled = False
    silence = False
    source = ""
    srcs = ['---', 'Tuner', 'CD', 'CD Changer', 'Input AUX 1', 'Input AUX 2', 'USB', 'Bluetooth']
    have_changer = False
    cd_disk = 0
    volume = 0
    vol_change = False
    track_intro = False
    random = False
    repeat = False
    rds_alt = False
    want_rdtxt = False
    balance_lr = 0
    show_balance_lr = False
    balance_rf = 0
    show_balance_rf = False
    bass = 0
    show_bass = False
    treble = 0
    show_treble = False
    loudness = False
    show_loudness = False
    autovol = 0
    show_autovol = 0
    ambience = ""
    ambs = {0x03: 'None', 0x07: 'Classical', 0x0b: 'Jazz-Blues', 0x0f: 'Pop-Rock', 0x13: 'Vocal', 0x17: 'Techno'}
    ambience_show = False
    radio_mem = 0
    radio_band = ""
    bands = ['---', ' FM1', ' FM2', 'DAB', 'FMAST', 'AMMW', 'AMLW', '---']
    radio_freq = ""
    radio_ast = False
    radio_scan = False
    want_rds = False
    have_rds = False
    want_ta = False
    have_ta = False
    traffic = False
    want_reg = False
    want_pty = False
    show_pty = False
    pty_mode = 0
    pty_sel = 0
    pty_cur = ""
    ptys = {0x00: 'Deactivate', 0x01: 'News', 0x02: 'Affairs', 0x03: 'Info', 0x04: 'Sport', 0x05: 'Educate', 0x06: 'Drama', 0x07: 'Culture',
            0x08: 'Science', 0x09: 'Varied', 0x0A: 'Pop M', 0x0B: 'Rock M', 0x0C: 'Easy M', 0x0D: 'Light M', 0x0E: 'Classics', 0x0F: 'Other M',
            0x10: 'Weather', 0x11: 'Finance', 0x12: 'Children', 0x13: 'Social', 0x14: 'Religion', 0x15: 'Phone In', 0x16: 'Travel',
            0x17: 'Leisure', 0x18: 'Jazz', 0x19: 'Country', 0x1A: 'Nation M', 0x1B: 'Oldies', 0x1C: 'Folk M', 0x1D: 'Document'}
    rds_name = ""
    cd_tracks = 0
    cd_len = ""
    cd_mp3 = 0
    track_num = 0
    track_time = ""
    track_len = ""
    track_name = ""
    track_author = ""
    rdtxt = ""
    key = {}

    def __init__(self, ss):
        self.ss = ss

    @staticmethod
    def get_str(b):
        ba = bytes(b).strip(b'\0')
        try:
            s = ba.decode('utf8')
        except UnicodeDecodeError:
            try:
                s = ba.decode('cp1251')
            except:
                s = ""
        return s.strip()

    def parse_mf(self, ci, cl, cd):
        typ = (cd[0] & 0xf0) >> 4
        arg = cd[0] & 0x0f
        if typ == 0:  # single
            # print("got mf:", hex(ci), ''.join('{:02x}'.format(x) for x in cd[1:min(1 + arg, cl)]))
            return (arg, cd[1:min(1 + arg, cl)])
        elif typ == 1:  # first
            fl = arg * 256 + cd[1]
            el = fl - (cl - 2)
            self.mfs[ci] = [fl, el, cd[2:cl]]
        elif typ == 2:  # consecutive. TODO: check frame order!
            if ci not in self.mfs:
                return None
            el = self.mfs[ci][1]
            if el > cl - 1:
                self.mfs[ci][1] -= cl - 1
                self.mfs[ci][2] += cd[1:cl]
            else:
                fl = self.mfs[ci][0]
                d = self.mfs[ci][2] + cd[1:min(cl, el + 2)]
                del self.mfs[ci]
                # print("got mf:", hex(ci), ''.join('{:02x}'.format(x) for x in d))
                return (fl, d)
        elif typ == 3:  # flow, packets not for us
            pass
        return None

    def decode(self, ci, cl, cd):
        if ci in self.cb and cd == self.cb[ci]:
            return
        self.cb[ci] = cd

        if ci == 0x0a4:  # current cd track, multiframe
            dd = self.parse_mf(ci, cl, cd)
            if not dd:
                return
            cd = dd[1]
            # cd track info
            #got mf: 0xa4 20009801546865204372616e626572726965730000000000416e696d616c20496e7374696e63740000000000
            #got mf: 0xa4 2000000000

            # radiotext
            #got mf: 0xa4 10000000544154415220524144494f53202020202020202020202020414c4c49202d2052454b4c414d41202838353532292039322d30302d383220202020202020202020
            #got mf: 0xa4 10000000544154415220524144494f53492038372e3520464d204348414c4c49202d2052454b4c414d41202838353532292039322d30302d383220202020202020202020
            #got mf: 0xa4 1000000000

            typ = (cd[0] >> 4) & 3
            if typ == 2:
                ha = bool(cd[2] & 0x10)
                self.track_author = ha and self.get_str(cd[4:24]) or ""
                self.track_name = self.get_str(ha and cd[24:44] or cd[4:24])
            elif typ == 1:
                print("ok", cd)
                self.rdtxt = self.get_str(cd[4:])

        elif ci == 0x125:  # track list, multiframe
            dd = self.parse_mf(ci, cl, cd)
            if not dd:
                return
            cd = dd[1]
            # cd list
            #got mf: 0x125 900100108111524f4f5400000000000000000000000000000000
            #got mf: 0x125 986f5d41f120696c6c5f6e696e6f5f2d5f686f775f63616e5f696b6f726e2d6b6973732d6d73742e6d70330000006d797a756b612e72755f332e5f42756c6c65745f6d797a756b612e72755f372e5f5374617469632d
            #got mf: 0x125 00

            # radio list, band
            #got mf: 0x125 100100103130332e3230000000
            #got mf: 0x125 20500000353331000000000000353331000000000000353331000000000000363330000000000000353331000000000000353331000000000000
            #got mf: 0x125 201000004543484f204d534b90464d2039302e3920903130312e354d485ab0504c555320202020903130362e393000002035392d33342d3233b0
            #got mf: 0x125 20200000464d2039302e39209031363a31363a333790343634375f31335fb03130332e363000000039302e36300000000044414e434520202090
            #got mf: 0x125 40200000464d2039302e39209031363a31363a333790343634375f31335fb03130332e363000000039302e36300000000044414e434520202090
            #got mf: 0x125 00



        elif ci == 0x131:  # cmd to cd changer
            pass

        elif ci == 0x165:  # radio status
            self.enabled = bool(cd[0] & 0x80)
            self.silence = bool(cd[0] & 0x20)
            self.source = self.srcs[(cd[2] >> 4) & 7]
            self.have_changer = bool(cd[1] & 0x10)
            #self.cd_disk = ((cd[1] >> 5) & 3) ^ 1  # for b7?

        elif ci == 0x1a5:  # volume
            self.volume = cd[0] & 0x1f
            self.vol_change = bool(cd[0] & 0x80)

        elif ci == 0x1e0:  # radio settings
            self.track_intro = bool(cd[0] & 0x20)
            self.random = bool(cd[0] & 0x04)
            self.repeat = bool(cd[1] & 0x80)
            self.rds_alt = bool(cd[2] & 0x20)
            self.want_rdtxt = bool(cd[4] & 0x20)

        elif ci == 0x1e5:  # audio settings
            self.balance_lr = ((cd[0] + 1) & 0x0f) - (cd[0] ^ 0x40 & 0x40) >> 2
            self.show_balance_lr = bool(cd[0] & 0x80)
            self.balance_rf = ((cd[1] + 1) & 0x0f) - (cd[1] ^ 0x40 & 0x40) >> 2
            self.show_balance_rf = bool(cd[1] & 0x80)
            self.bass = ((cd[2] + 1) & 0x0f) - (cd[2] ^ 0x40 & 0x40) >> 2
            self.show_bass = bool(cd[2] & 0x80)
            self.treble = ((cd[4] + 1) & 0x0f) - (cd[4] ^ 0x40 & 0x40) >> 2
            self.show_treble = bool(cd[4] & 0x80)
            self.loudness = bool(cd[5] & 0x40)
            self.show_loudness = bool(cd[5] & 0x80)
            self.autovol = cd[5] & 7
            self.show_autovol = bool(cd[5] & 0x10)
            self.ambience = self.ambs.get(cd[6] & 0x1f, "Unk:" + hex(cd[6] & 0x1f))
            self.ambience_show = bool(cd[6] & 0x40)

        elif ci == 0x225:  # radio freq
            if cl == 6:  # b7, from autowp docs
                self.radio_mem = cd[0] & 7
                self.radio_band = self.bands[(cd[1] >> 5) & 7]
                freq = (cd[1] & 0x0f) * 256 + cd[2]
                self.radio_ast = False
                self.radio_scan = False

            elif cl == 5:  # b3/b5
                self.radio_mem = (cd[1] >> 4) & 7
                self.radio_band = self.bands[(cd[2] >> 4) & 7]
                freq = (cd[3] & 0x0f) * 256 + cd[4]
                self.radio_ast = bool(cd[0] & 0x08)
                self.radio_scan = bool(cd[0] & 0x02)

            if self.radio_band in ('AMMW', 'AMLW'):
                self.radio_freq = "%d KHz" % freq
            else:
                self.radio_freq = "%.2f MHz" % (freq * 0.05 + 50)

        elif ci == 0x265:  # rds
            self.want_rds = bool(cd[0] & 0x80)
            self.have_rds = bool(cd[0] & 0x20)
            self.want_ta = bool(cd[0] & 0x10)
            self.have_ta = bool(cd[0] & 0x04)
            self.traffic = bool(cd[0] & 0x02)
            self.want_reg = bool(cd[0] & 0x01)
            self.want_pty = bool(cd[1] & 0x80)
            self.show_pty = bool(cd[1] & 0x40)
            self.pty_mode = (cd[1] >> 4) & 3
            self.pty_sel = cd[2]
            self.pty_cur = self.pty_mode in (1, 2) and cd[3] and self.ptys.get(cd[3], "Unk:" + hex(cd[3])) or ""

        elif ci == 0x2a5:  # rds title
            self.rds_name = self.get_str(cd) if cd[0] != 0 else None

        elif ci == 0x2e5:  # hz
            pass

        elif ci == 0x325:  # cd tray info
            self.cd_disk = cd[1] & 0x83

        elif ci == 0x365:  # cd disk info
            self.cd_tracks = cd[0]
            self.cd_len = "%02d:%02d" % (cd[1], cd[2]) if cd[1] != 0xff else "--:--"
            self.cd_mp3 = bool(cd[3] & 0x01)

        elif ci == 0x3a5:  # cd track info
            self.track_num = cd[0]
            self.track_len = "%02d:%02d" % (cd[1], cd[2]) if cd[1] != 0xff else "--:--"
            self.track_time = "%02d:%02d" % (cd[3], cd[4]) if cd[3] != 0xff else "--:--"

        elif ci == 0x3e5:  # keypad
            self.key['menu'] = bool(cd[0] & 0x40)
            self.key['tel'] = bool(cd[0] & 0x10)
            self.key['clim'] = bool(cd[0] & 0x01)
            self.key['trip'] = bool(cd[1] & 0x40)
            self.key['audio'] = bool(cd[1] & 0x01)
            self.key['ok'] = bool(cd[2] & 0x40)
            self.key['esc'] = bool(cd[2] & 0x10)
            self.key['dark'] = bool(cd[2] & 0x04)
            self.key['up'] = bool(cd[5] & 0x40)
            self.key['down'] = bool(cd[5] & 0x10)
            self.key['right'] = bool(cd[5] & 0x04)
            self.key['left'] = bool(cd[5] & 0x01)

        elif ci == 0x520:  # hz
            pass

        elif ci == 0x5e0:  # hw/sw radio info
            pass

        tuner = self.source == 'Tuner' and self.enabled
        cd = self.source in ('CD', 'CD Changer') and self.enabled
        aux = 'AUX' in self.source and self.enabled

        if not self.enabled:
            self.ss('icon', 'icon')
            self.ss('name', 'Disabled :(')

        elif aux:
            self.ss('icon', 'linein')
            self.ss('name', self.source)

        elif tuner:
            self.ss('icon', 'radio')
            self.ss('name', self.traffic and "Traffic" or self.rds_name or self.radio_freq)

        elif cd:
            self.ss('icon', self.cd_mp3 and 'cdmp3' or 'cdaudio')
            self.ss('name', self.cd_disk in (1, 3) and ('Track %d/%d' % (self.track_num, self.cd_tracks)) or "Wait...")

        self.ss('band', tuner and self.radio_band or "")
        self.ss('info', tuner and self.rds_name and self.radio_freq or
                (cd and ("» %s%s" % (self.track_time, self.track_len != "--:--" and " / " + self.track_len or "")) or ""))
        self.ss('memch', tuner and self.radio_mem and str(self.radio_mem) or "")
        self.ss('ta', self.enabled and self.want_ta and "TA" or "")
        self.ss('ta_ok', tuner and self.have_ta)
        self.ss('pty', self.enabled and self.want_pty and "PTY" or "")
        self.ss('ptyname', tuner and self.enabled and self.rdtxt == "" and self.pty_cur or "")
        self.ss('reg', tuner and self.want_reg and "REG" or "")
        self.ss('rds', tuner and self.want_rds and "RDS" or "")
        self.ss('rds_ok', tuner and self.have_rds)
        self.ss('rdtxt_rnd', tuner and self.want_rdtxt and "RDTXT" or (cd and self.random and "RDM" or (cd and self.track_intro and "INT" or "")))
        self.ss('loud', self.enabled and self.loudness and "LOUD" or "")
        self.ss('vol', self.enabled and ("Vol: [b]%d[/b]" % self.volume) or "")
        self.ss('volbar', self.enabled and self.volume or 0)
        self.ss('title', cd and (self.track_name + (self.track_author and (" / %s" % self.track_author) or "")) or (tuner and self.rdtxt) or "")
