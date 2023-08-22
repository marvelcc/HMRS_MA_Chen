import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import random

# Initialize the sets and parameters of the model
# Sets of the model
T = 12
period = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
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

activation = pd.read_csv('activation_cost.csv', header=None)
demand = pd.read_csv('demand.csv')
distance = pd.read_csv('distance_matrix.csv', index_col=0)
processing = pd.read_csv('processing_cost.csv', index_col=0)
procurement = pd.read_csv('procurement_price.csv', index_col=0)
returns = pd.read_csv('returns.csv')
capacity = pd.read_csv('production_capacity.csv', index_col=0)
capacity_bar = pd.read_csv('production_capacity_bar.csv', index_col=0)
capacity_k = pd.read_csv('production_capacity_k.csv', index_col=0)
ratio = pd.read_csv('ratio.csv', index_col=0)

# Read activation costs from activation_cost.csv
for i in activation.columns:
	for f in manu:
		C_f = {row[0]: row[1] for index, row in activation.iterrows() if row[0] in manu}
	for g in remanu:
		C_g = {row[0]: row[1] for index, row in activation.iterrows() if row[0] in remanu}
	for h in hybrid:
		C_h = {row[0]: row[1] for index, row in activation.iterrows() if row[0] in hybrid}
	for j in collect:
		C_j = {row[0]: row[1] for index, row in activation.iterrows() if row[0] in collect}
	for u in disassembly:
		C_u = {row[0]: row[1] for index, row in activation.iterrows() if row[0] in disassembly}
	for v in recycling:
		C_v = {row[0]: row[1] for index, row in activation.iterrows() if row[0] in recycling}
	for w in disposal:
		C_w = {row[0]: row[1] for index, row in activation.iterrows() if row[0] in disposal}

# Read distance between facilities from distance matrix
S_lf = {(l, f): distance.loc[l, f] for l in supplier for f in manu}
S_lh = {(l, h): distance.loc[l, h] for l in supplier for h in hybrid}
S_fi = {(f, i): distance.loc[f, i] for f in manu for i in warehouse}
S_gi = {(g, i): distance.loc[g, i] for g in remanu for i in warehouse}
S_hi = {(h, i): distance.loc[h, i] for h in hybrid for i in warehouse}
S_ju = {(j, u): distance.loc[j, u] for j in collect for u in disassembly}
S_uw = {(u, w): distance.loc[u, w] for u in disassembly for w in disposal}
S_uv = {(u, v): distance.loc[u, v] for u in disassembly for v in recycling}
S_uh = {(u, h): distance.loc[u, h] for u in disassembly for h in hybrid}
S_ug = {(u, g): distance.loc[u, g] for u in disassembly for g in remanu}
S_vf = {(v, f): distance.loc[v, f] for v in recycling for f in manu}
S_vh = {(v, h): distance.loc[v, h] for v in recycling for h in hybrid}

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

# Emission capacity in kg
CAP_CO2 = 40000000

# Cost in euro
pi = 1.5 # per kg 
omega_p = 0.03 # per km
omega_k = 0.012 # per km

# Amount of component component in a product
R_k = {'k1': 2, 'k2': 3, 'k3': 4}

# ==========================================


B_F = processing['B_F'].tolist()
B_G = processing['B_G'].tolist()
B_H = processing['B_H'].tolist()
B_H_bar = processing['B_H_bar'].tolist()
B_J = processing['B_J'].tolist()
B_KU = processing['B_KU'].tolist()
B_U = processing['B_U'].tolist()
B_V = processing['B_V'].tolist()
B_W = processing['B_W'].tolist()


# Read procurement cost in period t
P_k = {}
for t, row in procurement.iterrows():
	for k in procurement.columns:
		value = procurement.loc[t, k]
		P_k[(t, k)] = value
	
# Read demand at each distribution center in period t
D_i = {}
for t, row in demand.iterrows():
	for i in demand.columns:
		value = demand.loc[t, i]
		D_i[(t, i)] = value
	
