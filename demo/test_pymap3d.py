import pymap3d

lat, lon, alt = 42.5, -70.5, 1000
lat0, lon0, alt0 = 42.5, -70.5, 0
n, e, d = pymap3d.geodetic2ned(lat, lon, alt, lat0, lon0, alt0)
print(n, e, d)