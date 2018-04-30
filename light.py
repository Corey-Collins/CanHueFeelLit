import mss
import mss.tools
from PIL import Image
from phue import Bridge
import random
import time

def avg(image):
    color_tuple = [None, None, None]
    for channel in range(3):
        pixels = image.getdata(band=channel)
        values = []
        for pixel in pixels:
            values.append(pixel)
        color_tuple[channel] = sum (values)/len(values)
    return tuple(color_tuple)

def rgb_to_cie(rgb_tuple):
    red = rgb_tuple[0]
    green = rgb_tuple[1]
    blue = rgb_tuple[2]

    #Use the formula described in https://gist.github.com/popcorn245/30afa0f98eea1c2fd34d to get xy values.
    r = ((red + 0.055) / (1.055)) ** 2.4 if (red > 0.04045) else (red / 12.92)
    g = ((green + 0.055) / (1.055)) ** 2.4 if (green > 0.04045) else (green / 12.92)
    b = ((blue + 0.055) / (1.055)) ** 2.4 if (blue > 0.04045) else (blue / 12.92)

    X = r * 0.664511 + g * 0.154324 + b * 0.162028
    Y = r * 0.283881 + g * 0.668433 + b * 0.047685
    Z = r * 0.000088 + g * 0.072310 + b * 0.986039

    if((X + Y + Z) == 0):
        return (0, 0)

    cx = X / (X + Y + Z)
    cy = Y / (X + Y + Z)

    return (cx, cy)

def change_lights(mon, bulb):
    # Capture a bbox using percent values
    left = monitor['left'] + monitor['width'] * mon // 100  # 0% from the left
    top = monitor['top'] + monitor['height'] * mon // 100  # 0% from the top
    right = left + 400  # 400px width
    lower = top + 400  # 400px height

    bbox = (left, top, right, lower)

    # Grab the picture
    # Using PIL would be something like:
    # im = ImageGrab(bbox=bbox)
    sct_img = sct.grab(bbox)

    '''# save as png
    output = 'output.png'.format(**monitor)
    mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)'''

    # Create an Image
    img = Image.new('RGB', sct_img.size)

    # Best solution: create a list(tuple(R, G, B), ...) for putdata()
    pixels = zip(sct_img.raw[2::4],
                 sct_img.raw[1::4],
                 sct_img.raw[0::4])
    img.putdata(list(pixels))

    rgb_tuple = avg(img)

    luma = 0.2126 * rgb_tuple[0] + 0.7152 * rgb_tuple[1] + 0.0722 * rgb_tuple[2]

    cx, cy = rgb_to_cie(rgb_tuple)

    lights[bulb].xy = [cx, cy]
    lights[bulb].brightness = int(luma * 2.54)

    print('set light to ', cx, ' ', cy)
    print('luminance: ', luma)
    print()

b = Bridge('10.0.0.166')
b.connect()

lights = b.get_light_objects()

with mss.mss() as sct:

    #Use the 1st monitor
    monitor = sct.monitors[1]

    while True:
        change_lights(0, 0)
        change_lights(20, 1)
        change_lights(60, 2)
