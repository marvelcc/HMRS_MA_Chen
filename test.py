import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import random

# Initialize the sets and parameters of the model
# Sets of the model
component = ['k1', 'k2', 'k3']
supplier = ['l1', 'l2']
manu = ['f1', 'f2', 'f3', 'f4', 'f5']
remanu = ['g1', 'g2', 'g3', 'g4', 'g5']
hybrid = ['h1', 'h2', 'h3', 'h4', 'h5']
warehouse = ['i1', 'i2', 'i3']
collect = ['j1', 'j2', 'j3', 'j4']
disassembly = ['u1', 'u2', 'u3', 'u4', 'u5']
recycling = ['v1', 'v2', 'v3', 'v4', 'v5']
disposal = ['w1', 'w2', 'w3', 'w4', 'w5']
T = 10

# Activation cost of each facility
# C_f = {a: random.randrange(200,351)*10000 for a in manu}
# C_g = {a: random.randrange(200,351)*10000 for a in remanu}
# C_h = {a: random.randrange(200,351)*10000 for a in hybrid}
# C_j = {a: random.randrange(100,251)*1000 for a in collect}
# C_u = {a: random.randrange(100,251)*1000 for a in disassembly}
# C_v = {a: random.randrange(100,251)*1000 for a in recycling}
# C_w = {a: random.randrange(100,251)*1000 for a in disposal}
# static for testing ==================================================
C_f = {'f1': 2530000, 'f2': 2250000, 'f3': 2130000, 'f4': 2200000, 'f5': 3160000}
C_g = {'g1': 2140000, 'g2': 2120000, 'g3': 3380000, 'g4': 2360000, 'g5': 3390000}
C_h = {'h1': 2000000, 'h2': 2260000, 'h3': 2100000, 'h4': 2590000, 'h5': 2320000}
C_j = {'j1': 179000, 'j2': 120000, 'j3': 228000, 'j4': 225000}
C_u = {'u1': 142000, 'u2': 170000, 'u3': 128000, 'u4': 143000, 'u5': 102000}
C_v = {'v1': 108000, 'v2': 137000, 'v3': 187000, 'v4': 132000, 'v5': 101000}
C_w = {'w1': 203000, 'w2': 137000, 'w3': 240000, 'w4': 225000, 'w5': 177000}

# Production/processing cost for each type of facility
B_F = 20
B_G = 15
B_H = 17
B_H_bar = 10
B_J = 5
B_KU = 1
B_U = 2
B_V = 2
B_T = 3

# The procurement price for each component
# procurement_price = {a: random.randrange(1,7) for a in component}
# static for testing ==================================================
P_k = {'k1': 4, 'k2': 5, 'k3': 3}

# S between locations
S_lf = {('l1', 'f1'): 11, ('l1', 'f2'): 37, ('l1', 'f3'): 22, ('l1', 'f4'): 12, ('l1', 'f5'): 34, 
               ('l2', 'f1'): 43, ('l2', 'f2'): 25, ('l2', 'f3'): 19, ('l2', 'f4'): 12, ('l2', 'f5'): 16}
S_lh = {('l1', 'h1'): 49, ('l1', 'h2'): 28, ('l1', 'h3'): 23, ('l1', 'h4'): 23, ('l1', 'h5'): 22, 
               ('l2', 'h1'): 31, ('l2', 'h2'): 20, ('l2', 'h3'): 38, ('l2', 'h4'): 43, ('l2', 'h5'): 10}
S_fi = {('f1', 'i1'): 34, ('f1', 'i2'): 46, ('f1', 'i3'): 24, ('f2', 'i1'): 40, ('f2', 'i2'): 32, 
               ('f2', 'i3'): 48, ('f3', 'i1'): 36, ('f3', 'i2'): 33, ('f3', 'i3'): 23, ('f4', 'i1'): 13, 
               ('f4', 'i2'): 21, ('f4', 'i3'): 47, ('f5', 'i1'): 44, ('f5', 'i2'): 30, ('f5', 'i3'): 15}
