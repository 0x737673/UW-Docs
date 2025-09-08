import numpy as np
from pathlib import Path
from PIL import Image

def reconstructFF():
    """Reads a folder full of headerless txts and bludgeons them into a greyscale img"""
    # lotsa hardcoding since it's night oclock and I've got stuff2do
    YSTEPS = 21
    folder = Path("C:\\path\\to\\txt\\dump\\")
    files = sorted(folder.iterdir(), key=lambda f: f.stat().st_mtime)
    
    px = []
    for f in files:
        try:
            data = np.genfromtxt(f, dtype=float, skip_header=1)
            if data.ndim > 1:
                data = data.flatten()
            px.extend(data)
        except Exception as e:
            print(f"Skipping {f.name}: {e}")
    
    px = np.array(px, dtype=np.uint8)
    
    col = row = YSTEPS + 1
    px_count = row * col
    
    # snip vs pad
    if len(px) < px_count:
        imgt = np.pad(px, (0, px_count - len(px)), 'constant')
    else:
        imgt = px[:px_count]
    
    # reconstruct
    img = np.zeros((row, col), dtype=np.uint8)
    idx = 0
    for c in range(col):
        for r in range(row):
            if c % 2 == 0: # evens ^
                img[r, c] = imgt[idx]
            else:       # odds v
                img[row-1-r, c] = imgt[idx]
            idx += 1

    # save raw-ish data
    grey = Image.fromarray(img, mode="L")  # 8-bit grey
    grey.save("clusterduck.png")
    grey.show()
    np.savetxt("raw-px.txt", img, fmt="%d") 

    # upscale cuz 22x22 smol
    img = np.repeat(np.repeat(img, 20, axis=0), 20, axis=1)   # 1 -> 20x20
    grey_up = Image.fromarray(img, mode="L")
    grey_up.save("clustertruck.png")
    grey_up.show()
    np.savetxt("bloat-px.txt", img, fmt="%d") 

reconstructFF()