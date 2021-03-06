#!/usr/local/python/2.7.1/bin/python
# Used by Cellinfo.sh to solve equations
# _Cellinfo_solver.py task volumn_of_primitive_cell input_data(in the form of a python list)

import sys
import numpy as np

task = sys.argv[1]
Vpcell = float(sys.argv[2])

if task =='rwigs':
    N_atoms = eval(sys.argv[3])
    r_input = np.array(eval(sys.argv[4]))
    V_raw = 0
    for i in range(len(r_input)):
        V_raw += 4/3. * np.pi * (N_atoms[i]*r_input[i]**3)
    ratio = (Vpcell/V_raw)**(1/3.)
    r = r_input * ratio
    print "You should use",
    for i in range(len(r)):
        print "%.5f" % r[i],
    print "as your RWIGS in INCAR to get 100% filling."
