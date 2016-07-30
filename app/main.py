#!/usr/bin/python

# Citrocan
# Copyright (c) 2016 sisoftrg
# The MIT License (MIT)

import time
import threading

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, BooleanProperty

try:
    from jnius import autoclass
    serial = None
except ImportError:
    import serial
    autoclass = None

from kivy_decoder import KivyDecoder as Decoder

kivy.require('1.9.0')
__version__ = '1.0'

BtName = "citr"
Port = "/dev/ttyUSB0"
#Port = "/dev/rfcomm0"
FromFile = None  # "../cl-start"


class Citrocan(App):

    dec = None
    update = False
    stop_ev = threading.Event()
    d_time = StringProperty()
    d_date = StringProperty()
    d_temp = StringProperty()
    d_vol = StringProperty()
    d_band = StringProperty()
    d_name = StringProperty()
    d_info = StringProperty()
    d_title = StringProperty()
    d_memch = StringProperty()
    d_dx = StringProperty()
    d_rds = StringProperty()
    d_rds_ok = BooleanProperty()
    d_ta = StringProperty()
    d_ta_ok = BooleanProperty()
    d_pty = StringProperty()
    d_pty_ok = BooleanProperty()
    d_ptyname = StringProperty()
    d_rdtxt_rnd = StringProperty()
    d_reg = StringProperty()
    d_loud = StringProperty()
    d_icon = StringProperty("icon")
    d_volbar = NumericProperty()
    d_alert = StringProperty()
    d_debug = StringProperty()

    def build(self):
        Window.size = (1024, 520)
        self.dec = Decoder(self.prop_set)
        Clock.schedule_interval(self.update_time, .5)
        Clock.schedule_interval(self.visualize, .4)
        thr = threading.Thread(target=self.get_candata)
        thr.setDaemon(True)
        thr.start()

    def update_time(self, *_):
        self.d_time = time.strftime("%H %M" if ':' in self.d_time else "%H:%M")
        self.d_date = time.strftime("%a %d/%m/%Y")

    def visualize(self, *_):
        if self.dec and self.update:
            self.update = False
            self.dec.visualize()

    def prop_set(self, var, val):
        if self.__getattribute__("d_" + var) != val:
            self.__setattr__("d_" + var, val)

    def file_receiver(self, on_recv, fname):
        old_tm = .0
        sp = open(fname, "r")
        for ln in sp:
            if self.stop_ev.is_set():
                break
            buf = ln.strip()
            # print("got:", buf)
            if len(buf):
                tm, _, b = buf.partition(' ')
                if old_tm:
                    time.sleep(float(tm) - old_tm)
                old_tm = float(tm)
                if b[0] in ('R', 'S'):
                    on_recv(b)
        sp.close()
        print("EOF, stop playing.")

    def serial_receiver(self, on_recv):
        sp = None
        while not self.stop_ev.is_set():
            if not sp:
                buf = []
                ready = False
                try:
                    sp = serial.Serial(port=Port, baudrate=460800, timeout=1)
                except (ValueError, serial.SerialException) as e:
                    print("can't open serial:", e)
                    if self.dec.connected:
                        self.dec.connected = False
                        self.update = True

            if sp and not ready:
                try:
                    sp.write("i0\r\n".encode())
                except serial.SerialTimeoutException as e:
                    print("can't write to serial:", e)
                    time.sleep(1)

            if sp:
                while not self.stop_ev.is_set():
                    try:
                        r = sp.read(1)
                    except serial.SerialException:
                        sp.close()
                        sp = None
                        r = None
                    if not r:
                        break
                    if r == b'\n':
                        # print("got:", ''.join(buf))
                        if len(buf):
                            if buf[0] in ('R', 'S'):
                                on_recv(''.join(buf))
                            elif buf[0] == 'I':
                                ready = True
                            buf = []
                    elif r >= b' ':
                        buf.append(r.decode())
            else:
                time.sleep(1)

        if sp:
            sp.close()

    def bt_receiver(self, on_recv):
        BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        UUID = autoclass('java.util.UUID')

        sock = None
        while not self.stop_ev.is_set():
            if not sock:
                buf = []
                send = None
                recv = None
                ready = False
                if self.dec.connected:
                    self.dec.connected = False
                    self.update = True
                paired = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
                for dev in paired:
                    if dev.getName() == BtName:
                        sock = dev.createRfcommSocketToServiceRecord(UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                        recv = sock.getInputStream()
                        send = sock.getOutputStream()
                        print("wait for connection")
                        try:
                            sock.connect()
                        except Exception as e:
                            sock.close()
                            sock = None
                            print("can't connect bluetooth:", e)
                        break

            if sock and not ready:
                print("sending init")
                send.write("i0\r\n")
                send.flush()

            if sock:
                while not self.stop_ev.is_set():
                    try:
                        r = recv.read()
                    except Exception as e:
                        print("can't read from bluetooth:", e)
                        sock.close()
                        sock = None
                        r = None
                    if not r:
                        break
                    if r == 13:
                        # print("got:", ''.join(buf))
                        if len(buf):
                            if buf[0] in ('R', 'S'):
                                on_recv(''.join(buf))
                            elif buf[0] == 'I':
                                ready = True
                            buf = []
                    elif r >= 32:
                        buf.append(chr(r))

            else:
                time.sleep(1)

        if sock:
            sock.close()

    def get_candata(self):
        self.dec.connected = False
        self.update = True

        def on_recv(buf):
            # print("recv:", buf)
            try:
                flds = buf.split()
                cid = int(flds[1], 16)
                clen = int(flds[2])
                cflds = []
                for n in range(clen):
                    cflds.append(int(flds[n + 3], 16))
                if self.dec and self.dec.decode(cid, clen, cflds):
                    self.dec.connected = True
                    self.update = True
            except (TypeError, ValueError, IndexError) as e:
                print("can't decode:", buf, e)

        if FromFile:
            self.file_receiver(on_recv, FromFile)
        elif autoclass:
            self.bt_receiver(on_recv)
        else:
            self.serial_receiver(on_recv)

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        self.stop_ev.set()


if __name__ == '__main__':
    Citrocan().run()
