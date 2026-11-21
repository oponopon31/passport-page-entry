#!/usr/bin/env python3
"""PASSPORT OF THE REPUBLIC OF VELMORA -- an invented passport spread.

Draws a 1024x1024 open-passport spread for a country that does not
exist, procedurally, with Python 3 stdlib only (struct + zlib for the
PNG encoder and for the small PNG decoder below, a hand-defined 5x7
bitmap font, geometric drawing). No network, no randomness: two runs
produce a byte-identical PNG.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (fallback /output).

The country: REPUBLIC OF VELMORA (RESPUBLIKA VELMORA), a small
republic famous for its lakeside casinos, capital Velmar. The
holder is KORBAN SLOT, a 24-year-old slot player, born 14 JUN 2001
in Velmar, licence S-0771. Passport VEL077777 issued 14 MAR 2024
in Velmar, valid to 13 MAR 2034. The machine-readable zone is real
ICAO 9303 TD3: both lines are 44 characters and every check digit
is computed by the 7-3-1 algorithm in this program, not typed in
by hand.

The holder's photograph is a real photograph supplied by the holder,
shipped as assets/holder-photo.png next to this program. At run time
it is loaded with the small stdlib PNG decoder below (IHDR/IDAT,
zlib, all five scanline filters, 8-bit RGB/RGBA, non-interlaced) --
no PIL at run time. The asset itself was prepared at build time
only: a tight passport-style head-and-shoulders crop, resized to
150x200. The face is untouched; at run time the pink wall / dark
door behind the holder is replaced with a plain light background
(see clean_photo_background), as a real passport photo requires.

Travel history (every stamp after the 14 MAR 2024 issue date):
  03 JUN 2024  out of Velmora, into Zoraville, Tarnovia (casino town)
  21 JUN 2024  out of Tarnovia, back into Velmora
  12 AUG 2025  out of Velmora, into Lumina, Ostara (casino resort)
  06 SEP 2025  out of Ostara, back into Velmora
An Ostara visitor visa, type C single entry, 30 days, valid
01 AUG - 30 SEP 2025, fee 40 VEL, covers the Ostara trip.
Red ink = Velmora, blue ink = Tarnovia, green ink = Ostara.

The telling detail: the visa page carries a slot credit
endorsement -- the holder is a registered slot player, casino
credit limited to 500 VEL per visit, winnings above 1,000 VEL must
be declared at the border -- and a round casino-tax stamp (40 VEL
paid, Port of Velmar, 03 JUN 2024) sits beside it. The data page
notes the holder's slot licence and the duty to declare winnings.
Labels are bilingual: Velmoran and English.
"""
import hashlib
import math
import os
import struct
import zlib

W = H = 1024

DESK = (22, 32, 48)       # dark desk under the open book
DESK_DK = (12, 18, 30)    # drop shadow
PAPER = (247, 243, 230)   # passport paper, off-white
PAPER2 = (240, 234, 216)  # slightly deeper paper (MRZ band)
GUIL = (226, 219, 194)    # guilloche lines on the paper
GUIL2 = (232, 225, 202)   # faint watermark
INK = (16, 22, 30)        # near-black text
NAVY = (18, 48, 74)       # page rules
MAROON = (128, 32, 40)    # header, emblem, Velmora stamps
GOLD = (176, 138, 52)     # emblem, rules
GOLD_LT = (212, 175, 90)
GRAY = (96, 96, 88)       # small labels
RED = (178, 34, 28)       # Velmora stamps
BLUE = (28, 68, 150)      # Tarnovia stamps
GREEN = (30, 110, 70)     # Ostara stamps and visa
KEY = (255, 0, 255)       # transparent key colour for stamp canvases

# ---------------------------------------------------------------- font ----
# Hand-defined 5x7 bitmap font. '#' = set pixel, '.' = empty.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '<': ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "'": ("01100", "00100", "00000", "00000", "00000", "00000", "00000"),
    '\u00b7': ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
    '\u010c': ("01010", "00100", "01110", "10001", "10000", "10001", "01110"),
    '\u0110': ("11110", "10001", "10001", "11111", "10001", "10001", "11110"),
    '\u0160': ("01010", "00100", "01111", "10000", "01110", "00001", "11110"),
    '\u017d': ("01010", "00100", "11111", "00010", "00100", "01000", "11111"),
}

# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return (self.buf[i], self.buf[i + 1], self.buf[i + 2])

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def blend(self, x, y, c, a):
        """Blend colour c over the pixel at (x, y); a = weight of c."""
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            for k in range(3):
                self.buf[i + k] = int(c[k] * a + self.buf[i + k] * (1 - a))

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = c[0]
                self.buf[i + 1] = c[1]
                self.buf[i + 2] = c[2]

    def hline(self, x0, x1, y, c, t=1):
        if x1 < x0:
            x0, x1 = x1, x0
        for yy in range(y, y + t):
            for xx in range(x0, x1 + 1):
                self.set(xx, yy, c)

    def vline(self, x, y0, y1, c, t=1):
        if y1 < y0:
            y0, y1 = y1, y0
        for xx in range(x, x + t):
            for yy in range(y0, y1 + 1):
                self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.fill_rect(x, y, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def fill_circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cx + dx, cy + dy, c)

    def circle(self, cx, cy, r, c, t=1):
        x, y, d = 0, r, 1 - r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.fill_rect(px, py, t, t, c)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

    def fill_ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            dx = int(rx * (1 - (dy / ry) ** 2) ** 0.5) if ry else 0
            self.hline(cx - dx, cx + dx, cy + dy, c)

    def fill_poly(self, pts, c):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, c)

    # ------------------------------------------------------------ text ----
    def text(self, x, y, s, scale, c, pitch=None):
        s = s.upper()
        cx = x
        step = pitch if pitch is not None else 6 * scale
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += step
        return cx

    def text_width(self, s, scale, pitch=None):
        step = pitch if pitch is not None else 6 * scale
        return len(s) * step - (step - 5 * scale)

    def text_centred(self, cx, y, s, scale, c, pitch=None):
        x = cx - self.text_width(s, scale, pitch) // 2
        self.text(x, y, s, scale, c, pitch)
        return x

    def text_right(self, x_right, y, s, scale, c, pitch=None):
        x = x_right - self.text_width(s, scale, pitch)
        self.text(x, y, s, scale, c, pitch)
        return x

    def wrap(self, s, scale, max_w, pitch=None):
        max_chars = max(1, max_w // (pitch if pitch is not None
                                     else 6 * scale))
        lines, cur = [], ''
        for word in s.upper().split(' '):
            trial = (cur + ' ' + word).strip() if cur else word
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ------------------------------------------------------------------ png ----
def write_png(path, canvas):
    w, h = canvas.w, canvas.h
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)  # filter: none
        raw += canvas.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack('>I', len(data)) + typ + data
        out += struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', comp) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return png


def load_png_rgb(path):
    """Minimal stdlib PNG decoder: 8-bit RGB/RGBA, non-interlaced.
    Returns (width, height, rgb bytearray). Raises on anything else."""
    with open(path, 'rb') as f:
        data = f.read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', 'not a PNG'
    pos = 8
    idat = b''
    w = h = bit_depth = colour = interlace = None
    while pos < len(data):
        (ln,) = struct.unpack('>I', data[pos:pos + 4])
        typ = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        if typ == b'IHDR':
            w, h, bit_depth, colour, _c, _f, interlace = \
                struct.unpack('>IIBBBBB', chunk)
        elif typ == b'IDAT':
            idat += chunk
        elif typ == b'IEND':
            break
        pos += 12 + ln
    assert bit_depth == 8 and colour in (2, 6), 'unsupported PNG'
    assert interlace == 0, 'interlaced PNG not supported'
    channels = 3 if colour == 2 else 4
    raw = zlib.decompress(idat)
    stride = w * channels
    px = bytearray(w * h * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        ftype = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if ftype == 0:
            pass
        elif ftype == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ftype == 3:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                b = prev[i]
                cc = prev[i - channels] if i >= channels else 0
                pp = a + b - cc
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - cc)
                pr = a if (pa <= pb and pa <= pc) else \
                    (b if pb <= pc else cc)
                line[i] = (line[i] + pr) & 0xFF
        else:
            raise ValueError('bad PNG filter %d' % ftype)
        for x in range(w):
            o = (y * w + x) * 3
            s = x * channels
            px[o] = line[s]
            px[o + 1] = line[s + 1]
            px[o + 2] = line[s + 2]
        prev = line
    return w, h, px