S_gi = {('g1', 'i1'): 25, ('g1', 'i2'): 48, ('g1', 'i3'): 46, ('g2', 'i1'): 23, ('g2', 'i2'): 36, 
               ('g2', 'i3'): 19, ('g3', 'i1'): 37, ('g3', 'i2'): 42, ('g3', 'i3'): 17, ('g4', 'i1'): 24, 
               ('g4', 'i2'): 22, ('g4', 'i3'): 25, ('g5', 'i1'): 46, ('g5', 'i2'): 20, ('g5', 'i3'): 27}
S_hi = {('h1', 'i1'): 14, ('h1', 'i2'): 17, ('h1', 'i3'): 19, ('h2', 'i1'): 16, ('h2', 'i2'): 15, 
               ('h2', 'i3'): 43, ('h3', 'i1'): 12, ('h3', 'i2'): 40, ('h3', 'i3'): 45, ('h4', 'i1'): 20, 
               ('h4', 'i2'): 31, ('h4', 'i3'): 39, ('h5', 'i1'): 34, ('h5', 'i2'): 40, ('h5', 'i3'): 25}
S_ju = {('j1', 'u1'): 41, ('j1', 'u2'): 29, ('j1', 'u3'): 40, ('j1', 'u4'): 16, ('j1', 'u5'): 20, 
               ('j2', 'u1'): 45, ('j2', 'u2'): 33, ('j2', 'u3'): 37, ('j2', 'u4'): 32, ('j2', 'u5'): 29, 
               ('j3', 'u1'): 23, ('j3', 'u2'): 47, ('j3', 'u3'): 11, ('j3', 'u4'): 23, ('j3', 'u5'): 15, 
               ('j4', 'u1'): 41, ('j4', 'u2'): 32, ('j4', 'u3'): 44, ('j4', 'u4'): 32, ('j4', 'u5'): 38}
S_uw = {('u1', 'w1'): 29, ('u1', 'w2'): 30, ('u1', 'w3'): 45, ('u1', 'w4'): 26, ('u1', 'w5'): 42, 
               ('u2', 'w1'): 30, ('u2', 'w2'): 23, ('u2', 'w3'): 31, ('u2', 'w4'): 20, ('u2', 'w5'): 34, 
               ('u3', 'w1'): 34, ('u3', 'w2'): 14, ('u3', 'w3'): 15, ('u3', 'w4'): 30, ('u3', 'w5'): 30, 
               ('u4', 'w1'): 36, ('u4', 'w2'): 32, ('u4', 'w3'): 14, ('u4', 'w4'): 12, ('u4', 'w5'): 16, 
               ('u5', 'w1'): 45, ('u5', 'w2'): 45, ('u5', 'w3'): 45, ('u5', 'w4'): 43, ('u5', 'w5'): 12}
S_uv = {('u1', 'v1'): 28, ('u1', 'v2'): 44, ('u1', 'v3'): 40, ('u1', 'v4'): 31, ('u1', 'v5'): 40, 
               ('u2', 'v1'): 12, ('u2', 'v2'): 10, ('u2', 'v3'): 12, ('u2', 'v4'): 46, ('u2', 'v5'): 41, 
               ('u3', 'v1'): 44, ('u3', 'v2'): 37, ('u3', 'v3'): 39, ('u3', 'v4'): 33, ('u3', 'v5'): 28, 
               ('u4', 'v1'): 30, ('u4', 'v2'): 27, ('u4', 'v3'): 10, ('u4', 'v4'): 26, ('u4', 'v5'): 38, 
               ('u5', 'v1'): 14, ('u5', 'v2'): 43, ('u5', 'v3'): 34, ('u5', 'v4'): 43, ('u5', 'v5'): 28}
