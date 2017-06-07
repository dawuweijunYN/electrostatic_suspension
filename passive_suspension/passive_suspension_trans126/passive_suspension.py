from numpy import pi, sin, sinh, cos, arange, subtract, around, exp, insert, arctan
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from config import *
import os

def calc_cap_vs_gap(start_gap=1e-6, end_gap=20e-6, numcalc=20):
    '''
    Writes parameters of gap to file params.txt,
    starts ANSYS cap_calc.bat simulation and reads the results
    '''
    with open('cap_calc_params.txt','w') as f:
        f.truncate()
        f.write('d_min = '+     str(start_gap)+'\n')
        f.write('d_max = '+     str(end_gap)  +'\n')
        f.write('NUM_CALCS = '+ str(numcalc)  +'\n')
        f.write('d_inc = (d_max-d_min)/(NUM_CALCS-1)')
    os.system('cap_calc_start.bat')
    cap_list, gap_list = read_from_file('./output/CAPACITANCE_VS_GAP.txt')
    with open('cap_vs_gap_data.txt','w') as f:
        f.truncate()
        n = 0
        for cap, gap in zip(cap_list, gap_list):
            n += 1
            f.write('CAP'+str(n)+' = '+str(cap)+'\n')
            f.write('GAP'+str(n)+' = '+str(gap)+'\n')
    return cap_list, gap_list

def read_from_file(fname,header=False):
    '''
    Reads the results of capacitance calculation
    '''
    cap_list, gap_list = [], []
    with open(fname,'r') as f:
        if header == True: f = f.readlines()[14:]
        for line in f:
            gap_list.append(float(line.split()[0]))
            cap_list.append(float(line.split()[1]))
    return cap_list, gap_list

def calc_force_vs_gap(start_gap=1e-6, end_gap=20e-6, numcalc=20, solid=False):
    with open('params_pas_susp.txt','w') as f:
        f.truncate()
        f.write('d_min = '+     str(start_gap)+'\n')
        f.write('d_max = '+     str(end_gap)  +'\n')
        f.write('NUM_CALCS = '+ str(numcalc)  +'\n')
        f.write("ANALYSIS_TYPE = 'force_calc'"+'\n')
        f.write('d_inc = (d_max-d_min)/(NUM_CALCS-1)')
    if solid == False:
        os.system('pas_susp_start.bat')
    else:
        os.system('pas_susp_start_SOLID.bat')
    force_list, gap_list = read_from_file('./output/force_y.txt')
    return force_list, gap_list

def calc_dynamic(init_gap=30e-6, mass=8,time=time*2,dt=dt*2):
    with open('params_pas_susp.txt','w') as f:
        f.truncate()
        f.write('d_max = 100e-6'+'\n')
        f.write('mass = ' +    str(mass)+'\n')
        f.write('init_gap = '+ str(init_gap)  +'\n')
        f.write('dyntime = ' +    str(time)+'\n')
        f.write('dyndt = ' +      str(dt)+'\n')
        f.write('NUM_CALCS = 1' +'\n')
        f.write("ANALYSIS_TYPE = 'dynamic_calc'")
    os.system('pas_susp_start.bat')
    uy_list, time_list = read_from_file('./output/dyn_UY_vs_Time.txt',True)
    return uy_list, time_list

def calc_theory_cap(gap_list, S, eps_r=1, eps_0=8.854e-12):
    '''Calculates theory capacitance of parallel plate capacitor
    with S, gap, eps_r and eps_0 attributes.
    '''
    cap = []
    for gap in gap_list:    
        cap.append(eps_r*eps_0*S/gap)
    return cap  

def calc_theory_force(gap_list):
    force = []
    for gap in gap_list:
        C = EPS_0*S/gap
        peak_coef = (2*pi*V_freq)*ind-1/(2*pi*V_freq)/C
        # print(V_freq*ind,1/V_freq/C) 
        q0 = V_amp/((2*pi*V_freq)*(res**2+(peak_coef)**2)**0.5)
        force.append( q0**2/(2*EPS_0*S)/2 )
    return force