def blit_photo(cv, img, x0, y0, w, h, alpha=1.0):
    """Blit a decoded photo onto the canvas, nearest-neighbour scaled."""
    iw, ih, px = img
    for y in range(h):
        sy = y * ih // h
        for x in range(w):
            sx = x * iw // w
            o = (sy * iw + sx) * 3
            c = (px[o], px[o + 1], px[o + 2])
            if alpha >= 1.0:
                cv.set(x0 + x, y0 + y, c)
            else:
                cv.blend(x0 + x, y0 + y, c, alpha)


PHOTO_BG = (243, 242, 238)  # plain light passport-photo background


def _rgb_dist(a, b):
    dr = a[0] - b[0]
    dg = a[1] - b[1]
    db = a[2] - b[2]
    return (dr * dr + dg * dg + db * db) ** 0.5


def clean_photo_background(img):
    """Replace the selfie's pink wall / dark door background with a plain
    light passport-photo background, leaving the face untouched.

    Region-grows outward from border pixels that match the two known
    background colours (bright pink wall on the left, dark warm wood on
    the right), stepping only to neighbours of similar colour, and never
    into skin-like or very dark (hair) pixels. The shoulders fill the
    bottom edge, so it is never used as a seed. The resulting mask is
    box-blurred twice so the head/shoulders feather cleanly into the
    flat light background instead of a hard cut-out edge. Pure stdlib,
    fully deterministic."""
    iw, ih, px = img

    def pix(x, y):
        o = (y * iw + x) * 3
        return (px[o], px[o + 1], px[o + 2])

    def is_seed(c):
        r, g, b = c
        if r >= 200 and b >= 170 and r - g >= 40:  # pink wall
            return True
        if (45 <= r <= 110 and 35 <= g <= 85 and 35 <= b <= 85
                and r >= g and r - g <= 35):       # dark wood
            return True
        return False

    def is_skin(c):
        r, g, b = c
        return (r > 150 and g > b and 30 <= r - g <= 70
                and 40 <= r - b <= 95)

    def is_hair_dark(c):
        return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) < 38

    mask = bytearray(iw * ih)
    stack = []
    for x in range(iw):
        if is_seed(pix(x, 0)):
            stack.append((x, 0))
    for y in range(ih):
        if is_seed(pix(0, y)):
            stack.append((0, y))
        if is_seed(pix(iw - 1, y)):
            stack.append((iw - 1, y))
    # interior seeds: pink-wall pixels enclosed by hair strands, which
    # the border flood can never reach. Strict test (B well above G)
    # so bright skin highlights, which are pink-ish but B < G, never
    # seed.
    for y in range(ih):
        for x in range(iw):
            r, g, b = pix(x, y)
            if r >= 200 and b - g >= 30 and r - g >= 40:
                stack.append((x, y))
    while stack:
        x, y = stack.pop()
        if mask[y * iw + x]:
            continue
        mask[y * iw + x] = 1
        c = pix(x, y)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < iw and 0 <= ny < ih and not mask[ny * iw + nx]:
                n = pix(nx, ny)
                if (_rgb_dist(c, n) <= 22 and not is_skin(n)
                        and not is_hair_dark(n)):
                    stack.append((nx, ny))
    # feather: one 3x3 box blur of the mask -> soft alpha, then boost it
    # so the background reads as flat light (a half-blended pink pixel
    # still looks pink) while the subject edge keeps a ~1px soft rim.
    alpha = [float(m) for m in mask]
    nxt = [0.0] * (iw * ih)
    for y in range(ih):
        for x in range(iw):
            s = 0.0
            n = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < iw and 0 <= yy < ih:
                        s += alpha[yy * iw + xx]
                        n += 1
            nxt[y * iw + x] = min(1.0, (s / n) * 1.6)
    alpha = nxt
    out = bytearray(px)
    for i in range(iw * ih):
        a = alpha[i]
        if a > 0:
            o = i * 3
            for k in range(3):
                out[o + k] = int(round(PHOTO_BG[k] * a
                                      + px[o + k] * (1 - a)))
    return iw, ih, out