S_uh = {('u1', 'h1'): 32, ('u1', 'h2'): 24, ('u1', 'h3'): 40, ('u1', 'h4'): 27, ('u1', 'h5'): 38, 
               ('u2', 'h1'): 22, ('u2', 'h2'): 28, ('u2', 'h3'): 29, ('u2', 'h4'): 38, ('u2', 'h5'): 11, 
               ('u3', 'h1'): 17, ('u3', 'h2'): 27, ('u3', 'h3'): 31, ('u3', 'h4'): 18, ('u3', 'h5'): 44, 
               ('u4', 'h1'): 21, ('u4', 'h2'): 22, ('u4', 'h3'): 39, ('u4', 'h4'): 19, ('u4', 'h5'): 46, 
               ('u5', 'h1'): 46, ('u5', 'h2'): 33, ('u5', 'h3'): 18, ('u5', 'h4'): 46, ('u5', 'h5'): 45}
S_ug = {('u1', 'g1'): 44, ('u1', 'g2'): 33, ('u1', 'g3'): 24, ('u1', 'g4'): 14, ('u1', 'g5'): 48, 
               ('u2', 'g1'): 49, ('u2', 'g2'): 36, ('u2', 'g3'): 11, ('u2', 'g4'): 21, ('u2', 'g5'): 34, 
               ('u3', 'g1'): 17, ('u3', 'g2'): 15, ('u3', 'g3'): 38, ('u3', 'g4'): 20, ('u3', 'g5'): 25, 
               ('u4', 'g1'): 45, ('u4', 'g2'): 35, ('u4', 'g3'): 33, ('u4', 'g4'): 33, ('u4', 'g5'): 38, 
               ('u5', 'g1'): 47, ('u5', 'g2'): 34, ('u5', 'g3'): 12, ('u5', 'g4'): 15, ('u5', 'g5'): 12}
S_vf = {('v1', 'f1'): 10, ('v1', 'f2'): 38, ('v1', 'f3'): 37, ('v1', 'f4'): 45, ('v1', 'f5'): 16, 
               ('v2', 'f1'): 31, ('v2', 'f2'): 49, ('v2', 'f3'): 30, ('v2', 'f4'): 25, ('v2', 'f5'): 18, 
               ('v3', 'f1'): 23, ('v3', 'f2'): 13, ('v3', 'f3'): 22, ('v3', 'f4'): 33, ('v3', 'f5'): 49, 
               ('v4', 'f1'): 31, ('v4', 'f2'): 21, ('v4', 'f3'): 30, ('v4', 'f4'): 18, ('v4', 'f5'): 44, 
               ('v5', 'f1'): 25, ('v5', 'f2'): 14, ('v5', 'f3'): 22, ('v5', 'f4'): 38, ('v5', 'f5'): 14}
S_vh = {('v1', 'h1'): 34, ('v1', 'h2'): 44, ('v1', 'h3'): 17, ('v1', 'h4'): 35, ('v1', 'h5'): 29, 
               ('v2', 'h1'): 17, ('v2', 'h2'): 27, ('v2', 'h3'): 31, ('v2', 'h4'): 42, ('v2', 'h5'): 15, 
               ('v3', 'h1'): 21, ('v3', 'h2'): 33, ('v3', 'h3'): 10, ('v3', 'h4'): 34, ('v3', 'h5'): 22, 
               ('v4', 'h1'): 38, ('v4', 'h2'): 48, ('v4', 'h3'): 38, ('v4', 'h4'): 17, ('v4', 'h5'): 42, 
               ('v5', 'h1'): 14, ('v5', 'h2'): 21, ('v5', 'h3'): 43, ('v5', 'h4'): 11, ('v5', 'h5'): 13}

# Emission in kg per product or component
E_F = 0.5
E_G = 0.3
E_H = 0.4
E_J = 0.07
E_U = 0.2
E_KU = 0.01
E_V = 0.2
E_W = 0.8
E_P = 0.0025
E_K = 0.0005

# Cost in euro
pi = 1.5 # per kg 
omega_p = 0.03 # per km
omega_k = 0.006 # per km

# Amount of component component in a product
R_k = {'k1': 2, 'k2': 3, 'k3': 4}

# Demand at each distribution center
# demand_i = {a: random.randrange(10,31) * 1000 for a in warehouse}
# static for testing ==================================================
D_i = {'i1': 23000, 'i2': 32000, 'i3': 11000}