# Read number of returned product at each collection center in period t
M_j = {}
for t, row in returns.iterrows():
	for j in returns.columns:
		value = returns.loc[t, j]
		M_j[(t, j)] = value

# Read the production capacity of each facility in period t
CAP_f = {}
CAP_g = {}
CAP_h = {}
CAP_j = {}
CAP_u = {}
CAP_h_bar = {}
CAP_Ku = {}
CAP_Kv = {}
CAP_Kw = {}
for t, row in capacity.iterrows():
	for f in capacity.columns:
		value = capacity.loc[t, f]
		CAP_f[(t, f)] = value
	for g in capacity.columns:
		value = capacity.loc[t, g]
		CAP_g[(t, g)] = value
	for h in capacity.columns:
		value = capacity.loc[t, h]
		CAP_h[(t, h)] = value
	for j in capacity.columns:
		value = capacity.loc[t, j]
		CAP_j[(t, j)] = value
	for u in capacity.columns:
		value = capacity.loc[t, u]
		CAP_u[(t, u)] = value
for t, row in capacity_bar.iterrows():
	for h in capacity_bar.columns:
		value = capacity_bar.loc[t, h]
		CAP_h_bar[(t, h)] = value
for t, row in capacity_k.iterrows():
	for u in capacity_k.columns:
			value = capacity_k.loc[t, u]
			CAP_Ku[(t, u)] = value
	for v in capacity_k.columns:
		value = capacity_k.loc[t, v]
		CAP_Kv[(t, v)] = value
	for w in capacity_k.columns:
		value = capacity_k.loc[t, w]
		CAP_Kw[(t, w)] = value


# Read the ratio between EoU (a), EoL (b) and disposal (c) products in period t
alpha = ratio['a'].tolist()
beta = ratio['b'].tolist()
gamma = ratio['c'].tolist()

m = gp.Model('HMRS')
# Add decision variables
# Binary decision variables
X_f = m.addVars(manu, period, vtype=GRB.BINARY, name="X_f")
X_g = m.addVars(remanu, period, vtype=GRB.BINARY, name="X_g")
X_h = m.addVars(hybrid, period, vtype=GRB.BINARY, name="X_h")
X_j = m.addVars(collect, period, vtype=GRB.BINARY, name="X_j")
X_u = m.addVars(disassembly, period, vtype=GRB.BINARY, name="X_u")
X_v = m.addVars(recycling, period, vtype=GRB.BINARY, name="X_v")
X_w = m.addVars(disposal, period, vtype=GRB.BINARY, name="X_w")

# Quantity of flow between facilities
Q_klf = m.addVars(component, supplier, manu, period, vtype=GRB.INTEGER, lb=0, name="Q_klf")
Q_klh = m.addVars(component, supplier, hybrid, period, vtype=GRB.INTEGER, lb=0, name="Q_klh")
Q_fi = m.addVars(manu, warehouse, period, vtype=GRB.INTEGER, lb=0, name="Q_fi")
Q_gi = m.addVars(remanu, warehouse, period, vtype=GRB.INTEGER, lb=0, name="Q_gi")
Q_hi = m.addVars(hybrid, warehouse, period, vtype=GRB.INTEGER, lb=0, name="Q_hi")
Q_hi_bar = m.addVars(hybrid, warehouse, period, vtype=GRB.INTEGER, lb=0, name="Q_hi_bar")
Q_ju = m.addVars(collect, disassembly, period, vtype=GRB.INTEGER, lb=0, name="Q_ju")
Q_kuw = m.addVars(component, disassembly, disposal, period, vtype=GRB.INTEGER, lb=0, name="Q_kuw")
Q_kuv = m.addVars(component, disassembly, recycling, period, vtype=GRB.INTEGER, lb=0, name="Q_kuv")
Q_uh = m.addVars(disassembly, hybrid, period, vtype=GRB.INTEGER, lb=0, name="Q_uh")
Q_ug = m.addVars(disassembly, remanu, period, vtype=GRB.INTEGER, lb=0, name="Q_ug")
Q_kvf = m.addVars(component, recycling, manu, period, vtype=GRB.INTEGER, lb=0, name="Q_kvf")
Q_kvh = m.addVars(component, recycling, hybrid, period, vtype=GRB.INTEGER, lb=0, name="Q_kvh")