# -------------------------------------------------------------- mrz --------
def mrz_value(ch):
    if ch == '<':
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - ord('A') + 10


def mrz_check(s):
    weights = (7, 3, 1)
    return str(sum(mrz_value(ch) * weights[i % 3]
                   for i, ch in enumerate(s)) % 10)


def build_mrz():
    """ICAO 9303 TD3, two lines of 44 characters, check digits computed."""
    surname_given = "KORBAN<<SLOT"
    line1 = ("P<VEL" + surname_given).ljust(44, '<')
    doc = "VEL077777"
    dob = "010614"
    exp = "340313"
    personal = "3187552019<<<<"
    body = (doc + mrz_check(doc) + "VEL" + dob + mrz_check(dob)
            + "M" + exp + mrz_check(exp) + personal
            + mrz_check(personal))
    line2 = body + mrz_check(body)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ------------------------------------------------------------ drawing -----
def wave_line(cv, x0, x1, y, amp, period, c):
    """A gentle sine wave drawn as short segments."""
    prev = None
    for x in range(x0, x1 + 1, 3):
        yy = y + int(amp * math.sin(2 * math.pi * (x - x0) / period))
        if prev is not None:
            cv.line(prev[0], prev[1], x, yy, c, 1)
        prev = (x, yy)


def guilloche_page(cv, x0, x1, y0, y1):
    """Fine wavy security lines across a page, plus a faint watermark."""
    for y in range(y0 + 8, y1 - 8, 18):
        wave_line(cv, x0 + 6, x1 - 6, y, 3, 46, GUIL)
    # faint watermark: two concentric circles, the state emblem ghost
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    cv.circle(cx, cy, 150, GUIL2, 1)
    cv.circle(cx, cy, 138, GUIL2, 1)


def page_frame(cv, x0, x1, y0, y1):
    cv.hline(x0 + 10, x1 - 10, y0 + 10, NAVY, 1)
    cv.hline(x0 + 10, x1 - 10, y1 - 10, NAVY, 1)
    cv.vline(x0 + 10, y0 + 10, y1 - 10, NAVY, 1)
    cv.vline(x1 - 10, y0 + 10, y1 - 10, NAVY, 1)


def draw_emblem(cv, cx, cy):
    """State emblem: gold ring, a lucky 777, small stars."""
    cv.circle(cx, cy, 30, GOLD, 2)
    cv.circle(cx, cy, 26, GOLD, 1)
    # small four-point star above the 777
    sx, sy = cx, cy - 19
    cv.fill_poly([(sx, sy - 5), (sx + 2, sy - 2), (sx + 5, sy),
                  (sx + 2, sy + 2), (sx, sy + 5), (sx - 2, sy + 2),
                  (sx - 5, sy), (sx - 2, sy - 2)], GOLD)
    cv.text_centred(cx, cy - 6, "777", 2, GOLD)
    # two tiny stars flanking the 777
    for tx in (cx - 20, cx + 20):
        cv.fill_poly([(tx, cy + 8), (tx + 1, cy + 10), (tx + 3, cy + 11),
                      (tx + 1, cy + 12), (tx, cy + 14), (tx - 1, cy + 12),
                      (tx - 3, cy + 11), (tx - 1, cy + 10)], GOLD)


def draw_photo_frame(cv, img, x0, y0, w, h):
    """The holder's photograph in a maroon frame with a gold inner line."""
    blit_photo(cv, img, x0 + 2, y0 + 2, w - 4, h - 4)
    cv.hline(x0, x0 + w - 1, y0, MAROON, 2)
    cv.hline(x0, x0 + w - 1, y0 + h - 2, MAROON, 2)
    cv.vline(x0, y0, y0 + h - 1, MAROON, 2)
    cv.vline(x0 + w - 2, y0, y0 + h - 1, MAROON, 2)
    cv.hline(x0 + 4, x0 + w - 5, y0 + 4, GOLD, 1)
    cv.hline(x0 + 4, x0 + w - 5, y0 + h - 5, GOLD, 1)
    cv.vline(x0 + 4, y0 + 4, y0 + h - 5, GOLD, 1)
    cv.vline(x0 + w - 5, y0 + 4, y0 + h - 5, GOLD, 1)