# Returned product
# M_j = {a: random.randrange(15,26) * 1000 for a in collect }
# static for testing ==================================================
M_j = {'j1': 20000, 'j2': 20000, 'j3': 15000, 'j4': 25000}

# Capacity of each facility
# CAP_f = {a: random.randrange(15,25) * 1000 for a in manu }
# CAP_g = {a: random.randrange(8,14) * 1000 for a in remanu }
# CAP_h = {a: random.randrange(9,15) * 1000 for a in hybrid }
# CAP_h_bar = {a: random.randrange(5,10) * 1000 for a in hybrid }
# CAP_j = {a: random.randrange(8,15) * 1000 for a in collect }
# CAP_u = {a: random.randrange(10,15) * 1000 for a in disassembly }
# CAP_Ku = {a: random.randrange(30,50) * 300 for a in component for b in disassembly }
# CAP_Kv = {a: random.randrange(15,25) * 300 for a in component for b in recycling }
# CAP_Kw = {a: random.randrange(15,25) * 300 for a in component for b in disposal}
# static for testing ==================================================
CAP_f = {'f1': 16000, 'f2': 18000, 'f3': 22000, 'f4': 15000, 'f5': 22000}
CAP_g = {'g1': 10000, 'g2': 9000, 'g3': 8000, 'g4': 12000, 'g5': 8000}
CAP_h = {'h1': 14000, 'h2': 10000, 'h3': 11000, 'h4': 9000, 'h5': 12000}
CAP_h_bar = {'h1': 5000, 'h2': 5000, 'h3': 7000, 'h4': 6000, 'h5': 6000}
CAP_j = {'j1': 15000, 'j2': 15000, 'j3': 15000, 'j4': 15000}
CAP_u = {'u1': 120000, 'u2': 140000, 'u3': 110000, 'u4': 120000, 'u5': 130000}
CAP_Ku = {'u1': 90000, 'u2': 144000, 'u3': 111000, 'u4': 121000, 'u5': 110000}
CAP_Kv = {'v1': 5700, 'v2': 7200, 'v3': 6600, 'v4': 6200, 'v5': 5900}
CAP_Kw = {'w1': 5400, 'w2': 5700, 'w3': 7200, 'w4': 5900, 'w5': 6400}
CAP_CO2 = 4000000

# Percentage of EoU (a), EoL (b) and disposal (c) products
# a = round(random.uniform(0.5, 0.7), 2)
# b = round(random.uniform(0.15, 0.4), 2)
# c = max(round(1 - a - b, 2), 0.1)
# static for testing ==================================================
alpha = 0.65
beta = 0.25
gamma = 0.1

# Create Model
m = gp.Model('HMRS')

# Add decision variables
# Binary decision variables
X_f = m.addVars(manu, vtype=GRB.BINARY)
X_g = m.addVars(remanu, vtype=GRB.BINARY)
X_h = m.addVars(hybrid, vtype=GRB.BINARY)
X_j = m.addVars(collect, vtype=GRB.BINARY)
X_u = m.addVars(disassembly, vtype=GRB.BINARY)
X_v = m.addVars(recycling, vtype=GRB.BINARY)
X_w = m.addVars(disposal, vtype=GRB.BINARY)

# Quantity of flow between facilities
Q_klf = m.addVars(component, supplier, manu, vtype=GRB.INTEGER, lb=0)
Q_klh = m.addVars(component, supplier, hybrid, vtype=GRB.INTEGER, lb=0)
Q_fi = m.addVars(manu, warehouse, vtype=GRB.INTEGER, lb=0)
Q_gi = m.addVars(remanu, warehouse, vtype=GRB.INTEGER, lb=0)
Q_hi = m.addVars(hybrid, warehouse, vtype=GRB.INTEGER, lb=0)
Q_hi_bar = m.addVars(hybrid, warehouse, vtype=GRB.INTEGER, lb=0)
Q_ju = m.addVars(collect, disassembly, vtype=GRB.INTEGER, lb=0)
Q_kuw = m.addVars(component, disassembly, disposal, vtype=GRB.INTEGER, lb=0)
Q_kuv = m.addVars(component, disassembly, recycling, vtype=GRB.INTEGER, lb=0)
Q_uh = m.addVars(disassembly, hybrid, vtype=GRB.INTEGER, lb=0)
Q_ug = m.addVars(disassembly, remanu, vtype=GRB.INTEGER, lb=0)
Q_kvf = m.addVars(component, recycling, manu, vtype=GRB.INTEGER, lb=0)
Q_kvh = m.addVars(component, recycling, hybrid, vtype=GRB.INTEGER, lb=0)