def problem_properties():

    gap = 3e-6
    C = EPS_0*S/gap
    w0 = (1/ind/C)**0.5
    beta = res/2/ind
    n = 0.5*res/ind
    phi0 = arctan(res/(V_freq*ind-1/V_freq/C))
    q0 = V_amp/(2*pi*V_freq*(res**2+(2*pi*V_freq*ind-1/(2*pi*V_freq)/C)**2)**0.5)
    q0_2 = V_amp*S*EPS_0*4*pi/(  (ind*S*EPS_0*4*pi*(V_freq)**2-4*pi*gap)**2 + (res*S*EPS_0*4*pi*(V_freq))**2  )**0.5
    q0_3 = V_amp/ind/(((w0**2-(2*pi*V_freq)**2))**2+4*n**2*(2*pi*V_freq)**2)**0.5
    print('Problem properties with gap:',gap)
    print('Capacitance:',C,'| R:',res,'| L:',ind,'| w:',V_freq, '| wL-1/wc',V_freq*ind -1/V_freq/C, '| phi0 =',phi0,'| sin(phi0)=',sin(phi0), '| xi =',1/2*res*(C/ind)**0.5)
    print('q0 =',q0, '| U_cmax =',q0/C,q0_2/C,q0_3/C)
    print(res**2,',',4*ind/C)
    print((10e-6/(EPS_0*S*ind))**0.5)


def save_solution(gap_list,cap_cae,force_cae):
    fname = 'sol' +'_S'+ str(S) +'_w'+ str(V_freq) +'_R'+ str(res) +'_I'+ str(ind) +'.txt'
    with open('./saved/'+fname,'w') as f:
        f.truncate()
        f.write('gap_list = '+str(gap_list)+'\n')
        f.write('cap_cae = '+str(cap_cae)+'\n')
        f.write('force_cae = '+str(force_cae)+'\n')

def plot_cap():
    cap_cae, gap_list = read_from_file('./output/CAPACITANCE_VS_GAP.txt')
    cap_theory = calc_theory_cap(gap_list, S)
    fig = plt.figure()
    fig.set_size_inches(10, 10)
    p1 = fig.add_subplot(111)
    p1.plot(gap_list,cap_cae,marker='o',label='$FEM$',linewidth=2, color='r',markersize=6, mew=0)
    p1.plot(gap_list,cap_theory,marker='o', label='$Parallel$ $plate$ $theory$',linewidth=1,linestyle='--', color='b',markersize=4, mew=0)
    p1.set_xlabel("$gap, m$", fontsize=15)
    p1.set_ylabel("$Capacinatce, F$", fontsize=15)
    p1.legend(loc='upper right',fontsize=15,numpoints=1)
    p1.grid()
    p1.set_title('$Capacitance$ $vs$ $gap$',fontsize=20)
    fig.savefig('capacitance_vs_gap',dpi=300)
    cap_compare = []
    for gap, cae, theory in zip(gap_list, cap_cae, cap_theory):
        cap_compare.append(abs((theory/cae-1)*100))
    print('Capacitance difference max at gap =',str('%6.2e'%gap_list[cap_compare.index(max(cap_compare))]),':',str('%6.2f'%(max(cap_compare))),'%')

def plot_force_vs_gap():
    force_cae, gap_list = read_from_file('./output/force_y.txt')
    force_theory = calc_theory_force(gap_list)
    fig = plt.figure()
    fig.set_size_inches(10, 6)
    p1 = fig.add_subplot(111)
    p1.plot(gap_list,[x/2 for x in force_cae],marker='o', label="$FEM$ $trans126$",linewidth=2, color='r',markersize=6, mew=0)
    p1.plot(gap_list,force_theory,marker='o', label="$Analytical$",linewidth=1,linestyle='--', color='b',markersize=4, mew=0)
    p1.legend(loc='best',fontsize=15,numpoints=1)
    p1.set_xlabel("$gap, m$", fontsize=15)
    p1.set_ylabel("$Force, N$", fontsize=15)
    p1.set_title('$Ponderomotive$ $force$ $vs$ $gap$ $(Fixed$ $plates)$',fontsize=20)
    # p2 = fig.add_subplot(212)
    # p2.plot(gap_list,force_theory,marker='o', label="",linewidth=1,linestyle='--', color='b',markersize=4, mew=0)
    fname = './saved/plot_force' +'_S'+ str(S) +'_w'+ str(V_freq) +'_R'+ str(res) +'_I'+ str(ind) +'.png'
    fig.savefig(fname, dpi=300)
    fig.savefig('plot_force',dpi=300)
    