def draw_signature(cv, x, y, w):
    """A signature flourish in ink, with the printed name beneath."""
    pts = [(x + 4, y + 14), (x + 14, y + 2), (x + 22, y + 16),
           (x + 30, y + 4), (x + 38, y + 14), (x + 46, y + 6),
           (x + 58, y + 16), (x + 70, y + 2), (x + 82, y + 14),
           (x + 96, y + 8), (x + 112, y + 16)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, INK, 1)
    cv.line(x + 112, y + 16, x + 128, y + 10, INK, 1)
    cv.text(x, y + 22, "KORBAN SLOT", 1, INK)


# -------------------------------------------------------------- stamps -----
def blit_rotated(dst, src, cx, cy, angle_deg, alpha=0.78):
    """Blit src onto dst rotated about (cx, cy); KEY pixels stay clear,
    and the ink is blended at alpha so the paper shows through."""
    rad = math.radians(angle_deg)
    co, si = math.cos(rad), math.sin(rad)
    w, h = src.w, src.h
    ex = int((abs(w * co) + abs(h * si)) / 2) + 1
    ey = int((abs(w * si) + abs(h * co)) / 2) + 1
    for dy in range(-ey, ey + 1):
        for dx in range(-ex, ex + 1):
            sx = dx * co + dy * si + w / 2
            sy = -dx * si + dy * co + h / 2
            ix, iy = int(sx), int(sy)
            if 0 <= ix < w and 0 <= iy < h:
                px = src.get(ix, iy)
                if px != KEY:
                    dst.blend(cx + dx, cy + dy, px, alpha)


def stamp_canvas(country, city, kind, date, colour, foot):
    """One rectangular border stamp, drawn straight on its own canvas
    (220x100, KEY background) so the caller can rotate it."""
    sc = Canvas(220, 100, KEY)
    x0, y0, w, h = 10, 8, 200, 84
    # double border
    sc.hline(x0, x0 + w - 1, y0, colour, 2)
    sc.hline(x0, x0 + w - 1, y0 + h - 1, colour, 2)
    sc.vline(x0, y0, y0 + h - 1, colour, 2)
    sc.vline(x0 + w - 1, y0, y0 + h - 1, colour, 2)
    sc.hline(x0 + 4, x0 + w - 5, y0 + 4, colour, 1)
    sc.hline(x0 + 4, x0 + w - 5, y0 + h - 5, colour, 1)
    sc.vline(x0 + 4, y0 + 4, y0 + h - 5, colour, 1)
    sc.vline(x0 + w - 5, y0 + 4, y0 + h - 5, colour, 1)
    sc.text_centred(110, y0 + 9, country, 1, colour)
    sc.text_centred(110, y0 + 20, city, 2, colour)
    sc.text_centred(110, y0 + 40, kind, 1, colour)
    sc.text_centred(110, y0 + 52, date, 2, colour)
    sc.text_centred(110, y0 + 74, foot, 1, colour)
    return sc


def casino_tax_canvas():
    """Round casino-tax stamp: 160x160, KEY background."""
    sc = Canvas(160, 160, KEY)
    sc.circle(80, 80, 62, MAROON, 3)
    sc.circle(80, 80, 56, MAROON, 1)
    sc.text_centred(80, 42, "CASINO TAX", 2, MAROON)
    sc.text_centred(80, 62, "40 VEL", 2, MAROON)
    sc.hline(48, 112, 80, MAROON, 1)
    sc.text_centred(80, 86, "PAID", 2, MAROON)
    sc.text_centred(80, 106, "PORT OF VELMAR", 1, MAROON)
    sc.text_centred(80, 118, "03 JUN 2024", 1, MAROON)
    return sc


# -------------------------------------------------------------- layout -----
LX0, LX1 = 28, 504      # left page
RX0, RX1 = 520, 996     # right page
PY0, PY1 = 40, 984      # spread top / bottom