# Set objective function
# Activation costs of all facilities: SUM C_f * X_f
EK = gp.quicksum(C_f[a] * X_f[a] for a in manu) + gp.quicksum(C_g[a] * X_g[a] for a in remanu) + gp.quicksum(C_h[a] * X_h[a] for a in hybrid) + gp.quicksum(C_j[a] * X_j[a] for a in collect) + gp.quicksum(C_u[a] * X_u[a] for a in disassembly) + gp.quicksum(C_v[a] * X_v[a] for a in recycling) + gp.quicksum(C_w[a] * X_w[a] for a in disposal)

# Production/processing cost of all facilities: SUM B_f * Q_f
PK = gp.quicksum(B_F * Q_fi[a, b] for a in manu for b in warehouse) + gp.quicksum(B_G * Q_gi[a, b] for a in remanu for b in warehouse) + gp.quicksum(B_H * Q_hi[a, b] for a in hybrid for b in warehouse) + gp.quicksum(B_H_bar * Q_hi_bar[a, b] for a in hybrid for b in warehouse) + gp.quicksum(B_J * Q_ju[a, b] for a in collect for b in disassembly) + gp.quicksum(B_KU * Q_kuw[a, b, c] for a in component for b in disassembly for c in disposal) + gp.quicksum(B_KU * Q_kuv[a, b, c] for a in component for b in disassembly for c in recycling) + gp.quicksum(B_U * Q_uh[a, b] for a in disassembly for b in hybrid) + gp.quicksum(B_U * Q_ug[a, b] for a in disassembly for b in remanu) + gp.quicksum(B_V * Q_kvf[a, b, c] for a in component for b in recycling for c in manu) + gp.quicksum(B_V * Q_kvh[a, b, c] for a in component for b in recycling for c in hybrid) + gp.quicksum(P_k[a] * Q_klf[a, b, c] for a in component for b in supplier for c in manu) + gp.quicksum(P_k[a] * Q_klh[a, b, c] for a in component for b in supplier for c in hybrid)

# Transportation cost of all products and components for all routes
TK = omega_k * (gp.quicksum(S_lf[b, c] * Q_klf[a, b, c] for a in component for b in supplier for c in manu) + gp.quicksum(S_lh[b, c] * Q_klh[a, b, c] for a in component for b in supplier for c in hybrid) + gp.quicksum(S_uw[b, c] * Q_kuw[a, b, c] for a in component for b in disassembly for c in disposal) + gp.quicksum(S_uv[b, c] * Q_kuv[a, b, c] for a in component for b in disassembly for c in recycling) + gp.quicksum(S_vf[b, c] * Q_kvf[a, b, c] for a in component for b in recycling for c in manu) + gp.quicksum(S_vh[b, c] * Q_kvh[a, b, c] for a in component for b in recycling for c in hybrid)) + omega_p * (gp.quicksum(S_fi[a, b] * Q_fi[a, b] for a in manu for b in warehouse) + gp.quicksum(S_gi[a, b] * Q_gi[a, b] for a in remanu for b in warehouse) + gp.quicksum(S_hi[a, b] * Q_hi[a, b] for a in hybrid for b in warehouse) + gp.quicksum(S_hi[a, b] * Q_hi_bar[a, b] for a in hybrid for b in warehouse) + gp.quicksum(S_ju[a, b] * Q_ju[a, b] for a in collect for b in disassembly) + gp.quicksum(S_uh[a, b] * Q_uh[a, b] for a in disassembly for b in hybrid) + gp.quicksum(S_ug[a, b] * Q_ug[a, b] for a in disassembly for b in remanu))

