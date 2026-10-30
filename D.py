import time, random, sys, os, shutil
from PIL import Image, ImageDraw

os.system("")  # enables colors in Windows consoles

IMAGE = r"C:\Users\Ralph Dainiell\Downloads\mike.jpg"
CHARS = ".:-=+*#%@"          # light strokes -> heavy strokes

if not os.path.exists(IMAGE):
    sys.exit(f"Can't find {IMAGE}\nSave the original photo there as mike.jpg and run again.")

img = Image.open(IMAGE).convert("RGB")
W, H = img.size

# ---- find the white background (so it stays empty, but the eyeball stays white)
bg = img.copy()
ImageDraw.floodfill(bg, (5, 5), (255, 0, 255), thresh=40)
bgpx = bg.load()

# ---- closed-eye version: cover the eyeball with skin and draw an eyelid
SKIN = (130, 190, 45)
LID = (45, 95, 15)
closed = img.copy()
d = ImageDraw.Draw(closed)
d.ellipse([0.25 * W, 0.70 * H, 0.95 * W, 1.24 * H], fill=SKIN)
d.arc([0.30 * W, 0.76 * H, 0.90 * W, 0.90 * H], 15, 165, fill=LID, width=max(4, W // 60))

def fit_size():
    t = shutil.get_terminal_size((120, 40))
    cols = min(t.columns - 2, (t.lines - 3) * 2)   # characters are ~2x taller than wide
    return max(40, cols)

def render(im, size):
    rows = size // 2
    small = im.resize((size, rows), Image.LANCZOS)
    mask = bg.resize((size, rows), Image.NEAREST)
    px, mpx = small.load(), mask.load()
    lines = []
    for y in range(rows):
        row = []
        for x in range(size):
            if mpx[x, y] == (255, 0, 255):
                row.append(" ")
                continue
            r, g, b = px[x, y]
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            ch = CHARS[min(len(CHARS) - 1, 2 + int(lum * (len(CHARS) - 2)))]
            m = max(r, g, b)
            if m < 90:                      # keep dark colors (navy cap) visible
                k = 90 / max(m, 1)
                r, g, b = min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k))
            row.append(f"\033[38;2;{r};{g};{b}m{ch}")
        lines.append("".join(row) + "\033[0m")
    return "\n".join(lines)

size = fit_size()
open_f, closed_f = render(img, size), render(closed, size)

sys.stdout.write("\033[2J\033[?25l")
try:
    while True:
        sys.stdout.write("\033[H" + open_f); sys.stdout.flush()
        time.sleep(random.uniform(1.5, 4))
        sys.stdout.write("\033[H" + closed_f); sys.stdout.flush()
        time.sleep(0.15)
except KeyboardInterrupt:
    sys.stdout.write("\033[0m\033[?25h\033[2J")