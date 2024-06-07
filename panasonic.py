# source: https://martinsuniverse.de/?Bastelprojekte___Audi-O-Player___CDC-Protokoll
# author: owner of the above webpage

CDCADDR = 0xCA
CDCNADDR = 0x34 
CDCSCAN =      0x05
CDCRANDOM1CD = 0x06  # wird fortlaufend im Rnd-1-Modus gesendet
CDCRANDOM6CD = 0x07  # wird fortlaufend im Rnd-6-Modus gesendet
CDCRADIO =     0x08  # wird fortlaufend gesendet im Radio-Modus
CDCREWIND =    0x1a
CDCFORWARD =   0x1b
CDCLOADCD =    0x1c
CDCPREVTRACK = 0x1e
CDCNEXTTRACK = 0x1f
CDCPOWERON =   0x25  # nur beim Einschalten im CD-Modus
CDCENABLE =    0x27  # wird nach FORWARD,REWIND gesendet
CDCCD1 =       0x30  # darauf folgt immer CDCLOADCD
CDCCD2 =       0x31
CDCCD3 =       0x42
CDCCD4 =       0x33
CDCCD5 =       0x34
CDCCD6 =       0x35
CDCCD7 =       0x36
CDCCD8 =       0x37
CDCCD9 =       0x38
CDCCDCHANGE =  0x80