# Set objective function
# Activation costs of all facilities: SUM C_f * X_f
# Only at the beginning. No changes after.
EK = gp.quicksum(C_f[f] * X_f[f, t] for f in manu for t in period) + gp.quicksum(C_g[g] * X_g[g, t] for g in remanu for t in period) + gp.quicksum(C_h[h] * X_h[h, t] for h in hybrid for t in period) + gp.quicksum(C_j[a] * X_j[a, t] for a in collect for t in period) + gp.quicksum(C_u[a] * X_u[a, t] for a in disassembly for t in period) + gp.quicksum(C_v[a] * X_v[a, t] for a in recycling for t in period) + gp.quicksum(C_w[a] * X_w[a, t] for a in disposal for t in period)

# Production/processing cost of all facilities: SUM B_f * Q_f
PK = gp.quicksum(B_F[t] * Q_fi[f, i, t] for f in manu for i in warehouse for t in period) + gp.quicksum(B_G[t] * Q_gi[g, i, t] for g in remanu for i in warehouse for t in period) + gp.quicksum(B_H[t] * Q_hi[h, i, t] for h in hybrid for i in warehouse for t in period) + gp.quicksum(B_H_bar[t] * Q_hi_bar[h, i, t] for h in hybrid for i in warehouse) + gp.quicksum(B_J[t] * Q_ju[j, u, t] for j in collect for u in disassembly for t in period) + gp.quicksum(B_KU[t] * Q_kuw[k, u, w, t] for k in component for u in disassembly for w in disposal for t in period) + gp.quicksum(B_KU[t] * Q_kuv[k, u, v, t] for k in component for u in disassembly for v in recycling for t in period) + gp.quicksum(B_U[t] * Q_uh[u, h, t] for u in disassembly for h in hybrid for t in period) + gp.quicksum(B_U[t] * Q_ug[u, g, t] for u in disassembly for g in remanu for t in period) + gp.quicksum(B_V[t] * Q_kvf[k, v, f, t] for k in component for v in recycling for f in manu for t in period) + gp.quicksum(B_V[t] * Q_kvh[k, v, h, t] for k in component for v in recycling for h in hybrid for t in period) + gp.quicksum(P_k[t, k] * Q_klf[k, l, f, t] for k in component for l in supplier for f in manu for t in period) + gp.quicksum(P_k[t, k] * Q_klh[k, l, h, t] for ak in component for l in supplier for h in hybrid for t in period)

# Transportation cost of all products and components for all routes
TK = omega_k * (gp.quicksum(S_lf[l, f] * Q_klf[k, l, f, t] for k in component for l in supplier for f in manu for t in period) + gp.quicksum(S_lh[l, h] * Q_klh[k, l, h, t] for k in component for l in supplier for h in hybrid for t in period) + gp.quicksum(S_uw[u, w] * Q_kuw[k, u, w, t] for k in component for u in disassembly for w in disposal for t in period) + gp.quicksum(S_uv[u, v] * Q_kuv[k, u, v, t] for k in component for u in disassembly for v in recycling for t in period) + gp.quicksum(S_vf[v, f] * Q_kvf[k, v, f, t] for k in component for v in recycling for f in manu for t in period) + gp.quicksum(S_vh[v, h] * Q_kvh[k, v, h, t] for k in component for v in recycling for h in hybrid for t in period)) + omega_p * (gp.quicksum(S_fi[f, i] * Q_fi[f, i, t] for f in manu for i in warehouse for t in period) + gp.quicksum(S_gi[g, i] * Q_gi[g, i, t] for g in remanu for i in warehouse for t in period) + gp.quicksum(S_hi[h, i] * Q_hi[h, i, t] for h in hybrid for i in warehouse for t in period) + gp.quicksum(S_hi[h, i] * Q_hi_bar[h, i, t] for h in hybrid for i in warehouse for t in period) + gp.quicksum(S_ju[j, u] * Q_ju[j, u, t] for j in collect for u in disassembly for t in period) + gp.quicksum(S_uh[u, h] * Q_uh[u, h, t] for u in disassembly for h in hybrid for t in period) + gp.quicksum(S_ug[u, g] * Q_ug[u, g, t] for u in disassembly for g in remanu for t in period))

