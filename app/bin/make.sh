#!/bin/sh

# Citrocan
# Copyright (c) 2016 sisoftrg
# The MIT License (MIT)

#buildozer android release
java -jar signapk.jar testkey.x509.pem testkey.pk8 Citrocan-1.0-release-unsigned.apk Citrocan-1.0-release-signed.apk
adb install -r Citrocan-1.0-release-signed.apk
