#!/bin/sh

# Citrocan
# Copyright (c) 2016 sisoftrg
# The MIT License (MIT)

#buildozer android debug
java -jar signapk.jar testkey.x509.pem testkey.pk8 Citrocan-1.0-debug.apk Citrocan-1.0-debug-signed.apk
adb install -r Citrocan-1.0-debug-signed.apk
