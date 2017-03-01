def to_ints(img):
    data = [0] * 384000
    cdef int c = 0
    cdef int x
    cdef int y
    cdef int rgb
    cdef int alpha
    
    for x in range(0,800):
        for y in range(0, 480):
            rgb, alpha = img[y,x]
            data[c]=rgb
            c=c+1
    return list(data)

def downsample(ints):
    pixels = [0] * len(ints)
    cdef int i
    for i in range(0, len(ints)):
        if ints[i] <= 127:
            pixels[i] = 255
    return pixels

def to_epd_pixel4(raw):
    pixels = [0]*int(len(raw)/8)
    cdef int row = 30
    cdef int s = 1
    cdef int i
    for i in range(0, len(raw),16):
        pixels[row - s] = (
            ((raw[i + 6] << 7) & 0x80) |
            ((raw[i + 14] << 6) & 0x40) | 
            ((raw[i + 4] << 5) & 0x20) | 
            ((raw[i + 12] << 4) & 0x10) | 
            ((raw[i + 2] << 3) & 0x08) | 
            ((raw[i + 10] << 2) & 0x04) | 
            ((raw[i + 0] << 1) & 0x02) | 
            ((raw[i + 8] << 0) & 0x01))

        pixels[row + 30 - s] = (
            ((raw[i + 1] << 7) & 0x80) |
            ((raw[i + 9] << 6) & 0x40) | 
            ((raw[i + 3] << 5) & 0x20) | 
            ((raw[i + 11] << 4) & 0x10) |
            ((raw[i + 5] << 3) & 0x08) | 
            ((raw[i + 13] << 2) & 0x04) | 
            ((raw[i + 7] << 1) & 0x02) | 
            ((raw[i + 15] << 0) & 0x01))

        s = s + 1
        if s == 31:
            s = 1
            row = row + 60
    return pixels

def convert(img):
    img = img.convert("LA")
    img = img.load()
    return to_epd_pixel4(downsample(to_ints(img)))
