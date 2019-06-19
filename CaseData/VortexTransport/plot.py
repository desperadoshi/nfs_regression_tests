import numpy as np
import matplotlib.pyplot as plt
plt.style.use('sjc')
fig=plt.figure()
ax = fig.gca()

match_idx=1

ND = 2.0

p_order = 3
data_fname = "error_h_p%d.dat"%(p_order)
data = np.loadtxt(data_fname,skiprows=1,delimiter=',')
nDOF_arr = data[:,1]
uniq_arr, uniq_idx = np.unique(nDOF_arr, return_index=True)
data = data[uniq_idx,:]

nDOF_arr = data[:,1]
L2_arr = data[:,2]
h_arr = 1.0/(nDOF_arr**(1.0/ND))

ref_p_order = p_order + 1
b = np.log10(L2_arr[match_idx]) - (ref_p_order)*np.log10(h_arr[match_idx])
L2_ref_arr = 10.0**((ref_p_order)*np.log10(h_arr)+b)

ax.loglog(h_arr,L2_ref_arr,'-',label="%d th order accuracy"%(ref_p_order))
ax.loglog(h_arr,L2_arr,'o--',label="P%d"%(p_order))

p_order = 4
data_fname = "error_h_p%d.dat"%(p_order)
data = np.loadtxt(data_fname,skiprows=1,delimiter=',')
nDOF_arr = data[:,1]
uniq_arr, uniq_idx = np.unique(nDOF_arr, return_index=True)
data = data[uniq_idx,:]

nDOF_arr = data[:,1]
L2_arr = data[:,2]
h_arr = 1.0/(nDOF_arr**(1.0/ND))

ref_p_order = p_order + 1
b = np.log10(L2_arr[match_idx]) - (ref_p_order)*np.log10(h_arr[match_idx])
L2_ref_arr = 10.0**((ref_p_order)*np.log10(h_arr)+b)

ax.loglog(h_arr,L2_ref_arr,'-',label="%d th order accuracy"%(ref_p_order))
ax.loglog(h_arr,L2_arr,'o--',label="P%d"%(p_order))

ax.set_xlabel("h")
ax.set_ylabel(r"$L^2$")
ax.legend()

figname = "error_h.png"
fig.savefig(figname)
print("%s is saved."%(figname))

