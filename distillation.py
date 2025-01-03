import numpy as np
import streamlit as st
from matplotlib import pyplot as plt

def plotting(direction, alphas, lk, hk, xbots, xtops, nf, mtop, mbot):

    bBots = []  #create empty lists for intercept values in top and bottoms
    bTops = []      

    for i in xbots:  #iteratively assign b values to each component for both top and bottom op lines
        x = (1 - mbot) * i
        bBots.append(x)
    
    for i in xtops:
        x = (1 - mtop) * i
        bTops.append(x)
    
    j = 0 #iterator
    x = [] #defining lists
    y = []
    if direction:   #if stepping up column
        for i in xbots: #create lists of lists with each internal list refered to as subsets being assigned to a component
            c = [i] 
            x.append(c) #x values list
            y.append([0]) #y values list 0 as placeholder to allow to read value for while loop
            
        while j < 100 and y[lk - 1][-1] < xtops[lk - 1]: # <100 argument to ensure doesnt run forever and checking that top comp is not met
            
            v = 0 #iterator
            l = []
            
            for i in x: #create list of previously stepped x values
                l.append(i[-1])
            
            xarr = np.array(l) #use a numpy array to take dot product of x components and alpha values
            aarr = np.array(alphas)
            denom = sum(xarr * aarr)

            for i in alphas: #do y value stepping using the product of the component's alpha and x value then divide by denominator above
                num = i * x[v][-1]
                c = num/denom
                
                if j == 0: #replaces placeholder
                    y[v][0] = c
                
                else:
                    y[v].append(c) #adds y value to the component's y list
                    
                v += 1
                
            v = 0 #iterator 
            if j < nf: #if still below feed tray use bottom op line
                for i in y:
                    c = (i[-1] - bBots[v]) / mbot
                    x[v].append(c)
                    v += 1
            
            else: #if above feed tray use top op line
                for i in y:
                    c = (i[-1] - bTops[v]) / mtop
                    x[v].append(c)
                    v += 1
            j += 1
        return (j , y) #returns number of stages and the y values for plotting
            
    else:
        j += 1
        for i in xtops: #create list of component subsets no need for placeholder in y value lists
            c = [i]
            x.append(c)
            y.append([])

        while j < 100 and x[hk - 1][-1] < xbots[hk - 1]: # <100 used for force stop condition and other is for desired stop condition
            v = 0 #iterator
            l = []
            if j < nf: #if still above feed tray use top op line
                for i in x:
                    c = mtop * i[-1] + bTops[v]
                    y[v].append(c)
                    v += 1
                    
            else:
                for i in x: #if below feed tray use bottom op line
                    c = mbot * i[-1] + bBots[v]
                    y[v].append(c)
                    v += 1
            
            for i in y: #create list of previously found y values
                l.append(i[-1])
            
            xarr = np.array(l) #use numpy arrays to divide each component's y value by its alpha
            aarr = np.array(alphas)
            denom = sum(xarr / aarr)
            
            v = 0 #iterator
            for i in alphas: #equilibrium stepping from y to x values
                num = y[v][-1] / i
                c = num / denom
                x[v].append(c)
                v += 1
                
            j += 1
            
        return (j , x) #returns number of stages and x values for plotting

st.header("Multicomponent Distillation Calculator")
state = st.session_state
st.divider()
cols = st.columns(3)

with cols[0]:
    st.subheader('Antoine Coefficients')
    comps = st.number_input(label='Number of Components',value=2,min_value=1, max_value=10)

    nofc = np.linspace(1,comps,comps)
    antoine = []
    
    for i in nofc: #creates inputs for each component
        st.subheader('Component ' + str(int(i)))
        A = st.number_input(label = 'A ' + str(int(i)), value = 2.000,step = 0.001)
        B = st.number_input(label = 'B ' + str(int(i)), value = 2.00)
        C = st.number_input(label = 'C ' + str(int(i)), value = 2.00)
        
        n = (A,B,C)
        antoine.append(n) #collect antoine coefficients into a list of tuples
    
