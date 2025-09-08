# mpcnc driver - Connect to FluidNC AP first
# G91 = relative positioning; G21 = set dist to mm; G1 linear move
# e.g. G1 X{dist} Y{dist}: Y0 = straight line on X axis; Y5 = simul diagonal
# TODO: derive steps/spd/dist from ms target
import requests, time, math, urllib.parse
import numpy as np
from PIL import Image
from pathlib import Path
WATCHING = Path("C:\\ocviewtest")
_lastf = None # from ^
reconstructed = np.array([], dtype=np.uint8) # final img
YSTEPS = 21; # num xtra steps to go B to T completely (22: +21)
SPEED = f"F{60 * 8}"; # 8mm/s, feed rate in mm/min
DIST = 2.27; # mm to move

# funcs
def req(cmd):
    """Send cmd to stepper motors (no safety), returns a HTTP Response obj"""
    str = f"http://www.msftconnecttest.com/command?commandText={urllib.parse.quote(f"G91 G21 {cmd} {SPEED}")}" # CHECK NOT G20
    print(str)
    return requests.get(str)
    
def parse():
    """
    Parses the latest spectral .txt into greyscale image data.
    Returns: img buffer as 2d np[]
    """
    global _lastf
    global reconstructed
    # wait for newest modified file
    while True: # :[
        files = [f for f in WATCHING.iterdir()]
        if not files: 
            time.sleep(0.1)
            continue # restart

        newest = max(files, key=lambda f: f.stat().st_mtime)
        if newest != _lastf: 
            _lastf = newest
            break
        # if folder not empty, but file old: wait & retry
        time.sleep(0.1)    
    
    # normalize + conv
    px = np.loadtxt(newest, dtype=float)
    px = (px - px.min()) / (px.max() - px.min() + 1e-9) # zero offset
    grey = int((px*255).mean())
    reconstructed = np.append(reconstructed,grey)

def parsett():
    time.sleep(0.5)

def reconstruct():
    """reconstruct greyscale img from np array following snek pattern"""
    col = row = YSTEPS +1
    img = np.zeros((row, col), dtype=np.uint8)
    idx = 0
    
    # check for skyscrapers (1px wide, all px tall)
    px_count = row*col
    if len(reconstructed) < px_count:
        reconstructeded = np.pad(reconstructed, (0, px_count - len(reconstructed)), 'constant')
    else:
        reconstructeded = reconstructed[:px_count]
        
    for c in range(col):
        for r in range(row):
            if c % 2 == 0: # evens, traversing upwards
                img[r, c] = reconstructeded[idx]
            else: # odds, traversing downwards
                img[row-1-r, c] = reconstructeded[idx]
            idx += 1

    grey = Image.fromarray(img, mode='L')  # 8-bit grey
    grey.save("clusterduck.png")
    grey.show()
    np.savetxt("raw.txt", img, fmt="%d") 

# directions
left = f"G1 X-{DIST} Y0"
right = f"G1 X{DIST} Y0"
up = f"G1 X0 Y{DIST}"
down = f"G1 X0 Y-{DIST}"



# macros
def snek():
    """tells scanner to move in a snake pattern from the bottom left corner"""
    for _ in range(math.ceil(YSTEPS/2)):
        # up 21
        for _ in range(YSTEPS):
            req(up)
            parse()
        # right 1
        req(right)
        parse()
        # down 21
        for _ in range(YSTEPS):
            req(down)
            parse()
        # right 1
        req(right)
        parse()


# gogo
def driver():
    parse() # wait for 1st scan to appear to sync
    snek()
    reconstruct()

driver()