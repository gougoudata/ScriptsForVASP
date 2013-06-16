#!/usr/local/python/2.7.1/bin/python
# _Display_fit.py test_type line_from line_to P/M

import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import re

def centralfit(x, y):
    list = []
    x = np.array(x)
    y = np.array(y)
    for a in np.arange(160, 180, 0.1):
        for c in np.arange(-14.1, -14, 0.001):
            y_fit = a*(x**2)+c
            ss_resid = np.sum((y - y_fit)**2)
            list.append([ss_resid, a, c])
    the_one = list[np.array(list)[:,0].argmin()]
    y_fit = the_one[1]*(x**2)+the_one[2]
    y_avg = np.sum(y)/len(y)
    ss_resid = np.sum((y - y_fit)**2)
    ss_total = np.sum((y-y_avg)**2)
    r_squared = 1 - ss_resid/ss_total
    return (the_one[1], the_one[2], r_squared, y_fit)

def polyfit(x, y, degree):
    popts = np.polyfit(x, y, degree, full=True)
    p = np.poly1d(popts[0])
    x_fit = np.linspace(sorted(x)[0], sorted(x)[-1], 100)
    y_fit = p(x_fit)
    y_avg = np.sum(y)/len(y)
    ss_total = np.sum((y-y_avg)**2)
    r_squared = 1 - popts[1]/ss_total
    return (p, r_squared[0], x_fit, y_fit)

def murnaghan_eqn(V, V0, B0, B0_prime, E0):
    return (E0 + B0/B0_prime * V * (1 + (V0/V)**B0_prime/(B0_prime - 1)) - V0 * B0/(B0_prime -1))
    
#def murnaghan_eqn2(V, V0, B0, B0_prime, E0):
#    return (E0 + 9*V0*B0/16. * (((V0/V)**(2/3) - 1)**3 * B0_prime + ((V0/V)**(2/3) - 1)**2 * (6 - 4*(V0/V)**(2/3))))

def murnaghan_fit(x, y):
    coeffs, pcov = curve_fit(murnaghan_eqn, x, y, [30, 2.5, 4, -20])
    x_fit = np.linspace(sorted(x)[0], sorted(x)[-1], 100)
    y_fit = murnaghan_eqn(x_fit, *coeffs)
    y_fit_eqlen = murnaghan_eqn(x, *coeffs)
    ss_resid = np.sum((y_fit_eqlen - y)**2)
    y_avg = np.sum(y)/len(y)
    ss_total = np.sum((y-y_avg)**2)
    r_squared = 1 - ss_resid/ss_total
    return (coeffs, r_squared, x_fit, y_fit)

test_type = sys.argv[1]
f = open(test_type+'_output.txt','rU')
file = f.readlines()
f.close()
line_from = int(sys.argv[2]); line_to = int(sys.argv[3])

if test_type == 'entest':
    ENCUT = []; energy = []
    for i in file[line_from:line_to]:
        ENCUT.append(float(i.split()[0]))
        energy.append(float(i.split()[4]))
    plt.plot(ENCUT, energy, 'o')
    plt.plot([ENCUT[0], ENCUT[-1]], [0.001, 0.001], 'k:')
    plt.xlabel('ENCUT (eV)')
    plt.ylabel('E (eV)')

elif test_type == 'kptest':
    nKP = []; energy = []
    for i in file[line_from:line_to]:
        nKP.append(float(i.split()[0]))
        energy.append(float(i.split()[4]))
    plt.plot(nKP, energy, 'o')
    plt.plot([nKP[0], nKP[-1]], [0.001, 0.001], 'k:')
    plt.xlabel('nKP')
    plt.ylabel('E (eV)')