# Cost from CO2-offset
KK = pi * (gp.quicksum(Q_fi[a, b, t] * E_F for a in manu for b in warehouse for t in period) + gp.quicksum(Q_gi[a, b, t] * E_G for a in remanu for b in warehouse for t in period) + gp.quicksum((Q_hi[a, b, t] + Q_hi_bar[a, b, t]) * E_H for a in hybrid for b in warehouse for t in period) + gp.quicksum(Q_ju[a, b, t] * E_J for a in collect for b in disassembly for t in period) + gp.quicksum(Q_ug[a, b, t] * E_U for a in disassembly for b in remanu for t in period) + gp.quicksum(Q_uh[a, b, t] * E_U for a in disassembly for b in hybrid for t in period) + gp.quicksum(Q_kuw[a, b, c, t] * E_KU for a in component for b in disassembly for c in disposal for t in period) + gp.quicksum(Q_kuv[a, b, c, t] * E_KU for a in component for b in disassembly for c in recycling for t in period) + gp.quicksum(Q_kvf[a, b, c, t] * E_V for a in component for b in recycling for c in manu for t in period) + gp.quicksum(Q_kvh[a, b, c, t] * E_V for a in component for b in recycling for c in hybrid for t in period) + (gp.quicksum(Q_fi[a, b, t] * S_fi[a, b] for a in manu for b in warehouse for t in period) + gp.quicksum(Q_gi[a, b, t] * S_gi[a, b] for a in remanu for b in warehouse for t in period) + gp.quicksum((Q_hi[a, b, t] + Q_hi_bar[a, b, t]) * S_hi[a, b] for a in hybrid for b in warehouse for t in period) + gp.quicksum(Q_ju[a, b, t] * S_ju[a, b] for a in collect for b in disassembly for t in period)) * E_P + (gp.quicksum(Q_klf[a, b, c, t] * S_lf[b, c] for a in component for b in supplier for c in manu for t in period) + gp.quicksum(Q_klh[a, b, c, t] * S_lh[b, c] for a in component for b in supplier for c in hybrid for t in period) + gp.quicksum(Q_kuw[a, b, c, t] * S_uw[b, c] for a in component for b in disassembly for c in disposal for t in period) + gp.quicksum(Q_kuv[a, b, c, t] * S_uv[b, c] for a in component for b in disassembly for c in recycling for t in period) + gp.quicksum(Q_kvf[a, b, c, t] * S_vf[b, c] for a in component for b in recycling for c in manu for t in period) + gp.quicksum(Q_kvh[a, b, c, t] * S_vh[b, c] for a in component for b in recycling for c in hybrid for t in period)) * E_K)

# Define the objective function
m.setObjective(EK + PK + TK + KK, GRB.MINIMIZE)

# Add constraints
# (1)
m.addConstrs((gp.quicksum(Q_fi[a, b, t] for b in warehouse) <= CAP_f[t, a] * X_f[a, t] for a in manu for t in period), name='c1')

# (2)
m.addConstrs((gp.quicksum(Q_gi[a, b, t] for b in warehouse) <= CAP_g[t, a] * X_g[a, t] for a in remanu for t in period), name='c2')

