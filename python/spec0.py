import os
import matplotlib.pyplot as plt
FROOT = "C:\\path\\to\\your\\spectral\\txt\\folder\\"

def load_ocvt(f):
    with open(f) as ff:
        # if header add @ftr for l in ff: if ">>>>>Begin" not in l and ">>>>>End" not in l and
        # this is for headerless ascii output in oceanview
        px = [(float(p[0]), float(p[1])) for l in ff if (p := l.strip().split()) and len(p) >= 2 and p[0].replace('.', '', 1).isdigit()]
    return zip(*px) if px else ([], [])

# who needs try catches if we hardcode it
fn = os.path.join(FROOT, "q_Reflection__1083__2766.txt")
wavlen, ntnsity = load_ocvt(fn)

plt.figure(figsize=(10,6))
plt.plot(wavlen, ntnsity, linewidth=1)
plt.title("Spectrum")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Intensity (au)")
plt.ylim(-2000,2000)
plt.xlim(350,1000)
plt.grid(True)
plt.show()
