from machine import Pin, SPI
import time

# NEC Protocol Constants
NEC_HDR_MARK = 9000
NEC_HDR_SPACE = 4500
NEC_BIT_MARK = 560
NEC_ONE_SPACE = 1690
NEC_ONE_LEN = NEC_BIT_MARK + NEC_ONE_SPACE
NEC_ZERO_SPACE = 560
NEC_ZERO_LEN = NEC_BIT_MARK + NEC_ZERO_SPACE

# VAG CDC
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

MODE_PLAY = 0xFF
MODE_SHUFFLE = 0x55
MODE_SCAN = 0x00

# GPIO pin for the IR receiver
IR_PIN = 0

# Variables for NEC decoding
raw_data = 0
bit_count = 0
last_fall = 0

def nec_handler(pin):
    global raw_data, bit_count, last_fall
    
    now = time.ticks_us()
    duration = time.ticks_diff(now, last_fall)
    last_fall = now

    # Start Bit MARK+SPACE
    if NEC_HDR_MARK + NEC_HDR_SPACE - 200 < duration < NEC_HDR_MARK + NEC_HDR_SPACE + 200:
        raw_data = 0
        bit_count = 0
    # Between 0-1 bit
    elif NEC_ZERO_LEN - 200 < duration < NEC_ONE_LEN + 200:
        if bit_count < 32:
            if NEC_ONE_LEN - 200 < duration < NEC_ONE_LEN + 200:
                raw_data = (raw_data << 1) | 1
            elif NEC_ZERO_LEN - 200 < duration < NEC_ZERO_LEN + 200:
                raw_data = (raw_data << 1)
            bit_count += 1
    # else:
        # print("faulty bit, duration: {}, cnt: {}".format(duration, bit_count))

# Setup the IR receiver pin
ir = Pin(IR_PIN, Pin.IN, Pin.PULL_UP)
ir.irq(trigger=machine.Pin.IRQ_RISING, handler=nec_handler)

# Setup SPI transmiter with 50kBaud
# 62,5 kHz, MSB First, Cycle Start, CPOL=0, CPHA=1
res = SPI(0, baudrate=62500, polarity=0, phase=1, firstbit=SPI.MSB)

def nec_recv():
    bit_count = 0
    return raw_data

def nec_command(raw_data):
    return (raw_data >> 8 & 0xFF)

def rev(x, n=8):
    y = 0
    for _ in range(n):
        y <<= 1
        y |= x & 0x01
        x >>= 1
    return y

def send_package(frame):
    buf = bytearray(1)
    for i in range(8):
        buf[0] = frame[i]
        res.write(buf)
        time.sleep(0.000874)  # 874us

def send_state(cdno, trackno, mins, sec, mode): 
    msg = bytearray([
        0x34,
        0xFF ^ cdno,    # max 16 cds
        0xFF ^ trackno, # max 255 tracks
        0xFF,           # minutes,
        0xFF,           # seconds,
        MODE_PLAY,
        0xCF,
        0x3C])
    send_package(msg)
    
send_package((0x74,0xBE,0xFE,0xFF,0xFF,0xFF,0x8F,0x7C)); # idle
time.sleep(0.010);
send_package((0x34,0xFF,0xFE,0xFE,0xFE,0xFF,0xFA,0x3C)); # load disc
time.sleep(0.100);
send_package((0x74,0xBE,0xFE,0xFF,0xFF,0xFF,0x8F,0x7C)); # idle
time.sleep(0.010);

print("Listening to NEC commands")
i = 1
while True:
    send_state(1, i, 21, 37, MODE_PLAY)
    i = i+1 if i<255 else 0
    time.sleep(0.041) # sleep 41ms
    
    if bit_count == 32:
        code = nec_recv()
        print("Received NEC code: 0x{:08X}".format(code))