# (3)
m.addConstrs((gp.quicksum(Q_hi[a, b, t] for b in warehouse) <= CAP_h[t, a] * X_h[a, t] for a in hybrid for t in period), name='c3')

# (4)
m.addConstrs((gp.quicksum(Q_hi_bar[a, b, t] for b in warehouse) <= CAP_h_bar[t, a] * X_h[a, t] for a in hybrid for t in period), name='c4')

# (5)
m.addConstrs((gp.quicksum(Q_ju[a, b, t] for b in disassembly) <= CAP_j[t, a] * X_j[a, t] for a in collect for t in period), name='c5')

# (6)
m.addConstrs((gp.quicksum(Q_ug[a, b, t] for b in remanu) + gp.quicksum(Q_uh[a, b, t] for b in hybrid) <= CAP_u[t, a] * X_u[a, t] for a in disassembly for t in period), name='c6')

# (7)
m.addConstrs((gp.quicksum(Q_kuv[a, b, c, t] for a in component for c in recycling) + gp.quicksum(Q_kuw[a, b, c, t] for a in component for c in disposal) <= CAP_Ku[t, b] * X_u[b, t] for b in disassembly for t in period), name='c7')

# (8)
m.addConstrs((gp.quicksum(Q_kvf[a, b, c, t] for a in component for c in manu) + gp.quicksum(Q_kvh[a, b, c, t] for a in component for c in hybrid) <= CAP_Kv[t, b] * X_v[b, t] for b in recycling for t in period), name='c8')

# (9)
m.addConstrs((gp.quicksum(Q_kuw[a, b, c, t] for a in component for b in disassembly) <= CAP_Kw[t, c] * X_w[c, t] for c in disposal for t in period), name='c9')

# # (10)
m.addConstrs(((gp.quicksum(Q_fi[a, b, t] for a in manu) + gp.quicksum(Q_hi[a, b, t] for a in hybrid) + gp.quicksum(Q_gi[a, b ,t] for a in remanu) + gp.quicksum(Q_hi_bar[a, b ,t] for a in hybrid) == D_i[t, b]) for b in warehouse for t in period), name='c10')

# # (11)
m.addConstrs((gp.quicksum(Q_klf[a, b, c, t] for b in supplier) + gp.quicksum(Q_kvf[a, b, c, t] for b in recycling)  == gp.quicksum(Q_fi[c, b, t] for b in warehouse) * R_k[a] for a in component for c in manu for t in period), name='c11')

# # (12) PENDING REVIEW
m.addConstrs((gp.quicksum(Q_ug[a, b, t] for a in disassembly) == gp.quicksum(Q_gi[b, c, t] for c in warehouse) for b in remanu for t in period), name='c12')

# # (13) PENDING REVIEW
m.addConstrs((gp.quicksum(Q_klh[a, b, c, t] for b in supplier) + gp.quicksum(Q_kvh[a, b, c, t] for b in recycling) == gp.quicksum(Q_hi[c, b, t] for b in warehouse) * R_k[a] for a in component for c in hybrid for t in period), name='c13')

# # (14) PENDING REVIEW
m.addConstrs((gp.quicksum(Q_uh[u, h, t] for u in disassembly) == gp.quicksum(Q_hi_bar[h, i, t] for i in warehouse) for h in hybrid for t in period), name='c14')

# (15)
m.addConstrs((gp.quicksum(Q_ju[j, u, t] for u in disassembly) >= M_j[t, j] for j in collect for t in period), name='c15')

# # (16)
m.addConstrs(((gp.quicksum(Q_ju[j, u, t] for j in collect) * alpha[t] >= gp.quicksum(Q_ug[u, g, t] for g in remanu) + gp.quicksum(Q_uh[u,h,t] for h in hybrid)) for u in disassembly for t in period), name='c16')