# Cost from CO2-offset
KK = pi * (gp.quicksum(Q_fi[a, b] * E_F for a in manu for b in warehouse) + gp.quicksum(Q_gi[a, b] * E_G for a in remanu for b in warehouse) + gp.quicksum((Q_hi[a, b] + Q_hi_bar[a, b]) * E_H for a in hybrid for b in warehouse) + gp.quicksum(Q_ju[a, b] * E_J for a in collect for b in disassembly) + gp.quicksum(Q_ug[a, b] * E_U for a in disassembly for b in remanu) + gp.quicksum(Q_uh[a, b] * E_U for a in disassembly for b in hybrid) + gp.quicksum(Q_kuw[a, b, c] * E_KU for a in component for b in disassembly for c in disposal) + gp.quicksum(Q_kuv[a, b, c] * E_KU for a in component for b in disassembly for c in recycling) + gp.quicksum(Q_kvf[a, b, c] * E_V for a in component for b in recycling for c in manu) + gp.quicksum(Q_kvh[a, b, c] * E_V for a in component for b in recycling for c in hybrid) + (gp.quicksum(Q_fi[a, b] * S_fi[a, b] for a in manu for b in warehouse) + gp.quicksum(Q_gi[a, b] * S_gi[a, b] for a in remanu for b in warehouse) + gp.quicksum((Q_hi[a, b] + Q_hi_bar[a, b]) * S_hi[a, b] for a in hybrid for b in warehouse) + gp.quicksum(Q_ju[a, b] * S_ju[a, b] for a in collect for b in disassembly)) * E_P + (gp.quicksum(Q_klf[a, b, c] * S_lf[b, c] for a in component for b in supplier for c in manu) + gp.quicksum(Q_klh[a, b, c] * S_lh[b, c] for a in component for b in supplier for c in hybrid) + gp.quicksum(Q_kuw[a, b, c] * S_uw[b, c] for a in component for b in disassembly for c in disposal) + gp.quicksum(Q_kuv[a, b, c] * S_uv[b, c] for a in component for b in disassembly for c in recycling) + gp.quicksum(Q_kvf[a, b, c] * S_vf[b, c] for a in component for b in recycling for c in manu) + gp.quicksum(Q_kvh[a, b, c] * S_vh[b, c] for a in component for b in recycling for c in hybrid)) * E_K)

# Define the objective function
m.setObjective(EK + PK + TK + KK, GRB.MINIMIZE)

# Add constraints
# (1)
m.addConstrs(gp.quicksum(Q_fi[a, b] for b in warehouse) <= CAP_f[a] * X_f[a] for a in manu)

# (2)
m.addConstrs(gp.quicksum(Q_gi[a, b] for b in warehouse) <= CAP_g[a] * X_g[a] for a in remanu)

# (3)
m.addConstrs(gp.quicksum(Q_hi[a, b] for b in warehouse) <= CAP_h[a] * X_h[a] for a in hybrid)

# (4)
m.addConstrs(gp.quicksum(Q_hi_bar[a, b] for b in warehouse) <= CAP_h_bar[a] * X_h[a] for a in hybrid)

# (5)
m.addConstrs(gp.quicksum(Q_ju[a, b] for b in disassembly) <= CAP_j[a] * X_j[a] for a in collect)

# (6)
m.addConstrs(gp.quicksum(Q_ug[a, b] for b in remanu) + gp.quicksum(Q_uh[a, b] for b in hybrid) <= CAP_u[a] * X_u[a] for a in disassembly)

# (7)
m.addConstrs(gp.quicksum(Q_kuv[a, b, c] for a in component for c in recycling) + gp.quicksum(Q_kuw[a, b, c] for a in component for c in disposal) <= CAP_Ku[b] * X_u[b] for b in disassembly)

# (8)
m.addConstrs(gp.quicksum(Q_kvf[a, b, c] for a in component for c in manu) + gp.quicksum(Q_kvh[a, b, c] for a in component for c in hybrid) <= CAP_Kv[b] * X_v[b] for b in recycling)

