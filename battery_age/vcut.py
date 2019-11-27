import numpy as np
import pylab
Polynomial = np.polynomial.Polynomial

# cutoff for linear approximation
x_data = np.array([ .740, .370, .247, .185])
y_data = np.array([ 3.0, 3.1, 3.3, 3.2])

cmin, cmax = min(x_data), max(x_data)
pfit, stats = Polynomial.fit(x_data, y_data, 1, full=True, window=(cmin, cmax),
                             domain=(cmin, cmax))

print('Raw fit results:', pfit, stats, sep='\n')

Y0, m = pfit
resid, rank, sing_val, rcond = stats
rms = np.sqrt(resid[0]/len(y_data))

print('Fit: Y = {:.3f}[X] + {:.3f}'.format(m, Y0),
            '(rms residual = {:.4f})'.format(rms))

pylab.plot(x_data, y_data, 'o', color='k')
pylab.plot(x_data, pfit(x_data), color='k')
pylab.xlabel('Current (A)')
pylab.ylabel('Voltage (V)')
pylab.show()