elif test_type == 'lctest':
    scaling_factor = []; volume = []; energy = []
    for i in file[line_from:line_to]:
        scaling_factor.append(float(i.split()[0]))
        volume.append(float(i.split()[1]))
        energy.append(float(i.split()[2]))
    scaling_factor = np.array(scaling_factor)
    volume = np.array(volume)
    energy = np.array(energy)
    plt.plot(volume, energy, 'o', label="Original data")
    
    if sys.argv[4] == 'P':
        # fitting the 2nd order polynomial
        (p_vol, r_squared, volume_fit, energy_fit) = polyfit(volume, energy, 2)
        p_sf = np.poly1d(np.polyfit(scaling_factor, energy, 2))
        scaling_factor_eqlbrm = -p_sf[1]/2/p_sf[2]
        volume_eqlbrm = -p_vol[1]/2/p_vol[2]
        
        # plotting the 2nd order polynomial
        plt.plot(volume_fit, energy_fit, '-', label="2nd order polynomial")
        result_str = "E = %f x^2 + (%f) x + (%f)\n  R-squared is %f" % (p_vol[2], p_vol[1], p_vol[0], r_squared)
        plt.text(volume_fit[len(volume_fit)/4], energy_fit[6], result_str)
        
        # standrad output, directed to files by the bash script calling this python script
        print "2nd order polynomial fitting results (better for a small span of lattice constants):";
        print "  %s" % result_str
        print("  Equilibrium scaling factor is %f" % scaling_factor_eqlbrm)
        if scaling_factor_eqlbrm <= scaling_factor[0] or scaling_factor_eqlbrm >= scaling_factor[-1]:
            print("  !Equilibrium point is out of the considered range!")
        else:
            print("  V0 = %f\n  B0 = %f" % (volume_eqlbrm, -p_vol[1] * 160.2))
            print("  Total energy is %f" % energy_fit.min())
            np.savetxt(test_type+'_polyfit_data.dat', np.column_stack((volume_fit, energy_fit)), '%.6f', '\t')
    
    elif sys.argv[4] == 'M':
        # fitting the Murnaghan equation of state
        (coeffs_vol_M, r_squared_M, volume_fit_M, energy_fit_M) = murnaghan_fit(volume, energy)
        scaling_factor_eqlbrm = (coeffs_vol_M[0])**(1/3.)
        
        # plotting the Murnaghan equation of state
        plt.plot(volume_fit_M, energy_fit_M, '-', label="Murnaghan eqn of state")
        result_str = "R-squared is %f" % r_squared_M
        plt.text(volume_fit_M[len(volume_fit_M)/4], energy_fit_M[6], result_str)
        
        # standrad output, directed to files by the bash script calling this python script
        print "Murnaghan equation of state fitting results (better for a large span of lattice constants):"
        print "  %s" % result_str
        print("  Equilibrium scaling factor is %f" % scaling_factor_eqlbrm)
        if scaling_factor_eqlbrm <= scaling_factor[0] or scaling_factor_eqlbrm >= scaling_factor[-1]:
            print("  !Equilibrium point is out of the considered range!")
        else:
            print("  V0 = %f\n  B0 = %f\n  B0' = %f" % (coeffs_vol_M[0], coeffs_vol_M[1] * 160.2, coeffs_vol_M[2]))
            print("  Total energy is %f" % energy_fit_M.min())
            np.savetxt(test_type+'_eosfit_data.dat', np.column_stack((volume_fit_M, energy_fit_M)), '%.6f', '\t')
    
    plt.xlabel(r'Volume ($\AA^{3}$)')
    plt.ylabel('E (eV)')
    plt.legend()
    np.savetxt(test_type+'_orig_data.dat', np.column_stack((volume, energy)), '%.6f', '\t')
    
elif re.search('.*c[1-9][1-9].*', test_type) or re.search('A.*', test_type):     # meaning elastic const.
    delta = []; energy = []
    for i in file[line_from:line_to]:
        delta.append(float(i.split()[0]))
        energy.append(float(i.split()[1]))
        
    if re.search('.*c[1-9][1-9].*', test_type):
        (p, r_squared, delta_fit, energy_fit) = polyfit(delta, energy, 2)
        plt.plot(delta, energy, 'o', delta_fit, energy_fit, '-')
        result_str = "E = %f x^2 + (%f) x + (%f)\nR-squared is %f" % (p[2], p[1], p[0], r_squared)
    elif re.search('A.*', test_type):
        (p, r_squared, delta_fit, energy_fit) = polyfit(delta, energy, 3)
        plt.plot(delta, energy, 'o', delta_fit, energy_fit, '-')
        result_str = "E = %f x^3 + (%f) x^2 + (%f) x + (%f)\nR-squared is %f" % (p[3], p[2], p[1], p[0], r_squared)
        
    plt.text(delta_fit[len(delta_fit)/4], energy_fit[6], result_str)
    plt.xlabel('Delta (ratio)')
    plt.ylabel('E (eV)')
    print "Fitting result:", result_str
    
    
    
    
    
#    a, c, r_squared, y_fit = centralfit(delta, energy)
#    plt.plot(delta, y_fit, '-', label='E = a*x^2 + c')
#    result_str2 = "E = %.3f x^2 + (%.3f)\nR-squared is %f" % (a, c, r_squared)
#    plt.legend()
#    print "Fitting result:", result_str2

plt.savefig('fit_curve.png')
#plt.show()