# (9)
m.addConstrs(gp.quicksum(Q_kuw[a, b, c] for a in component for b in disassembly) <= CAP_Kw[c] * X_w[c] for c in disposal)

# # (10)
m.addConstrs(gp.quicksum(Q_fi[a, b] for a in manu) + gp.quicksum(Q_hi[a, b] for a in hybrid) + gp.quicksum(Q_gi[a, b] for a in remanu) + gp.quicksum(Q_hi_bar[a, b] for a in hybrid) == D_i[b] for b in warehouse)

# # (11)
m.addConstrs(gp.quicksum(Q_klf[a, b, c] for b in supplier) + gp.quicksum(Q_kvf[a, b, c] for b in recycling)  == gp.quicksum(Q_fi[c, b] for b in warehouse) * R_k[a] for a in component for c in manu)

# # (12) PENDING REVIEW
m.addConstrs(gp.quicksum(Q_ug[a, b] for a in disassembly) == gp.quicksum(Q_gi[b, c] for c in warehouse) for b in remanu)

# # (13) PENDING REVIEW
m.addConstrs(gp.quicksum(Q_klh[a, b, c] for b in supplier) + gp.quicksum(Q_kvh[a, b, c] for b in recycling) == gp.quicksum(Q_hi[c, b] for b in warehouse) * R_k[a] for a in component for c in hybrid)

# # (14) PENDING REVIEW
m.addConstrs(gp.quicksum(Q_uh[u, h] for u in disassembly) == gp.quicksum(Q_hi_bar[h, i] for i in warehouse) for h in hybrid)

# (15)
m.addConstrs(gp.quicksum(Q_ju[j, u] for u in disassembly) <= M_j[j] for j in collect)

# # (16)
m.addConstrs((gp.quicksum(Q_ju[j, u] for j in collect) * alpha >= gp.quicksum(Q_ug[u,g] for g in remanu) + gp.quicksum(Q_uh[u,h] for h in hybrid)) for u in disassembly)

# # (17)
m.addConstrs(gp.quicksum(Q_ju[j, u] for j in collect) * beta * R_k[k] >= gp.quicksum(Q_kuv[k,u,v] for v in recycling) for u in disassembly for k in component)

# # (18)
m.addConstrs(gp.quicksum(Q_ju[j, u] for j in collect) * gamma * R_k[k] >= gp.quicksum(Q_kuv[k,u,v] for v in recycling) for u in disassembly for k in component)

# # (19)
m.addConstrs(gp.quicksum(Q_kuv[a, m, r] for m in disassembly) == gp.quicksum(Q_kvf[a, r, c] for c in manu) + gp.quicksum(Q_kvh[a, r, c] for c in hybrid) for a in component for r in recycling)

# (20)
m.addConstr(gp.quicksum(Q_fi[a, b] * E_F for a in manu for b in warehouse) + gp.quicksum(Q_gi[a, b] * E_G for a in remanu for b in warehouse) + gp.quicksum((Q_hi[a, b] + Q_hi_bar[a, b]) * E_H for a in hybrid for b in warehouse) + gp.quicksum(Q_ju[a, b] * E_J for a in collect for b in disassembly) + gp.quicksum(Q_ug[a, b] * E_U for a in disassembly for b in remanu) + gp.quicksum(Q_uh[a, b] * E_U for a in disassembly for b in hybrid) + gp.quicksum(Q_kuw[a, b, c] * E_KU for a in component for b in disassembly for c in disposal) + gp.quicksum(Q_kuv[a, b, c] * E_KU for a in component for b in disassembly for c in recycling) + gp.quicksum(Q_kvf[a, b, c] * E_V for a in component for b in recycling for c in manu) + gp.quicksum(Q_kvh[a, b, c] * E_V for a in component for b in recycling for c in hybrid) + (gp.quicksum(Q_fi[a, b] * S_fi[a, b] for a in manu for b in warehouse) + gp.quicksum(Q_gi[a, b] * S_gi[a, b] for a in remanu for b in warehouse) + gp.quicksum((Q_hi[a, b] + Q_hi_bar[a, b]) * S_hi[a, b] for a in hybrid for b in warehouse) + gp.quicksum(Q_ju[a, b] * S_ju[a, b] for a in collect for b in disassembly)) * E_P + (gp.quicksum(Q_klf[a, b, c] * S_lf[b, c] for a in component for b in supplier for c in manu) + gp.quicksum(Q_klh[a, b, c] * S_lh[b, c] for a in component for b in supplier for c in hybrid) + gp.quicksum(Q_kuw[a, b, c] * S_uw[b, c] for a in component for b in disassembly for c in disposal) + gp.quicksum(Q_kuv[a, b, c] * S_uv[b, c] for a in component for b in disassembly for c in recycling) + gp.quicksum(Q_kvf[a, b, c] * S_vf[b, c] for a in component for b in recycling for c in manu) + gp.quicksum(Q_kvh[a, b, c] * S_vh[b, c] for a in component for b in recycling for c in hybrid)) * E_K <= CAP_CO2)


