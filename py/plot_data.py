import sys
import matplotlib.pyplot as plt
from v2t import v2t
from uncertainties import ufloat
import numpy as np

# 737.7 G/A
c2h = lambda current: ufloat(0.07377,0.000005)*current

def readfile(logfilename):
	data = []
	with open(logfilename,'r') as f:
		for line in f.readlines():
			tup = line.strip().split(',')
			data.append((float(tup[0]),float(tup[1])))
	return zip(*data)

def v2t_modified(v):
	try:
		return v2t(v)
	except AssertionError:
		return ufloat(273, 269)

def data(logfilename, type):
	if type=='lockin':
		time, lockin = readfile(logfilename)
		temp = [v2t_modified(ufloat(v,1e-7)) for v in lockin]
		return time, temp
	elif type=='ps':
		time, current = readfile(logfilename)
		field = [c2h(ufloat(c, 1e-3)) for c in current]
		return time, field
	else:
		print "File type unknown."

def time_slice(x, slice):
	index1 = np.array(x).searchsorted(slice[0])
	index2 = np.array(x).searchsorted(slice[1])
	return index1, index2

def find_ramp(t, c):
	slice = None
	next = False
	c0 = c[0]
	for i in range(len(c)):
		if np.abs(c0-c[i])>0.01:
			slice = (i,i)
			next = True
			break
	if next:
		for j in range(len(c[i:])):
			if np.abs(c[i+j+1]-c[i+j])/(t[i+j+1]-t[i+j])<0.1:
				slice = (i, i+j)
				break
	if slice:
		ramp = (c[slice[1]]-c[slice[0]])/(t[slice[1]]-t[slice[0]])
		return ramp, slice
	else:
		return None, None

def ramp_rates(psfilename):
	t, c = readfile(psfilename)
	ramps = []
	ramp, slice = find_ramp(t, c)
	while ramp:
		ramps.append( (ramp, slice) )
		ramp, new = find_ramp(t[slice[1]:], c[slice[1]:])
		if new:
			slice = (slice[1]+new[0], slice[1]+new[1])
	return ramps

def plotdata(lockinfilename, psfilename, title='Adiabatic Demagnetization', slice=None):
	timet, temp = data(lockinfilename, 'lockin')
	timef, field = data(psfilename, 'ps')
	t0 = min(timet[0], timef[0])
	tt = np.array(timet)-t0
	tf = np.array(timef)-t0
	tfinal = max(tt[-1], tf[-1])
	if slice:
		i1, i2 = time_slice(tt, slice)
		tt = tt[i1:i2]-tt[i1]
		temp = temp[i1:i2]
		i1, i2 = time_slice(tf, slice)
		tf = tf[i1:i2]-tf[i1]
		field = field[i1:i2]
		tfinal = max(tt[-1],tf[-1])
	plt.subplot(211)
	plt.plot(tt, [t.n for t in temp])
	plt.xlim(0,tfinal)
	plt.xlabel('Time (s)'); plt.ylabel('Temperature (K)')
	plt.subplot(212)
	plt.plot(tf, [f.n for f in field])
	plt.xlim(0,tfinal)
	plt.xlabel('Time (s)'); plt.ylabel('Field (T)')
	plt.show()

datadir = "/Users/rex/Dropbox/Physics 108/data"
# example plot
# plotdata('%s/lock-in-1426122746.log'%datadir, '%s/power-supply-1426122742.log'%datadir, slice=(840,980))