# (country, city, kind, date, colour, foot) -- chronological, in pairs:
# out of Velmora, into the neighbour, back out, back home.
STAMPS = [
    ("REPUBLIC OF VELMORA", "VELMAR", "DEPARTURE", "03 JUN 2024",
     RED, "PORT OF VELMAR"),
    ("TARNOVIA", "ZORAVILLE", "ARRIVAL", "03 JUN 2024",
     BLUE, "ZORAVILLE CASINO POST"),
    ("TARNOVIA", "ZORAVILLE", "DEPARTURE", "21 JUN 2024",
     BLUE, "ZORAVILLE CASINO POST"),
    ("REPUBLIC OF VELMORA", "VELMAR", "ARRIVAL", "21 JUN 2024",
     RED, "PORT OF VELMAR"),
    ("REPUBLIC OF VELMORA", "VELMAR", "DEPARTURE", "12 AUG 2025",
     RED, "PORT OF VELMAR"),
    ("OSTARA", "LUMINA", "ARRIVAL", "12 AUG 2025",
     GREEN, "LUMINA RESORT POST"),
    ("OSTARA", "LUMINA", "DEPARTURE", "06 SEP 2025",
     GREEN, "LUMINA RESORT POST"),
    ("REPUBLIC OF VELMORA", "VELMAR", "ARRIVAL", "06 SEP 2025",
     RED, "PORT OF VELMAR"),
]
ANGLES = [-3, 2, -2, 3, -4, 2, 3, -2]


def draw_left_page(cv, photo):
    guilloche_page(cv, LX0, LX1, PY0, PY1)
    page_frame(cv, LX0, LX1, PY0, PY1)
    cx = (LX0 + LX1) // 2
    # passport number, top right
    cv.text_right(LX1 - 24, 56, "VEL077777", 1, MAROON)
    # emblem, then the bilingual header
    draw_emblem(cv, cx, 102)
    cv.text_centred(cx, 146, "REPUBLIC OF VELMORA", 3, MAROON)
    cv.text_centred(cx, 174, "RESPUBLIKA VELMORA", 2, MAROON)
    cv.text_centred(cx, 198, "PASOŠ · PASSPORT", 1, GRAY)
    cv.hline(cx - 90, cx + 90, 216, GOLD, 1)
    # type / code / passport number row
    cv.text(48, 232, "TIP / TYPE", 1, GRAY)
    cv.text(48, 242, "P", 2, INK)
    cv.text(120, 232, "KOD / CODE", 1, GRAY)
    cv.text(120, 242, "VEL", 2, INK)
    cv.text(224, 232, "PAS BR. / PASSPORT NO.", 1, GRAY)
    cv.text(224, 242, "VEL077777", 2, INK)
    # photograph, left column
    draw_photo_frame(cv, photo, 48, 272, 150, 200)
    cv.text(48, 486, "POTPIS / HOLDER'S SIGNATURE", 1, GRAY)
    draw_signature(cv, 48, 498, 150)
    # data fields, right column
    fields = [
        (224, 272, "PREZIM / SURNAME", "KORBAN"),
        (224, 306, "IMEN / GIVEN NAMES", "SLOT"),
        (224, 340, "NAROD / NATIONALITY", "VELMORAN"),
        (224, 374, "ROĐEN / DATE OF BIRTH", "14 JUN 2001"),
        (364, 374, "POL / SEX", "M"),
        (224, 408, "ROD-KRAJ / PLACE OF BIRTH", "VELMAR"),
        (224, 442, "IZDAN / DATE OF ISSUE", "14 MAR 2024"),
        (224, 476, "VREDI / DATE OF EXPIRY", "13 MAR 2034"),
        (224, 510, "VLAST / AUTHORITY", "PASSPORT REGISTRY"),
        (224, 544, "LIČNI BR. / PERSONAL NO.", "3187 5520 19"),
    ]
    for x, y, label, value in fields:
        if label:
            cv.text(x, y, label, 1, GRAY)
        cv.text(x, y + 10, value, 2, INK)
    # observations -- the telling detail
    cv.fill_rect(48, 580, 282, 112, PAPER2)
    cv.hline(48, 329, 580, GOLD, 2)
    cv.hline(48, 329, 691, GOLD, 2)
    cv.vline(48, 580, 691, GOLD, 2)
    cv.vline(329, 580, 691, GOLD, 2)
    cv.text(60, 592, "NAPOMENA / OBSERVATIONS", 1, NAVY)
    oy = 608
    for line in cv.wrap(
            "HOLDER IS A LICENSED SLOT PLAYER, LICENCE S-0771. "
            "WINNINGS MUST BE DECLARED AT CUSTOMS.", 1, 258):
        cv.text(60, oy, line, 1, INK)
        oy += 11
    cv.text(60, oy + 6, "PASSPORT REGISTRY - VELMAR", 1, GRAY)
    # small second photograph, right of the observations box
    blit_photo(cv, photo, 356, 580, 64, 86, alpha=0.85)
    cv.hline(356, 419, 580, MAROON, 1)
    cv.hline(356, 419, 665, MAROON, 1)
    cv.vline(356, 580, 665, MAROON, 1)
    cv.vline(419, 580, 665, MAROON, 1)
    # property notice
    cv.text(48, 716, "NOTICE", 1, NAVY)
    ny = 730
    for line in cv.wrap(
            "THIS PASSPORT IS THE PROPERTY OF THE REPUBLIC OF VELMORA. "
            "IF FOUND, PLEASE RETURN IT TO THE NEAREST VELMORAN "
            "CONSULATE OR TO THE PASSPORT REGISTRY, VELMAR. "
            "THE HOLDER IS A CITIZEN OF THE REPUBLIC OF VELMORA AND IS "
            "ENTITLED TO THE PROTECTION OF ITS GOVERNMENT.", 1, 436):
        cv.text(48, ny, line, 1, GRAY)
        ny += 10
    # coordinates
    cv.text_centred(cx, 830, "VELMAR - LAKESIDE CASINOS OF VELMORA - "
                    "46.10 N 14.45 E", 1, GRAY)
    # machine-readable zone
    line1, line2 = build_mrz()
    cv.fill_rect(48, 880, 436, 62, PAPER2)
    cv.hline(48, 483, 880, NAVY, 1)
    cv.hline(48, 483, 941, NAVY, 1)
    cv.text_centred(cx, 892, line1, 1, INK, pitch=8)
    cv.text_centred(cx, 912, line2, 1, INK, pitch=8)
    return line1, line2