m.optimize()

# Print out results
if m.Status == GRB.OPTIMAL:
    total_cost = m.ObjVal
    f_to_i = m.getAttr('X', Q_fi)
    h_to_i = m.getAttr('X', Q_hi)
    h_bar_to_i = m.getAttr('X', Q_hi_bar)
    g_to_i = m.getAttr('X', Q_gi)
#    print(total_cost)
#    print(f_to_i)
#    print(h_to_i)
#    print(h_bar_to_i)
#    print(g_to_i)
#    print(D_i)
#    print(D_i_bar)
#    print(M_j)
    jtou = m.getAttr('X', Q_ju)
    utog = m.getAttr('X', Q_ug)
    utoh = m.getAttr('X', Q_uh)
    kutow = m.getAttr('X', Q_kuw)
    kutov = m.getAttr('X', Q_kuv)

    print("F to I: ")
    for f in manu:
        for i in warehouse:
            if f_to_i[f,i] > 0:
                print('%s -> %s: %g' % (f, i, f_to_i[f,i]))
    
    print("H to I: ")
    for h in hybrid:
        for i in warehouse:
            if h_to_i[h,i] > 0:
                print('%s -> %s: %g' % (h, i, h_to_i[h,i]))

    print("G to I: ")
    for g in remanu:
        for i in warehouse:
            if g_to_i[g,i] > 0:
                print('%s -> %s: %g' % (g, i, g_to_i[g,i]))
    
    print("H to I (remanu): ")
    for h in hybrid:
        for i in warehouse:
            if h_bar_to_i[h,i] > 0:
                print('%s -> %s: %g' % (h, i, h_bar_to_i[h,i]))

    print("Returned products at each collection center: ")
    print(M_j)
    print("Collection center to disassembly center: ")
    for j in collect:
        for u in disassembly:
            if jtou[j, u] > 0:
                print('%s -> %s: %g' % (j, u, jtou[j, u]))

    print("Disassembly center to remanufacturing facility: ")
    for u in disassembly:
        for g in remanu:
            if utog[u,g] > 0:
                print('%s -> %s: %g' % (u, g, utog[u, g]))

    print("Disassembly center to hybrid facility: ")
    for u in disassembly:
        for h in hybrid:
            if utoh[u,h] > 0:
                print('%s -> %s: %g' % (u, h, utoh[u, h]))

    print("Components from U to V")
    for k in component:
        for u in disassembly:
            for v in recycling:
                if kutov[k, u, v] > 0:
                    print('%s -> %s: %g' % (u, v, kutov[k, u, v]))

    print("Components from U to W")
    for k in component:
        for u in disassembly:
            for w in disposal:
                if kutow[k, u, w] > 0:
                    print('%s -> %s: %g' % (u, w, kutow[k, u, w]))
    
    print(total_cost)
    print("EK:")
    print(EK.getValue())
    print("PK:")
    print(PK.getValue())
    print("TK:")
    print(TK.getValue())
    print("KK:")
    print(KK.getValue())
    print("Emission in Ton:")
    print(KK.getValue() / pi)
    print("Optimality gap: ")
    print(m.MIPGap)

    test after branches