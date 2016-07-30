# coding=utf-8
from decoder import DEFAULT_DECODERS
from decoder.base import DecoderGroup


class KivyDecoder(DecoderGroup):

    def __init__(self, ss):
        super(KivyDecoder, self).__init__(
            DEFAULT_DECODERS, proxy_attributes=True)
        self.ss = ss
        self.connected = False

    def visualize(self):

        tuner = self.source == 'Tuner' and self.enabled
        cd = self.source in ('CD', 'CD Changer') and self.enabled
        aux = 'AUX' in self.source and self.enabled

        if not self.enabled:
            self.ss('icon', 'icon')
            self.ss('name', 'Disabled')
            self.ss('title', '')

        elif aux:
            self.ss('icon', 'linein')
            self.ss('name', self.source)
            self.ss('title', '')

        elif tuner:
            self.ss('icon', 'radio')
            self.ss('name', (
            self.rds_scan or self.ast_scan or self.pty_scan) and "Wait..." or (
                    self.traffic and "Traffic" or self.rds_name or self.radio_freq))
            self.ss('title', self.pty_scan and self.pty_sel and (
            "PTY: " + self.ptys.get(self.pty_sel, "")) or (
                    self.rds_scan and "RDS search.." or
                    (self.ast_scan and (
                    self.radio_scan and "Autostore stations.." or "List in progress..")) or self.rdtxt))

        elif cd:
            self.ss('icon', self.cd_mp3 and 'cdmp3' or 'cdaudio')
            self.ss('name', self.source == 'CD' and (
            self.cd_disk in (1, 3) and ('Track %d/%d' % (
            self.track_num, self.cd_tracks)) or "Wait...") or "CD Changer")
            self.ss('title', self.track_name + (
            self.track_author and (" / %s" % self.track_author) or ""))

        else:
            self.ss('icon', 'icon')
            self.ss('name', self.source)
            self.ss('title', '')

        self.ss('band', tuner and self.radio_band or "")
        self.ss('info', tuner and self.rds_name and self.radio_freq or
                (cd and ("%s %s%s" % (
                self.cd_pause and "×" or "»", self.track_time,
                self.track_len != "--:--" and " / " + self.track_len or "")) or ""))
        self.ss('memch',
                tuner and not self.radio_scan and self.radio_mem and str(
                    self.radio_mem) or "")
        self.ss('dx', tuner and self.radio_scan and "DX" or "")
        self.ss('ta', self.enabled and self.want_ta and "TA" or "")
        self.ss('ta_ok', tuner and self.have_ta)
        self.ss('pty', self.enabled and self.want_pty and "PTY" or "")
        self.ss('pty_ok',
                tuner and self.pty_cur == self.ptys.get(self.pty_sel, ""))
        self.ss('ptyname',
                tuner and self.enabled and self.rdtxt == "" and self.pty_cur or "")
        self.ss('reg', tuner and self.want_reg and "REG" or "")
        self.ss('rds', tuner and self.want_rds and "RDS" or "")
        self.ss('rds_ok', tuner and self.have_rds)
        self.ss('rdtxt_rnd', tuner and self.want_rdtxt and "RDTXT" or (cd and (
        self.random and "RDM" or (
        self.track_intro and "INT" or (self.repeat and "RPT")))) or "")
        self.ss('loud', self.enabled and self.loudness and "LOUD" or "")
        self.ss('vol', self.enabled and ("Vol: [b]%d[/b]" % self.volume) or "")
        self.ss('volbar', self.enabled and self.volume or 0)
        self.ss('temp', self.out_temp and (
        "[b]%.0f[/b]°C" % self.out_temp) or "[b]——[/b]°F")
        self.ss('alert', not self.connected and "No connection" or (
        self.show_message and self.msgs.get(self.message_id, "") or ""))
        self.ss('debug',
                "rpm=%d speed=%d power=%dV odometer=%d\neconomy=%d lighting=%d bright=%d ignition=%d funcs=%06x\n\nlamps=%s\n\nkeys=%s" % (
                    self.rpm, self.speed, self.power, self.odometer,
                    self.economy, self.lighting, self.brightness, self.ignition,
                    self.funcs, str(self.lamps), str(self.rkeys)))

    def visualize_test(self):
        self.ss('icon', "icon")
        self.ss('name', "Name")
        self.ss('title', "Title")
        self.ss('band', "Band")
        self.ss('info', "Info")
        self.ss('memch', "0")
        self.ss('dx', "DX")
        self.ss('ta', "TA")
        self.ss('ta_ok', True)
        self.ss('pty', "PTY")
        self.ss('pty_ok', True)
        self.ss('ptyname', "PtyName")
        self.ss('reg', "REG")
        self.ss('rds', "RDS")
        self.ss('rds_ok', True)
        self.ss('rdtxt_rnd', "RDTXT")
        self.ss('loud', "LOUD")
        self.ss('vol', "Vol: [b]15[/b]")
        self.ss('volbar', 15)
        self.ss('temp', "[b]33[/b]°C")
        self.ss('alert', "")
        self.ss('debug', "some debug info")
