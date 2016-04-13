#!/usr/bin/python

# Citrocan
# Copyright (c) 2016 sisoftrg
# The MIT License (MIT)

import time
import threading
import serial

import kivy
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty

from decoder import Decoder

kivy.require('1.9.0')
__version__ = '1.0'

Port = "/dev/ttyUSB0"


class Citrocan(App):

    stop_ev = threading.Event()
    d_time = StringProperty()
    d_date = StringProperty()
    d_temp = StringProperty("[b]——[/b]°F")
    d_vol = StringProperty()
    d_band = StringProperty()
    d_name = StringProperty()
    d_info = StringProperty()
    d_title = StringProperty()
    d_memch = StringProperty()
    d_rds = StringProperty()
    d_ta = StringProperty()
    d_rdtxt_rnd = StringProperty()
    d_reg = StringProperty()
    d_loud = StringProperty()
    d_icon = StringProperty("icon")
    d_volbar = NumericProperty()

    def build(self):
        Window.size = (531, 131)
        Clock.schedule_interval(self.update_time, .5)
        threading.Thread(target=self.get_candata).start()

    def update_time(self, *_):
        self.d_time = time.strftime("%H %M" if ':' in self.d_time else "%H:%M")
        self.d_date = time.strftime("%a %d/%m/%Y")

    @mainthread
    def safe_set(self, var, val):
        if self.__getattribute__("d_" + var) != val:
            self.__setattr__("d_" + var, val)

    def get_candata(self):
        sp = None
        dec = Decoder(self.safe_set)
        while not self.stop_ev.is_set():
            if not sp:
                try:
                    buf = ''
                    ready = False
                    sp = serial.Serial(port=Port, baudrate=460800, timeout=1)
                except (ValueError, serial.SerialException) as e:
                    print("can't open serial:", e)

            if sp and not ready:
                try:
                    sp.write("i1\r\n".encode())
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
                        #print("got:", buf)
                        if len(buf) and buf[0] == 'R':
                            try:
                                flds = buf.split()
                                cid = int(flds[1], 16)
                                clen = int(flds[2])
                                cflds = []
                                for n in range(clen):
                                    cflds.append(int(flds[n + 3], 16))
                                dec.decode(cid, clen, cflds)
                            except (TypeError, ValueError, IndexError) as e:
                                print("can't decode:", buf, e)
                        elif len(buf) and buf[0] == 'I':
                            ready = True
                        buf = ""
                    elif r >= b' ':
                        buf += r.decode()
            else:
                time.sleep(1)

        if sp:
            sp.close()

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        self.stop_ev.set()


if __name__ == '__main__':
    Citrocan().run()
