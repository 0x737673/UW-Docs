from dataclasses import dataclass, field
import numpy as np
import math

WAVELENGTHS = 651 #350-1000nm inc

@dataclass
class StaticProperties():
    '''Static spectrometer properties'''
    refract_idx: float # air = 1
    num_aperture: float # NA = RI * sin(theta); see spec sheet (USB650 NA: 0.22)
    theta: float # half angle; tmax = arcsin(NA/RI); USB 650 ~= 12.71 deg, 25.4 deg full
    core_width: float # fiber core width in mm
    
    def _validate_props(self):
        '''only checks existence, not bounds'''
        if self.num_aperture is None and self.theta is None:
            raise RuntimeError("StaticProperties: One of num_aperture or theta must be defined in order to attempt spatial mapping") 
        elif self.num_aperture is None:
            self.num_aperture = self.refract_idx * math.degrees(math.sin(math.radians(self.theta)))
            print(f"StaticProps: num_aperture missing, set to {self.num_aperture} based on theta = {self.theta} deg")
        elif self.theta is None:
            self.theta = self.refract_idx * math.degrees(math.asin(self.num_aperture / self.refract_idx))
            print(f"StaticProps: theta missing, set to {self.theta} based on NA = {self.num_aperture}")
        print(f"RI: {self.refract_idx}, NA: {self.num_aperture}, theta (deg): {self.theta}, core width (mm): {self.core_width}")

    def estimate_pxl_width(self, zdist):
        '''estimates the physical "pixel" capture space (not CCD pixel width) for bare fiber given z-dist, theta, and NA

            Args:
                self:  
                zdist: distance from probe to surface in mm'''
        self._validate_props()
        pwidth = 2 * zdist * math.degrees(math.tan(math.radians(self.theta))) + self.core_width
        print(f"zdist: {zdist}, cwidth: {self.core_width}, estimated pixel capture diameter: {pwidth}mm")
        return pwidth

    def __init__(self, zdist, na=0.22, tmax=12.7, cwidth=0.2, ri=1.0):
        self.refract_idx = ri
        self.num_aperture = na
        self.theta = tmax
        self.core_width = cwidth
        self.pwidth = self.estimate_pxl_width(zdist)


@dataclass(slots=True)
class NMData():
    '''corresponds to a single-point capture of spectral data'''
    rel_x: int # diagnostic - relative x from start
    rel_y: int # diagnostic - relative y from start
    wavelengths: np.ndarray # (651,)

    def __post_init__(self):
        if self.wavelengths.shape != (WAVELENGTHS,):
            raise ValueError(f"Wavelength vector size mismatched, got: {self.wavelengths.shape} , expected: ({WAVELENGTHS},)")
    
    def get_wavelength(self, widx: int):
        '''get a single, specific wavelength value for the given int index (350 to 1000)'''
        return self.wavelengths[widx - 350]
    

@dataclass(slots=True)
class Snekstruct():
    '''Diagnostic datastruct for snake-pattern scans'''
    zdist: float # dist from probe to surface in mm -- eventually this may need reconsideration if dynamically uneven
    abs_start_loc: tuple[int, int] #coords (x, y) for the absolute position the scan was started at
    y_max_steps: int 
    x_max_steps: int # where x * y = scan area
    props: StaticProperties
    points: list[NMData] = field(default_factory=list)

    def save_wave_data(self, pt: NMData):
        self.points.append(pt)

    def d2X(self):
        return np.stack([p.wavelengths for p in self.points])

