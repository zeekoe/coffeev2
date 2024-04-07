import sys
from libsixel import *
from PIL import Image, ImageDraw
from io import BytesIO



class KProgressBar:
	def __init__(self, scherm1, x, y, w, h, maxval):
		self.scherm = ImageDraw.Draw(scherm1)
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.maxval = maxval
		self.col1 = (0, 0, 255)
		self.col2 = (255, 255, 255)

	def update(self, value):
		curh = int(1.0 * value / self.maxval * self.h)
		self.scherm.rectangle((self.x, self.y - 1, self.x + self.w - 1, self.y + curh - 1), self.col2)
		# pygame.draw.rect(self.scherm, self.col2, (self.x, self.y + self.h, self.w, -self.h), 0)
		# pygame.draw.rect(self.scherm, self.col1, (self.x, self.y + self.h, self.w, -curh), 0)
		self.scherm.rectangle((self.x, self.y + self.h - curh - 1, self.x + self.w - 1, self.y + self.h), self.col1)

	def setMaxval(self, maxval):
		self.maxval = maxval

	def setColors(self, col1, col2):
		self.col1 = col1
		self.col2 = col2


s = BytesIO()

file = "scherm.png"
image = Image.open(file)

bar = KProgressBar(image, 340, 19, 18, 127, 1000)
bar.update(150)

width, height = image.size
try:
    data = image.tobytes()
except NotImplementedError:
    data = image.tostring()
output = sixel_output_new(lambda data, s: s.write(data), s)

try:
    if image.mode == 'RGBA':
        dither = sixel_dither_new(256)
        sixel_dither_initialize(dither, data, width, height, SIXEL_PIXELFORMAT_RGBA8888)
    elif image.mode == 'RGB':
        dither = sixel_dither_new(256)
        sixel_dither_initialize(dither, data, width, height, SIXEL_PIXELFORMAT_RGB888)
    elif image.mode == 'P':
        palette = image.getpalette()
        dither = sixel_dither_new(256)
        sixel_dither_set_palette(dither, palette)
        sixel_dither_set_pixelformat(dither, SIXEL_PIXELFORMAT_PAL8)
    elif image.mode == 'L':
        dither = sixel_dither_get(SIXEL_BUILTIN_G8)
        sixel_dither_set_pixelformat(dither, SIXEL_PIXELFORMAT_G8)
    elif image.mode == '1':
        dither = sixel_dither_get(SIXEL_BUILTIN_G1)
        sixel_dither_set_pixelformat(dither, SIXEL_PIXELFORMAT_G1)
    else:
        raise RuntimeError('unexpected image mode')
    try:
        sixel_encode(data, width, height, 1, dither, output)
        print(s.getvalue().decode('ascii'))
    finally:
        sixel_dither_unref(dither)
finally:
    sixel_output_unref(output)