def plot_dynamic():
    uy_list, time_list = read_from_file('./output/dyn_UY_vs_Time.txt',True)
    force_list, time_list = read_from_file('./output/dyn_Force_vs_Time.txt',True)
    volt_list, time_list = read_from_file('./output/dyn_Volt_vs_Time.txt',True)

    print(init_gap)
    C = EPS_0*S/init_gap
    e_ode = odeint(charge, [0.0, 0.0], time_list)[:, 0]
    U_ode = [-x/C for x in e_ode]
    F_ode = [x**2/(2*EPS_0*S) for x in e_ode]

    fig = plt.figure()
    fig.set_size_inches(12, 12)
    p1 = fig.add_subplot(311)
    p1.plot(time_list ,[-init_gap+x for x in uy_list],marker='o', label="FEM trans126",linewidth=2, color='r',markersize=0, mew=0)
    p1.plot([0, time_list[-1]],[0,0],linewidth=2, color='k')
    p1.legend(loc='best',fontsize=15,numpoints=1)
    p1.set_xlabel("time, sec", fontsize=15)
    p1.set_ylabel("displacement, m", fontsize=15)
    p2 = fig.add_subplot(312)
    # p2.plot(time_list ,[x-mass*g for x in force_list],marker='o', label="",linewidth=0.5, color='r',markersize=0, mew=0)
    
    
    p2.plot(time_list ,force_list,marker='o', label="",linewidth=1, color='r',markersize=0, mew=0)
    p2.plot(time_list ,F_ode,marker='o', label="",linewidth=0.5, color='b',markersize=0, mew=0,linestyle='--')

    p2.grid()
    p2.set_xlabel("time, sec", fontsize=15)
    p2.set_ylabel("forces sum, N", fontsize=15)
    p3 = fig.add_subplot(313)

    
    p3.plot(time_list ,volt_list,marker='o', label="F",linewidth=1, color='r',markersize=0, mew=0)
    p3.plot(time_list ,U_ode,marker='o', label="F",linewidth=0.5, color='b',markersize=0, mew=0,linestyle='--')

    p3.set_xlabel("time, sec", fontsize=15)
    p3.set_ylabel("voltage drop on capacitor, V", fontsize=15)    
    fig.savefig('./saved/dynamic_plot',dpi=300)
    fig.savefig('dynamic_plot',dpi=300)

def charge(y, t):
     y1, y2 = y
     dydt = [y2, 1/ind*(V_amp*sin(2*pi*V_freq*t) - y1*init_gap/S/EPS_0 - res*y2)]
     return dydt

'''SOLVE CAPACITY'''

# cap_cae, gap_list = calc_cap_vs_gap(start_gap, end_gap, n)

# problem_properties()

# '''SOLVE FORCE'''
# force_cae, gap_list = calc_force_vs_gap(start_gap, end_gap, n)
# save_solution(gap_list,cap_cae,force_cae)

# plot_cap()
# plot_force_vs_gap()

mass =  0.122395/2/g
init_gap =  3e-6
     
# uy_list, time_list = calc_dynamic(init_gap,mass,dt,dt*2)

plot_dynamic()

# C = EPS_0*S/init_gap
# time_list = list(arange(0,1e-4*32,1/V_freq/32))

# e_ode = odeint(charge, [0.0, 0.0], time_list)[:, 0]
# U_ode = [-x/C for x in e_ode]
# F_ode = [x**2/(2*EPS_0*S) for x in e_ode]

# print(1/(ind*C)**0.5/2/pi)

# gap_list = list(arange(0.1e-6,30e-6,0.1e-6))
# force_theory = calc_theory_force(gap_list)

# fig = plt.figure()
# fig.set_size_inches(12, 12)
# p1 = fig.add_subplot(311)

# p1.plot(gap_list,force_theory,marker='o', label="$Analytical$",linewidth=1,linestyle='-', color='b',markersize=0, mew=0)

# p2 = fig.add_subplot(312)
# p2.plot(time_list ,F_ode,marker='o', label="",linewidth=0.5, color='b',markersize=0, mew=0,linestyle='-')

# p3 = fig.add_subplot(313)
# potential =[]
# for gap in gap_list:
#     potential.append(-g*gap-V_amp**2/(2*res*mass*2*pi*V_freq)*arctan((2*pi*V_freq*ind-gap/(2*pi*V_freq*EPS_0*S))/res))

# p3.plot(gap_list, potential)

# fig.savefig('plot_testing',dpi=50)


# plt.show()