def draw_right_page(cv):
    guilloche_page(cv, RX0, RX1, PY0, PY1)
    page_frame(cv, RX0, RX1, PY0, PY1)
    cx = (RX0 + RX1) // 2
    cv.text(548, 56, "VIZE · VISAS", 2, NAVY)
    cv.text_right(972, 56, "5", 2, NAVY)
    cv.hline(548, 972, 78, GOLD, 1)
    # slot credit endorsement box, with the casino-tax stamp on it
    ex, ey, ew, eh = 548, 96, 424, 150
    cv.fill_rect(ex, ey, ew, eh, PAPER2)
    cv.hline(ex, ex + ew - 1, ey, NAVY, 2)
    cv.hline(ex, ex + ew - 1, ey + eh - 1, NAVY, 2)
    cv.vline(ex, ey, ey + eh - 1, NAVY, 2)
    cv.vline(ex + ew - 1, ey, ey + eh - 1, NAVY, 2)
    cv.text(ex + 12, ey + 10, "SLOT CREDIT ENDORSEMENT", 1, NAVY)
    cv.text(ex + 12, ey + 24,
            "VELMAR CASINO AUTHORITY - 14 MAR 2024", 1, GRAY)
    ty = ey + 42
    for line in cv.wrap(
            "HOLDER IS A REGISTERED SLOT PLAYER. CASINO CREDIT "
            "LIMITED TO 500 VEL PER VISIT. WINNINGS ABOVE 1,000 VEL "
            "MUST BE DECLARED AT THE BORDER.", 1, 248):
        cv.text(ex + 12, ty, line, 1, INK)
        ty += 11
    toll = casino_tax_canvas()
    blit_rotated(cv, toll, 888, 172, 8, alpha=0.85)
    # stamps: 4 rows x 2 columns, chronological
    xs = [RX0 + 28, RX0 + 248]
    ys = [262, 362, 462, 562]
    for i, (country, city, kind, date, colour, foot) in enumerate(STAMPS):
        sc = stamp_canvas(country, city, kind, date, colour, foot)
        row, col = divmod(i, 2)
        blit_rotated(cv, sc, xs[col] + 100, ys[row] + 42, ANGLES[i])
    # Ostara visitor visa sticker
    vx, vy, vw, vh = 548, 676, 424, 192
    cv.fill_rect(vx, vy, vw, vh, (252, 250, 244))
    cv.hline(vx, vx + vw - 1, vy, GREEN, 2)
    cv.hline(vx, vx + vw - 1, vy + vh - 1, GREEN, 2)
    cv.vline(vx, vy, vy + vh - 1, GREEN, 2)
    cv.vline(vx + vw - 1, vy, vy + vh - 1, GREEN, 2)
    cv.fill_rect(vx + 1, vy + 1, vw - 2, 20, GREEN)
    cv.text_centred(vx + vw // 2, vy + 7, "OSTARA · VISITOR VISA", 1,
                    (252, 250, 244))
    cv.text(vx + 10, vy + 32, "OSTARA VISITOR VISA", 2, GREEN)
    cv.text(vx + 10, vy + 56, "TYPE", 1, GRAY)
    cv.text(vx + 10, vy + 66, "C - SINGLE ENTRY", 1, INK)
    cv.text(vx + 220, vy + 56, "DURATION OF STAY", 1, GRAY)
    cv.text(vx + 220, vy + 66, "30 DAYS", 1, INK)
    cv.text(vx + 10, vy + 88, "VALID FROM", 1, GRAY)
    cv.text(vx + 10, vy + 98, "01 AUG 2025", 1, INK)
    cv.text(vx + 220, vy + 88, "UNTIL", 1, GRAY)
    cv.text(vx + 220, vy + 98, "30 SEP 2025", 1, INK)
    cv.text(vx + 10, vy + 120, "ISSUED AT", 1, GRAY)
    cv.text(vx + 10, vy + 130, "VELMAR, 18 JUL 2025", 1, INK)
    cv.text(vx + 220, vy + 120, "FEE", 1, GRAY)
    cv.text(vx + 220, vy + 130, "40 VEL", 1, INK)
    # machine-readable barcode strip at the foot of the sticker
    bx = vx + 10
    for bw in (2, 1, 3, 1, 2, 4, 1, 2, 1, 3, 2, 1, 4, 2, 1, 3, 1, 2):
        cv.fill_rect(bx, vy + vh - 26, bw, 18, INK)
        bx += bw + 2
    # legend
    cv.text_centred(cx, 892, "RED - VELMORA · BLUE - TARNOVIA · "
                    "GREEN - OSTARA", 1, GRAY)
    cv.text_centred(cx, 906, "STAMPS APPLIED AT THE PORT OF ENTRY", 1, GRAY)
    cv.text_right(972, 950, "VEL077777", 1, MAROON)