# # (17)
m.addConstrs((gp.quicksum(Q_ju[j, u, t] for j in collect) * beta[t] * R_k[k] >= gp.quicksum(Q_kuv[k,u,v,t] for v in recycling) for u in disassembly for k in component for t in period), name='c17')

# # (18)
m.addConstrs((gp.quicksum(Q_ju[j, u, t] for j in collect) * gamma[t] * R_k[k] >= gp.quicksum(Q_kuv[k,u,v,t] for v in recycling) for u in disassembly for k in component for t in period), name='c18')

# # (19)
m.addConstrs((gp.quicksum(Q_kuv[a, m, r, t] for m in disassembly) == gp.quicksum(Q_kvf[a, r, c, t] for c in manu) + gp.quicksum(Q_kvh[a, r, c, t] for c in hybrid) for a in component for r in recycling for t in period), name='c19')

# (20)
# m.addConstr((gp.quicksum(Q_fi[a, b, t] * E_F for a in manu for b in warehouse) + gp.quicksum(Q_gi[a, b, t] * E_G for a in remanu for b in warehouse) + gp.quicksum((Q_hi[a, b, t] + Q_hi_bar[a, b, t]) * E_H for a in hybrid for b in warehouse) + gp.quicksum(Q_ju[a, b, t] * E_J for a in collect for b in disassembly) + gp.quicksum(Q_ug[a, b, t] * E_U for a in disassembly for b in remanu) + gp.quicksum(Q_uh[a, b, t] * E_U for a in disassembly for b in hybrid) + gp.quicksum(Q_kuw[a, b, c, t] * E_KU for a in component for b in disassembly for c in disposal) + gp.quicksum(Q_kuv[a, b, c, t] * E_KU for a in component for b in disassembly for c in recycling) + gp.quicksum(Q_kvf[a, b, c, t] * E_V for a in component for b in recycling for c in manu) + gp.quicksum(Q_kvh[a, b, c, t] * E_V for a in component for b in recycling for c in hybrid) + (gp.quicksum(Q_fi[a, b, t] * S_fi[a, b] for a in manu for b in warehouse) + gp.quicksum(Q_gi[a, b, t] * S_gi[a, b] for a in remanu for b in warehouse) + gp.quicksum((Q_hi[a, b, t] + Q_hi_bar[a, b, t]) * S_hi[a, b] for a in hybrid for b in warehouse) + gp.quicksum(Q_ju[a, b, t] * S_ju[a, b] for a in collect for b in disassembly)) * E_P + (gp.quicksum(Q_klf[a, b, c, t] * S_lf[b, c] for a in component for b in supplier for c in manu) + gp.quicksum(Q_klh[a, b, c, t] * S_lh[b, c] for a in component for b in supplier for c in hybrid) + gp.quicksum(Q_kuw[a, b, c, t] * S_uw[b, c] for a in component for b in disassembly for c in disposal) + gp.quicksum(Q_kuv[a, b, c, t] * S_uv[b, c] for a in component for b in disassembly for c in recycling) + gp.quicksum(Q_kvf[a, b, c, t] * S_vf[b, c] for a in component for b in recycling for c in manu) + gp.quicksum(Q_kvh[a, b, c, t] * S_vh[b, c] for a in component for b in recycling for c in hybrid)) * E_K <= CAP_CO2 for t in period), name='c20')

# Activation constraint

