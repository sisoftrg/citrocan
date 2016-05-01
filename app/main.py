#!/usr/bin/python

# Citrocan
# Copyright (c) 2016 sisoftrg
# The MIT License (MIT)

import time
import threading

import kivy
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, BooleanProperty

try:
    from jnius import autoclass
    serial = None
except ImportError:
    import serial
    autoclass = None

from decoder import Decoder

kivy.require('1.9.0')
__version__ = '1.0'

BtName = "citr"
Port = "/dev/ttyUSB0"
#Port = "/dev/rfcomm0"


class Citrocan(App):

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

    def build(self):
        Window.size = (531, 131)
        Clock.schedule_interval(self.update_time, .5)
        thr = threading.Thread(target=self.get_candata)
        thr.setDaemon(True)
        thr.start()

    def update_time(self, *_):
        self.d_time = time.strftime("%H %M" if ':' in self.d_time else "%H:%M")
        self.d_date = time.strftime("%a %d/%m/%Y")

    @mainthread
    def safe_set(self, var, val):
        if self.__getattribute__("d_" + var) != val:
            self.__setattr__("d_" + var, val)

    def serial_receiver(self, on_recv):
        sp = None
        while not self.stop_ev.is_set():
            if not sp:
                buf = ''
                ready = False
                try:
                    sp = serial.Serial(port=Port, baudrate=460800, timeout=1)
                except (ValueError, serial.SerialException) as e:
                    print("can't open serial:", e)
                    self.safe_set('alert', "No connection")

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
                        # print("got:", buf)
                        if len(buf):
                            if buf[0] in ('R', 'S'):
                                on_recv(buf)
                            elif buf[0] == 'I':
                                ready = True
                            buf = ''
                    elif r >= b' ':
                        buf += r.decode()
            else:
                time.sleep(1)

        if sp:
            sp.close()

    def bt_receiver(self, on_recv):
        BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        #BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
        #BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
        UUID = autoclass('java.util.UUID')

        sock = None
        while not self.stop_ev.is_set():
            if not sock:
                buf = ''
                send = None
                recv = None
                ready = False
                self.safe_set('alert', "No connection")
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
                send.write("i1\r\n")
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
                        # print("got:", buf)
                        if len(buf):
                            if buf[0] in ('R', 'S'):
                                on_recv(buf)
                            elif buf[0] == 'I':
                                ready = True
                            buf = ''
                    elif r >= 32:
                        buf += chr(r)

            else:
                time.sleep(1)

        if sock:
            sock.close()

    def get_candata(self):
        dec = Decoder(self.safe_set)

        def on_recv(buf):
            print("recv:", buf)
            try:
                flds = buf.split()
                cid = int(flds[1], 16)
                clen = int(flds[2])
                cflds = []
                for n in range(clen):
                    cflds.append(int(flds[n + 3], 16))
                if dec.decode(cid, clen, cflds):
                    dec.visualize()
            except (TypeError, ValueError, IndexError) as e:
                print("can't decode:", buf, e)

        if autoclass:
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