def draw():
    cv = Canvas(W, H, DESK)
    # drop shadow of the open book
    cv.fill_rect(34, 46, 968, 944, DESK_DK)
    # the two pages
    cv.fill_rect(LX0, PY0, LX1 - LX0, PY1 - PY0, PAPER)
    cv.fill_rect(RX0, PY0, RX1 - RX0, PY1 - PY0, PAPER)
    # spine shadow between the pages
    for i, c in enumerate(((210, 204, 184), (190, 183, 162),
                           (170, 162, 140))):
        cv.vline(LX1 + i, PY0, PY1 - 1, c, 1)
        cv.vline(RX0 - 1 - i, PY0, PY1 - 1, c, 1)
    cv.vline((LX1 + RX0) // 2, PY0, PY1 - 1, (150, 142, 120), 2)
    here = os.path.dirname(os.path.abspath(__file__))
    photo = load_png_rgb(os.path.join(here, "assets", "holder-photo.png"))
    photo = clean_photo_background(photo)
    mrz = draw_left_page(cv, photo)
    draw_right_page(cv)
    return cv, mrz


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(outdir, exist_ok=True)
    except OSError:
        outdir = "."
    path = os.path.join(outdir, "entry.png")
    cv, (line1, line2) = draw()
    png = write_png(path, cv)
    print("path:  ", path)
    print("sha256:", hashlib.sha256(png).hexdigest())
    print("bytes: ", len(png))
    print("size:  ", cv.w, "x", cv.h)
    print("mrz1:  ", line1)
    print("mrz2:  ", line2)


if __name__ == "__main__":
    main()