for t in period:
	for f in manu:
		m.addConstrs(((X_f[f, 0] == 0) >> (X_f[f, i+1] == 0) for i in range(0, 11)))
		m.addConstrs(((X_f[f, 0] == 1) >> (X_f[f, i+1] == 1) for i in range(0, 11)))
	for g in remanu:
		m.addConstrs(((X_g[g, 0] == 0) >> (X_g[g, i+1] == 0) for i in range(0, 11)))
		m.addConstrs(((X_g[g, 0] == 1) >> (X_g[g, i+1] == 1) for i in range(0, 11)))
	for h in hybrid:
		m.addConstrs(((X_h[h, 0] == 0) >> (X_h[h, i+1] == 0) for i in range(0, 11)))
		m.addConstrs(((X_h[h, 0] == 1) >> (X_h[h, i+1] == 1) for i in range(0, 11)))
	for j in collect:
		m.addConstrs(((X_j[j, 0] == 0) >> (X_j[j, i+1] == 0) for i in range(0, 11)))
		m.addConstrs(((X_j[j, 0] == 1) >> (X_j[j, i+1] == 1) for i in range(0, 11)))
	for u in disassembly:
		m.addConstrs(((X_u[u, 0] == 0) >> (X_u[u, i+1] == 0) for i in range(0, 11)))
		m.addConstrs(((X_u[u, 0] == 1) >> (X_u[u, i+1] == 1) for i in range(0, 11)))
	for v in recycling:
		m.addConstrs(((X_v[v, 0] == 0) >> (X_v[v, i+1] == 0) for i in range(0, 11)))
		m.addConstrs(((X_v[v, 0] == 1) >> (X_v[v, i+1] == 1) for i in range(0, 11)))
	for w in disposal:
		m.addConstrs(((X_w[w, 0] == 0) >> (X_w[w, i+1] == 0) for i in range(0, 11)))
		m.addConstrs(((X_w[w, 0] == 1) >> (X_w[w, i+1] == 1) for i in range(0, 11)))

m.optimize()

# m.write("HMRS.lp")
# m.write("HMRS.mps")

# Print out results
if m.Status == GRB.OPTIMAL:
	total_cost = m.ObjVal
	
	xf = m.getAttr('X', X_f)
	xg = m.getAttr('X', X_g)
	xh = m.getAttr('X', X_h)

	fi = m.getAttr('X', Q_fi)
	hi = m.getAttr('X', Q_hi)
	gi = m.getAttr('X', Q_gi)
	hi_bar = m.getAttr('X', Q_hi_bar)

	df_xf = pd.DataFrame(xf.values(), index=pd.MultiIndex.from_tuples(xf.keys()))
	xf_unstacked = df_xf.unstack(level=0)
	df_fi = pd.DataFrame(fi.values(), index=pd.MultiIndex.from_tuples(fi.keys()))
	fi_unstacked = df_fi.unstack(level=0)
	df_xg = pd.DataFrame(xg.values(), index=pd.MultiIndex.from_tuples(xg.keys()))
	xg_unstacked = df_xg.unstack(level=0)
	df_gi = pd.DataFrame(gi.values(), index=pd.MultiIndex.from_tuples(gi.keys()))
	gi_unstacked = df_gi.unstack(level=0)
	df_xh = pd.DataFrame(xh.values(), index=pd.MultiIndex.from_tuples(xh.keys()))
	xh_unstacked = df_xh.unstack(level=0)
	df_hi = pd.DataFrame(hi.values(), index=pd.MultiIndex.from_tuples(hi.keys()))
	hi_unstacked = df_hi.unstack(level=0)
	df_hi_bar = pd.DataFrame(hi_bar.values(), index=pd.MultiIndex.from_tuples(hi_bar.keys()))
	hi_bar_unstacked = df_hi_bar.unstack(level=0)

	facility_opening = pd.concat([xf_unstacked, xg_unstacked, xh_unstacked], axis=1)

	print(facility_opening)
	
	



