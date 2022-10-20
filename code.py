import gc

print(gc.mem_free())
import board
from digitalio import DigitalInOut, Pull, Direction

from neopixel import NeoPixel
from time import monotonic, sleep

print(f"post imports {gc.mem_free()}")


# from audioio import AudioOut
# from audiocore import WaveFile

prev = gc.mem_free()
print(f"post audio {gc.mem_free()}")
# from adafruit_led_animation.animation.blink import Blink

# print(f"Blink = {prev - gc.mem_free()}") # 6320
prev = gc.mem_free()
from adafruit_led_animation.animation.chase import Chase

print(f"Chase = {prev - gc.mem_free()}")
# prev = gc.mem_free()
# from adafruit_led_animation.animation.sparkle import Sparkle

# print(f"Sparkle = {prev - gc.mem_free()}")
prev = gc.mem_free()
from adafruit_led_animation.animation.comet import Comet

print(f"Comet = {prev - gc.mem_free()}")
prev = gc.mem_free()

# from adafruit_led_animation.animation.pulse import Pulse
# print(f"Pulse = {prev - gc.mem_free()}")
# prev = gc.mem_free()


from adafruit_led_animation.color import (
    # RED,
    # YELLOW,
    ORANGE,
    # GREEN,
    # TEAL,
    CYAN,
    # BLUE,
    PURPLE,
    # MAGENTA,
    # WHITE,
    # BLACK,
    # GOLD,
    # PINK,
    AQUA,
    JADE,
    AMBER,
    # OLD_LACE,
)

GS_SKY_BLUE = (160, 255, 255)
GS_GOLD = (255, 200, 66)
GS_LBLUE = (86, 192, 255)
GS_LBLUE_LOW = (2, 20, 20)
head = None
body = None
mode = 0  # startup
# mode = 1 # awake
# mode = 2 # armed
print(f"Colors = {prev - gc.mem_free()}")
print(f"more imports {gc.mem_free()}")


# Setup hardware

# speaker = DigitalInOut(board.SPEAKER_ENABLE)
# speaker.direction = Direction.OUTPUT
# speaker.value = True
# audio = AudioOut(board.SPEAKER)
# print(f"audio setup {gc.mem_free()}")


button_A = DigitalInOut(board.BUTTON_A)
button_A.switch_to_input(pull=Pull.DOWN)

button_B = DigitalInOut(board.BUTTON_B)
button_B.switch_to_input(pull=Pull.DOWN)

pixel_strip = NeoPixel(board.A1, 30, brightness=0.2, auto_write=False)
cp_pixels = NeoPixel(board.NEOPIXEL, 10, brightness=0.08, auto_write=False)

print(f"config {gc.mem_free()}")

# def play_sound(filename, wait=True):
#     with open(filename, "rb") as wave_file:
#         wave = WaveFile(wave_file)
#         audio.play(wave)
#         if wait:
#             while audio.playing:
#                 pass


def animate(pixels: list, seconds: int):
    print(f"animate start {gc.mem_free()}")
    start = monotonic()
    now = monotonic()
    print(
        f"animate while loop {gc.mem_free()} for {type(pixels[0]).__name__} and {type(pixels[1]).__name__}"
    )
    while now < start + seconds:
        for pixel in pixels:
            pixel.animate()
        now = monotonic()
    print(f"animate done {gc.mem_free()}")


def monitor():
    global mode
    print("Monitor")
    body = Comet(pixel_strip, speed=0.1, color=GS_LBLUE, tail_length=5, bounce=False)
    head = Comet(cp_pixels, speed=0.5, color=GS_GOLD, tail_length=3, bounce=False)
    animate([body, head], 10)
    pixel_strip.fill((0, 0, 20))
    cp_pixels.fill((0, 0, 20))
    pixel_strip.show()
    cp_pixels.show()
    mode = 1
    print("Monitor ON")


def arm():
    global mode
    print("Arm")
    body = Chase(pixel_strip, speed=0.8, size=3, spacing=6, color=AMBER)
    head = Chase(cp_pixels, speed=0.8, size=2, spacing=6, color=JADE)
    print(f"Arm -- pre animate {gc.mem_free()}")
    animate([body, head], 15)
    mode = 2
    print("Armed")


# Setup sound detection
import array
import math
import audiobusio


def normalized_rms(values):
    minbuf = int(sum(values) / len(values))
    return math.sqrt(
        sum(float(sample - minbuf) * (sample - minbuf) for sample in values)
        / len(values)
    )


mic = audiobusio.PDMIn(
    board.MICROPHONE_CLOCK, board.MICROPHONE_DATA, sample_rate=16000, bit_depth=16
)

samples = array.array("H", [0] * 160)
mic.record(samples, len(samples))
input_floor = normalized_rms(samples) + 10

# Lower number means more sensitive - more LEDs will light up with less sound.
sensitivity = 500
input_ceiling = input_floor + sensitivity


gc.collect()
print(f"post startup {gc.mem_free()}")
while True:
    if button_A.value or mode == 2:
        arm()
        gc.collect()
        print(gc.mem_free())
        print("Transitioning to Monitor Mode.")
        monitor()
        gc.collect()
        print(gc.mem_free())
    if mode == 0:
        monitor()
        gc.collect()
        print(gc.mem_free())
    if mode == 1:
        # Pulse
        for i in range(255, 0, -5):
            pixel_strip.fill((0, 0, i))
            cp_pixels.fill((0, 0, i))
            pixel_strip.show()
            cp_pixels.show()
        for i in range(0, 255, 5):
            pixel_strip.fill((0, 0, i))
            cp_pixels.fill((0, 0, i))
            pixel_strip.show()
            cp_pixels.show()
        mic.record(samples, len(samples))
        magnitude = normalized_rms(samples)
        # print(f"Magnitude: {magnitude}")
        if magnitude > 100:
            print(f"ARMING due to SOUND!!! --- {magnitude}")
            arm()
    sleep(0.2)