with cols[1]:
    st.subheader('Feed Conditions')
    zs = []
    
    for i in nofc:
        z = st.slider(
            label='Feed Composition of Component ' + str(int(i)),
            value= 1 / comps,
            min_value=0.001,
            max_value=1.000,
            )
        zs.append(z)
    
    if sum(zs) != 1:
        st.subheader('Feed Compositions do not Sum to 1')
        zs = [0] * comps
        stop = True
    
    else:
        stop = False
    
    q = st.number_input(
        label='Feed Quality',
        value=1.0,
    )
    
    T = st.number_input(label = 'Temperature of Feed Stream in C',value = 50.0,min_value = -273.0)
    nf = st.number_input(label = 'Feed Location',value = 5, min_value = 0)
    direction = st.toggle('Feed Location is Counting from Bottom')
    
with cols[2]:
    st.subheader('Design Specs')
    lk = st.slider(
        label='Light Key Component Number',
        value=1,
        min_value=1,
        max_value= comps,
    )
    
    lkD = st.slider(
        label='Fraction of Light Key Leaving in Distillate',
        value=0.90,
        min_value=0.01,
        max_value=0.99,
    )
    
    hk = st.slider(
        label='Heavy Key Component Number',
        value=2,
        min_value=1,
        max_value=comps,
    )
    
    if lk == hk:
        st.subheader('Keys must be different components')
    
    hkB = st.slider(
        label='Fraction of Heavy Key Leaving out Bottom',
        value=0.95,
        min_value=0.01,
        max_value=0.99,
    )
    
    R = st.number_input(label = 'Reflux Ratio',value = 5.0, min_value = 0.001)
    
pp = []

for i in antoine:
    if i[-1] + T == 0:
        stop = True
        st.subheader('Temperature is not valid for the Antoine Coefficients provided')
        break
    
    else:
        p = 10 ** (i[0] - i[1] / (T + i[2]))
        pp.append(p)

ref = min(pp)

j = 0
lnk = []
hnk = []
alpha = []
F = 100
Dlk = lkD * F * zs[lk - 1]
Blk = F * zs[lk - 1] - Dlk

Bhk = hkB * F * zs[hk - 1]
Dhk = F * zs[hk - 1] - Bhk

D = Dlk + Dhk
B = Blk + Bhk

if pp[lk - 1] < pp[hk - 1]:
    st.subheader('Error: Light key must be more volatile than heavy key')
    stop = True

elif not stop:
    for i in pp:
    
        x = i / ref
        alpha.append(x)
    
        if i < pp[lk - 1] and i > pp[hk - 1]:
            pp = []
            st.subheader('This Program Does not Support Distributed Keys')
            stop = True
            break
    
        elif i > pp[lk - 1]:
            stop = False
            D += F * zs[j]
        
        elif i < pp[hk - 1]:
            B += F * zs[j]
            stop = False
        
        j += 1

N = 1

if not (stop or D == 0 or B == 0):
    L = D * R
    V = D + L
    mtop = L / V

    xbots = []
    xtops = []
    v = 0
    for i in pp:
        if i > pp[lk - 1]:
            xtops.append((F * zs[v]) / D)
            xbots.append(0)
        
        elif i < pp[hk - 1]:
            xtops.append(0)
            xbots.append((F * zs[v]) / B)
    
        elif i == pp[lk - 1]:
            xtops.append(Dlk / D)
            xbots.append(Blk / B)
        
        elif i == pp[hk - 1]:
            xtops.append(Dhk / D)
            xbots.append(Bhk / B)
        
        v += 1

    Lp = L + q*F
    Vp = V - (1 - q) * F
    mbot = Lp / Vp

    N , values = plotting(direction, alpha, lk, hk, xbots, xtops, nf, mtop, mbot)
    
st.divider()

if direction:
    phase = 'Vapour'

else:
    phase = 'Liquid'

fig, ax = plt.subplots()
ax.set_ylim([0, 1])
ax.set_xlim([0, N])
ax.set_aspect(N-1)
ax.set_xlabel('Stage Number')
ax.set_ylabel('Mole Fraction in ' + phase)

xaxis = np.linspace(0,N-1,N)
colours = ['tab:red','tab:blue','tab:green','tab:orange','tab:yellow','tab:gray','tab:black','tab:olive','tab:pink','tab:purple']
v = 1
if not stop:
    for i in values:
        ax.plot(xaxis, np.array(i), label = "Component " + str(v), c = colours[v-1])
        v += 1
    ax.legend()

cols2 = st.columns(1)
with cols2[0]:
    st.pyplot(fig)
    st.metric('Number of Stages',N - 1)