# # Print out results
# if m.Status == GRB.OPTIMAL:
# 	total_cost = m.ObjVal
# 	f_to_i = m.getAttr('X', Q_fi)
# 	h_to_i = m.getAttr('X', Q_hi)
# 	h_bar_to_i = m.getAttr('X', Q_hi_bar)
# 	g_to_i = m.getAttr('X', Q_gi)
# #    print(total_cost)
# #    print(f_to_i)
# #    print(h_to_i)
# #    print(h_bar_to_i)
# #    print(g_to_i)
# #    print(D_i)
# #    print(D_i_bar)
# #    print(M_j)
# 	jtou = m.getAttr('X', Q_ju)
# 	utog = m.getAttr('X', Q_ug)
# 	utoh = m.getAttr('X', Q_uh)
# 	kutow = m.getAttr('X', Q_kuw)
# 	kutov = m.getAttr('X', Q_kuv)
# 	print()
# 	print()
# 	print()
# 	print()
# 	xf = m.getAttr('X', X_f)
# 	print(xf)
# 	print(init_value.X)
# 	# for f in manu:
# 	# 	for i in warehouse:
# 	# 		if f_to_i[f,i] > 0:
# 	# 			print('%s -> %s: %g' % (f, i, f_to_i[f,i]))
	
# 	# print("H to I: ")
# 	# for h in hybrid:
# 	# 	for i in warehouse:
# 	# 		if h_to_i[h,i] > 0:
# 	# 			print('%s -> %s: %g' % (h, i, h_to_i[h,i]))

# 	# print("G to I: ")
# 	# for g in remanu:
# 	# 	for i in warehouse:
# 	# 		if g_to_i[g,i] > 0:
# 	# 			print('%s -> %s: %g' % (g, i, g_to_i[g,i]))
	
# 	# print("H to I (remanu): ")
# 	# for h in hybrid:
# 	# 	for i in warehouse:
# 	# 		if h_bar_to_i[h,i] > 0:
# 	# 			print('%s -> %s: %g' % (h, i, h_bar_to_i[h,i]))

# 	# print("Returned products at each collection center: ")
# 	# print(M_j)
# 	# print("Collection center to disassembly center: ")
# 	# for j in collect:
# 	# 	for u in disassembly:
# 	# 		if jtou[j, u] > 0:
# 	# 			print('%s -> %s: %g' % (j, u, jtou[j, u]))

# 	# print("Disassembly center to remanufacturing facility: ")
# 	# for u in disassembly:
# 	# 	for g in remanu:
# 	# 		if utog[u,g] > 0:
# 	# 			print('%s -> %s: %g' % (u, g, utog[u, g]))

# 	# print("Disassembly center to hybrid facility: ")
# 	# for u in disassembly:
# 	# 	for h in hybrid:
# 	# 		if utoh[u,h] > 0:
# 	# 			print('%s -> %s: %g' % (u, h, utoh[u, h]))

# 	# print("Components from U to V")
# 	# for k in component:
# 	# 	for u in disassembly:
# 	# 		for v in recycling:
# 	# 			if kutov[k, u, v] > 0:
# 	# 				print('%s -> %s: %g' % (u, v, kutov[k, u, v]))

# 	# print("Components from U to W")
# 	# for k in component:
# 	# 	for u in disassembly:
# 	# 		for w in disposal:
# 	# 			if kutow[k, u, w] > 0:
# 	# 				print('%s -> %s: %g' % (u, w, kutow[k, u, w]))
# 	# print(total_cost)
# 	# print("EK:")
# 	# print(EK.getValue())
# 	# print("PK:")
# 	# print(PK.getValue())
# 	# print("TK:")
# 	# print(TK.getValue())
# 	# print("KK:")
# 	# print(KK.getValue())
# 	# print("Emission in Ton:")
# 	# print(KK.getValue() / pi)
# 	# print("Optimality gap: ")
# 	# print(m.MIPGap)
# 	# print("=============================================================================================")
# 	# print("=============================================================================================")
# 	# print()

# elif m.Status == GRB.INFEASIBLE:
# 	print(f"ERROR in period {t}")
# 	m.computeIIS()
# 	m.write("model.ilp")
# 	m.write("hmrs.mps")
# 	for c in m.getConstrs():
# 		if c.IISConstr: print(f'\t{c.constrname}: {m.getRow(c)} {c.Sense} {c.RHS}')
# 	print("=============================================================================================")
# 	print("=============================================================================================")
# 	print()
