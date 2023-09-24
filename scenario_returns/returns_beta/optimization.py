import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import os

m = gp.Model('HMRS')

# Set time limit
time_limit_seconds = 60 * 3
m.setParam('TimeLimit', time_limit_seconds)

# Scenario: changes in M_j and beta dominant
parameters = "parameters/base/"
results = "results/scenario_returns/returns_beta/"

percentage_variations = [-0.5, -0.25, 0.0, 0.25, 0.5]

comparison = pd.DataFrame(columns=[f'{p * 100}%' for p in percentage_variations])
comparison_rows = ['Gesamtkosten', 'Einrichtungskosten', 'Produktionskosten', 'Transportkosten', 'Emissionskosten', 'CO2-Ausstoß', 'Optimality Gap', 'Run Time', 'Variables', 'Nodes', 'Constraints']
activation_compare = pd.DataFrame()

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

locations = manu + remanu + hybrid + collect + disassembly + recycling + disposal

# Reading basis scenario data
activation = pd.read_csv(parameters + 'activation_cost.csv', header=None)
demand = pd.read_csv(parameters + 'demand.csv', index_col=0)
distance = pd.read_csv(parameters + 'distance_matrix.csv', index_col=0)
processing = pd.read_csv(parameters + 'processing_cost.csv', index_col=0)
procurement = pd.read_csv(parameters + 'procurement_price.csv', index_col=0)
returns = pd.read_csv(parameters +  'returns.csv', index_col=0)
capacity = pd.read_csv(parameters + 'production_capacity.csv', index_col=0)
capacity_bar = pd.read_csv(parameters + 'production_capacity_bar.csv', index_col=0)
capacity_k = pd.read_csv(parameters + 'production_capacity_k.csv', index_col=0)
ratio = pd.read_csv(parameters + 'ratio_b_dominant.csv', index_col=0)


for change in percentage_variations:

	new = 1 + change
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
	E_F = 10
	E_G = 2
	E_H = 5
	E_J = 10
	E_U = 5
	E_KU = 0.5
	E_V = 0.5
	E_W = 2
	E_P = 0.009
	E_K = 0.0006


	# Emission capacity in kg
	CAP_Em = 20000000


	# Cost in euro
	pi = 0.085 # carbon legal per kg 
	pi_p = 0.134 # carbon penalty per kg
	omega_p = 0.0058 # per km per product
	omega_k = 0.00039 # per km per component


	# Amount of component component in a product
	R_k = {'k1': 1, 'k2': 4, 'k3': 10}


	# Production cost per period
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
			value = returns.loc[t, j] * new
			M_j[(t, j)] = value

	# The ratio between EoU, EoL and to-be-disposed components
	alpha = ratio['a'].tolist()
	beta = ratio['b'].tolist()
	gamma = ratio['c'].tolist()



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
		for f in capacity.filter(like='f').columns:
			value = capacity.loc[t, f]
			CAP_f[(t, f)] = value
		for g in capacity.filter(like='g').columns:
			value = capacity.loc[t, g]
			CAP_g[(t, g)] = value
		for h in capacity.filter(like='h').columns:
			value = capacity.loc[t, h]
			CAP_h[(t, h)] = value
		for j in capacity.filter(like='j').columns:
			value = capacity.loc[t, j]
			CAP_j[(t, j)] = value
		for u in capacity.filter(like='u').columns:
			value = capacity.loc[t, u]
			CAP_u[(t, u)] = value
	for t, row in capacity_bar.iterrows():
		for h in capacity_bar.columns:
			value = capacity_bar.loc[t, h]
			CAP_h_bar[(t, h)] = value
	for t, row in capacity_k.iterrows():
		for u in capacity_k.filter(like='u').columns:
			value = capacity_k.loc[t, u]
			CAP_Ku[(t, u)] = value
		for v in capacity_k.filter(like='v').columns:
			value = capacity_k.loc[t, v]
			CAP_Kv[(t, v)] = value
		for w in capacity_k.filter(like='w').columns:
			value = capacity_k.loc[t, w]
			CAP_Kw[(t, w)] = value


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
	legal = m.addVar(vtype=GRB.INTEGER, name="legal")
	excess = m.addVar(vtype=GRB.INTEGER, name="excess")
	CO2 = m.addVar(vtype=GRB.INTEGER)
	CAP_CO2 = m.addVar(vtype=GRB.INTEGER,lb=CAP_Em, ub=CAP_Em)
	var1 = m.addVar(lb=-GRB.INFINITY)


	# Set objective function
	# Activation costs of all facilities: SUM C_f * X_f
	EK = gp.quicksum(C_f[f] * X_f[f, t] / T for f in manu for t in period) + gp.quicksum(C_g[g] * X_g[g, t] / T for g in remanu for t in period) + gp.quicksum(C_h[h] * X_h[h, t] / T for h in hybrid for t in period) + gp.quicksum(C_j[a] * X_j[a, t] / T for a in collect for t in period) + gp.quicksum(C_u[a] * X_u[a, t] / T for a in disassembly for t in period) + gp.quicksum(C_v[a] * X_v[a, t] / T for a in recycling for t in period) + gp.quicksum(C_w[a] * X_w[a, t] / T for a in disposal for t in period)

	# Production/processing cost of all facilities: SUM B_f * Q_f
	PK = gp.quicksum(B_F[t] * Q_fi[f, i, t] for f in manu for i in warehouse for t in period) + gp.quicksum(B_G[t] * Q_gi[g, i, t] for g in remanu for i in warehouse for t in period) + gp.quicksum(B_H[t] * Q_hi[h, i, t] for h in hybrid for i in warehouse for t in period) + gp.quicksum(B_H_bar[t] * Q_hi_bar[h, i, t] for h in hybrid for i in warehouse) + gp.quicksum(B_J[t] * Q_ju[j, u, t] for j in collect for u in disassembly for t in period) + gp.quicksum(B_KU[t] * Q_kuw[k, u, w, t] for k in component for u in disassembly for w in disposal for t in period) + gp.quicksum(B_KU[t] * Q_kuv[k, u, v, t] for k in component for u in disassembly for v in recycling for t in period) + gp.quicksum(B_U[t] * Q_uh[u, h, t] for u in disassembly for h in hybrid for t in period) + gp.quicksum(B_U[t] * Q_ug[u, g, t] for u in disassembly for g in remanu for t in period) + gp.quicksum(B_V[t] * Q_kvf[k, v, f, t] for k in component for v in recycling for f in manu for t in period) + gp.quicksum(B_V[t] * Q_kvh[k, v, h, t] for k in component for v in recycling for h in hybrid for t in period) + gp.quicksum(P_k[t, k] * Q_klf[k, l, f, t] for k in component for l in supplier for f in manu for t in period) + gp.quicksum(P_k[t, k] * Q_klh[k, l, h, t] for k in component for l in supplier for h in hybrid for t in period)

	# Transportation cost of all products and components for all routes
	TK = omega_k * (gp.quicksum(S_lf[l, f] * Q_klf[k, l, f, t] for k in component for l in supplier for f in manu for t in period) + gp.quicksum(S_lh[l, h] * Q_klh[k, l, h, t] for k in component for l in supplier for h in hybrid for t in period) + gp.quicksum(S_uw[u, w] * Q_kuw[k, u, w, t] for k in component for u in disassembly for w in disposal for t in period) + gp.quicksum(S_uv[u, v] * Q_kuv[k, u, v, t] for k in component for u in disassembly for v in recycling for t in period) + gp.quicksum(S_vf[v, f] * Q_kvf[k, v, f, t] for k in component for v in recycling for f in manu for t in period) + gp.quicksum(S_vh[v, h] * Q_kvh[k, v, h, t] for k in component for v in recycling for h in hybrid for t in period)) + omega_p * (gp.quicksum(S_fi[f, i] * Q_fi[f, i, t] for f in manu for i in warehouse for t in period) + gp.quicksum(S_gi[g, i] * Q_gi[g, i, t] for g in remanu for i in warehouse for t in period) + gp.quicksum(S_hi[h, i] * Q_hi[h, i, t] for h in hybrid for i in warehouse for t in period) + gp.quicksum(S_hi[h, i] * Q_hi_bar[h, i, t] for h in hybrid for i in warehouse for t in period) + gp.quicksum(S_ju[j, u] * Q_ju[j, u, t] for j in collect for u in disassembly for t in period) + gp.quicksum(S_uh[u, h] * Q_uh[u, h, t] for u in disassembly for h in hybrid for t in period) + gp.quicksum(S_ug[u, g] * Q_ug[u, g, t] for u in disassembly for g in remanu for t in period))

	# Cost from CO2-offset
	KK = pi * legal + pi_p * excess


	# Define the objective function
	m.setObjective(EK + PK + TK + KK, GRB.MINIMIZE)

	m.addConstrs((gp.quicksum(Q_gi[g, i, 0] for i in warehouse) == 0 for g in remanu), name="gi0")
	m.addConstrs((gp.quicksum(Q_hi_bar[h, i, 0] for i in warehouse) == 0 for h in hybrid), name="hibar0")
	m.addConstrs((gp.quicksum(Q_fi[f, i, 0] for i in warehouse) * R_k[k] == gp.quicksum(Q_klf[k, l, f, 0] for l in supplier) for k in component for f in manu), name="klf_fi")
	m.addConstrs((gp.quicksum(Q_hi[h, i, 0] for i in warehouse) * R_k[k] == gp.quicksum(Q_klh[k, l, h, 0] for l in supplier) for k in component for h in hybrid), name="klh_hi")
	
	# Add constraints
	# (1)
	m.addConstrs(((gp.quicksum(Q_fi[f, i, t] for i in warehouse) <= CAP_f[t, f] * X_f[f, t]) for f in manu for t in period), name='c1')

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

	# (10)
	m.addConstrs(((gp.quicksum(Q_fi[f, i, t] for f in manu) + gp.quicksum(Q_hi[h, i, t] for h in hybrid) + gp.quicksum(Q_gi[g, i ,t] for g in remanu) + gp.quicksum(Q_hi_bar[h, i ,t] for h in hybrid) == D_i[t, i]) for i in warehouse for t in period), name='c10')

	# (11)
	m.addConstrs((gp.quicksum(Q_klf[a, b, c, int(t+1)] for b in supplier) + gp.quicksum(Q_kvf[a, b, c, t] for b in recycling)  == gp.quicksum(Q_fi[c, b, int(t+1)] for b in warehouse) * R_k[a] for a in component for c in manu for t in range(T-1)), name='c11')

	# (12)
	m.addConstrs((gp.quicksum(Q_ug[a, b, t] for a in disassembly) == gp.quicksum(Q_gi[b, c, int(t+1)] for c in warehouse) for b in remanu for t in range(T-1)), name='c12')

	# (13)
	m.addConstrs((gp.quicksum(Q_klh[a, b, c, int(t+1)] for b in supplier) + gp.quicksum(Q_kvh[a, b, c, t] for b in recycling) == gp.quicksum(Q_hi[c, b, int(t+1)] for b in warehouse) * R_k[a] for a in component for c in hybrid for t in range(T-1)), name='c13')

	# (14)
	m.addConstrs((gp.quicksum(Q_uh[u, h, t] for u in disassembly) == gp.quicksum(Q_hi_bar[h, i, int(t+1)] for i in warehouse) for h in hybrid for t in range(T-1)), name='c14')

	# (15)
	m.addConstrs(((gp.quicksum(Q_ju[j, u, t] for u in disassembly) == M_j[t, j]) for j in collect for t in period), name='c15')

	# (16)
	m.addConstrs((gp.quicksum(Q_ju[j, u, t] for j in collect) * alpha[t] == gp.quicksum(Q_ug[u, g, t] for g in remanu) + gp.quicksum(Q_uh[u,h,t] for h in hybrid) for u in disassembly for t in period), name='c16')

	# (17)
	m.addConstrs((gp.quicksum(Q_ju[j, u, t] for j in collect) * R_k[k] * beta[t]  == gp.quicksum(Q_kuv[k,u,v,t] for v in recycling) for u in disassembly for k in component for t in period), name='c17')

	# (18)
	m.addConstrs((gp.quicksum(Q_ju[j, u, t] for j in collect) * R_k[k] * gamma[t] == gp.quicksum(Q_kuw[k,u,w,t] for w in disposal) for u in disassembly for k in component for t in period), name='c18')

	# (19)
	m.addConstrs((gp.quicksum(Q_kuv[k, u, v, t] for u in disassembly) == (gp.quicksum(Q_kvf[k, v, f, t] for f in manu) + gp.quicksum(Q_kvh[k, v, h, t] for h in hybrid)) for k in component for v in recycling for t in period), name='c19')

	# CO2 constraint
	m.addConstr((CO2 == gp.quicksum(Q_fi[a, b, t] * E_F for a in manu for b in warehouse for t in period) + gp.quicksum(Q_gi[a, b, t] * E_G for a in remanu for b in warehouse for t in period) + gp.quicksum((Q_hi[a, b, t] + Q_hi_bar[a, b, t]) * E_H for a in hybrid for b in warehouse for t in period) + gp.quicksum(Q_ju[a, b, t] * E_J for a in collect for b in disassembly for t in period) + gp.quicksum(Q_ug[a, b, t] * E_U for a in disassembly for b in remanu for t in period) + gp.quicksum(Q_uh[a, b, t] * E_U for a in disassembly for b in hybrid for t in period) + gp.quicksum(Q_kuw[a, b, c, t] * E_KU for a in component for b in disassembly for c in disposal for t in period) + gp.quicksum(Q_kuv[a, b, c, t] * E_KU for a in component for b in disassembly for c in recycling for t in period) + gp.quicksum(Q_kvf[a, b, c, t] * E_V for a in component for b in recycling for c in manu for t in period) + gp.quicksum(Q_kvh[a, b, c, t] * E_V for a in component for b in recycling for c in hybrid for t in period) + (gp.quicksum(Q_fi[a, b, t] * S_fi[a, b] for a in manu for b in warehouse for t in period) + gp.quicksum(Q_gi[a, b, t] * S_gi[a, b] for a in remanu for b in warehouse for t in period) + gp.quicksum((Q_hi[a, b, t] + Q_hi_bar[a, b, t]) * S_hi[a, b] for a in hybrid for b in warehouse for t in period) + gp.quicksum(Q_ju[a, b, t] * S_ju[a, b] for a in collect for b in disassembly for t in period)) * E_P + (gp.quicksum(Q_klf[a, b, c, t] * S_lf[b, c] for a in component for b in supplier for c in manu for t in period) + gp.quicksum(Q_klh[a, b, c, t] * S_lh[b, c] for a in component for b in supplier for c in hybrid for t in period) + gp.quicksum(Q_kuw[a, b, c, t] * S_uw[b, c] for a in component for b in disassembly for c in disposal for t in period) + gp.quicksum(Q_kuv[a, b, c, t] * S_uv[b, c] for a in component for b in disassembly for c in recycling for t in period) + gp.quicksum(Q_kvf[a, b, c, t] * S_vf[b, c] for a in component for b in recycling for c in manu for t in period) + gp.quicksum(Q_kvh[a, b, c, t] * S_vh[b, c] for a in component for b in recycling for c in hybrid for t in period)) * E_K), name="CO2")

	m.addConstr(var1 == CO2 - CAP_CO2)
	m.addGenConstrMin(legal, [CO2, CAP_CO2])
	m.addGenConstrMax(excess, [var1], 0.0)

	# Activation constraint: Once a facility is opened in the first period, it stays open. No new facilities are allowed to open in later periods
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

	results_foldername = f'M_j_b_{int(change * 100)}/'
	results_path = os.path.join(results, results_foldername)
	os.makedirs(results_path, exist_ok=True)
	log_filename = results + results_foldername + "mip_log.txt"
	objective_filename = results + results_foldername + "objective_function.txt"

	m.Params.OutputFlag = 1
	m.Params.LogFile = log_filename

	m.optimize()


	# Print out results
	if m.Status == GRB.OPTIMAL:
		
		gap = m.MIPGap
		time = m.Runtime
		num_var = m.NumVars
		num_constr = m.NumConstrs
		nodes = m.NodeCount
		solution = m.getAttr('X')
		total_cost = m.ObjVal

		comparison.at['Gesamtkosten', f'{change * 100}%'] = round(total_cost)
		comparison.at['Einrichtungskosten', f'{change * 100}%'] = round(EK.getValue())
		comparison.at['Produktionskosten', f'{change * 100}%'] = round(PK.getValue())
		comparison.at['Transportkosten', f'{change * 100}%'] = round(TK.getValue())
		comparison.at['Emissionskosten', f'{change * 100}%'] = round(KK.getValue())
		comparison.at['CO2-Ausstoß', f'{change * 100}%'] = round(CO2.X)
		comparison.at['Optimality Gap', f'{change * 100}%'] = gap
		comparison.at['Run Time', f'{change * 100}%'] = time
		comparison.at['Variables', f'{change * 100}%'] = num_var
		comparison.at['Constraints', f'{change * 100}%'] = num_constr
		comparison.at['Nodes', f'{change * 100}%'] = nodes


		# Activation decisions
		activation_table = pd.DataFrame(columns=[l for l in locations])

		xf = m.getAttr('X', X_f)
		xf_filter = {key: value for key, value in xf.items() if key[1] == 0}
		xf_df = pd.DataFrame.from_dict(xf_filter, orient='index', columns=['0'])
		xf_df.index = xf_df.index.map(lambda x: x[0])
		xf_df = xf_df.T
		
		xg = m.getAttr('X', X_g)
		xg_filter = {key: value for key, value in xg.items() if key[1] == 0}
		xg_df = pd.DataFrame.from_dict(xg_filter, orient='index', columns=['0'])
		xg_df.index = xg_df.index.map(lambda x: x[0])
		xg_df = xg_df.T

		xh = m.getAttr('X', X_h)
		xh_filter = {key: value for key, value in xh.items() if key[1] == 0}
		xh_df = pd.DataFrame.from_dict(xh_filter, orient='index', columns=['0'])
		xh_df.index = xh_df.index.map(lambda x: x[0])
		xh_df = xh_df.T

		xj = m.getAttr('X', X_j)
		xj_filter = {key: value for key, value in xj.items() if key[1] == 0}
		xj_df = pd.DataFrame.from_dict(xj_filter, orient='index', columns=['0'])
		xj_df.index = xj_df.index.map(lambda x: x[0])
		xj_df = xj_df.T

		xu = m.getAttr('X', X_u)
		xu_filter = {key: value for key, value in xu.items() if key[1] == 0}
		xu_df = pd.DataFrame.from_dict(xu_filter, orient='index', columns=['0'])
		xu_df.index = xu_df.index.map(lambda x: x[0])
		xu_df = xu_df.T

		xv = m.getAttr('X', X_v)
		xv_filter = {key: value for key, value in xv.items() if key[1] == 0}
		xv_df = pd.DataFrame.from_dict(xv_filter, orient='index', columns=['0'])
		xv_df.index = xv_df.index.map(lambda x: x[0])
		xv_df = xv_df.T

		xw = m.getAttr('X', X_w)
		xw_filter = {key: value for key, value in xw.items() if key[1] == 0}
		xw_df = pd.DataFrame.from_dict(xw_filter, orient='index', columns=['0'])
		xw_df.index = xw_df.index.map(lambda x: x[0])
		xw_df = xw_df.T


		activation_table = pd.concat([xf_df, xg_df, xh_df, xj_df, xu_df, xv_df, xw_df], axis=1)
		activation_compare = pd.concat([activation_compare, activation_table], axis=0)
		activation_compare.to_csv(results + "activation_comparison.csv")

		# Transport quantity Q_klf: supplier --> manu
		lf = m.getAttr('X', Q_klf)
		qklf = pd.DataFrame.from_dict(lf, orient="index")
		qklf.index = pd.MultiIndex.from_tuples(qklf.index)
		qklf = qklf.unstack().groupby(level=0)
		qklf_df = {}
		for name, df in qklf:
			qklf_df[name] = df
		k1_lf = qklf_df['k1']
		k2_lf = qklf_df['k2']
		k3_lf = qklf_df['k3']
		k1_lf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klf_k1.csv")
		k2_lf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klf_k2.csv")
		k3_lf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klf_k3.csv")


		# Transport quantity Q_klh: supplier --> hybrid
		lh = m.getAttr('X', Q_klh)
		qklh = pd.DataFrame.from_dict(lh, orient="index")
		qklh.index = pd.MultiIndex.from_tuples(qklh.index)
		qklh = qklh.unstack().groupby(level=0)
		qklh_df = {}
		for name, df in qklh:
			qklh_df[name] = df
		k1_lh = qklh_df['k1']
		k2_lh = qklh_df['k2']
		k3_lh = qklh_df['k3']
		k1_lh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klh_k1.csv")
		k2_lh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klh_k2.csv")
		k3_lh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klh_k3.csv")


		# Transport quantity Q_fi: manu --> warehouse
		fi = m.getAttr('X', Q_fi)
		qfi = pd.DataFrame.from_dict(fi, orient="index")
		qfi.index = pd.MultiIndex.from_tuples(qfi.index)
		qfi = qfi.unstack()
		qfi.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_fi.csv")


		# Transport quantity Q_gi: remanu --> warehouse
		gi = m.getAttr('X', Q_gi)
		qgi = pd.DataFrame.from_dict(gi, orient="index")
		qgi.index = pd.MultiIndex.from_tuples(qgi.index)
		qgi = qgi.unstack()
		qgi.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_gi.csv")


		# Transport quantity Q_hi: hybrid --> warehouse
		hi = m.getAttr('X', Q_hi)
		qhi = pd.DataFrame.from_dict(hi, orient="index")
		qhi.index = pd.MultiIndex.from_tuples(qhi.index)
		qhi = qhi.unstack()
		qhi.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_hi.csv")


		# Transport quantity Q_hi_bar: hybrid --> warehouse
		hi_bar = m.getAttr('X', Q_hi_bar)
		qhi_bar = pd.DataFrame.from_dict(hi_bar, orient="index")
		qhi_bar.index = pd.MultiIndex.from_tuples(qhi_bar.index)
		qhi_bar = qhi_bar.unstack()
		qhi_bar.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_hi_bar.csv")


		# Transport quantity Q_ju: collection --> disassembly
		ju = m.getAttr('X', Q_ju)
		qju = pd.DataFrame.from_dict(ju, orient="index")
		qju.index = pd.MultiIndex.from_tuples(qju.index)
		qju = qju.unstack()
		qju.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_ju.csv")


		# Transport component quantity Q_kuv: disassembly --> recycling
		uv = m.getAttr('X', Q_kuv)
		qkuv = pd.DataFrame.from_dict(uv, orient="index")
		qkuv.index = pd.MultiIndex.from_tuples(qkuv.index)
		qkuv = qkuv.unstack().groupby(level=0)
		qkuv_df = {}
		for name, df in qkuv:
			qkuv_df[name] = df
		k1_uv = qkuv_df['k1']
		k2_uv = qkuv_df['k2']
		k3_uv = qkuv_df['k3']
		k1_uv.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuv_k1.csv")
		k2_uv.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuv_k2.csv")
		k3_uv.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuv_k3.csv")


		# Transport component quantity Q_kuw: disassembly --> disposal
		uw = m.getAttr('X', Q_kuw)
		qkuw = pd.DataFrame.from_dict(uw, orient="index")
		qkuw.index = pd.MultiIndex.from_tuples(qkuw.index)
		qkuw = qkuw.unstack().groupby(level=0)
		qkuw_df = {}
		for name, df in qkuw:
			qkuw_df[name] = df
		k1_uw = qkuw_df['k1']
		k2_uw = qkuw_df['k2']
		k3_uw = qkuw_df['k3']
		k1_uw.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuw_k1.csv")
		k2_uw.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuw_k2.csv")
		k3_uw.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuw_k3.csv")


		# Transport quantity Q_ug: disassembly --> remanu
		ug = m.getAttr('X', Q_ug)
		qug = pd.DataFrame.from_dict(ug, orient="index")
		qug.index = pd.MultiIndex.from_tuples(qug.index)
		qug = qug.unstack()
		qug.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_ug.csv")


		# Transport quantity Q_uh: disassembly --> hybrid
		uh = m.getAttr('X', Q_uh)
		uh = m.getAttr('X', Q_uh)
		quh = pd.DataFrame.from_dict(uh, orient="index")
		quh.index = pd.MultiIndex.from_tuples(quh.index)
		quh = quh.unstack()
		quh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_uh.csv")


		# Transport component quantity Q_kvf: recycling --> manu
		vf = m.getAttr('X', Q_kvf)
		qkvf = pd.DataFrame.from_dict(vf, orient="index")
		qkvf.index = pd.MultiIndex.from_tuples(qkvf.index)
		qkvf = qkvf.unstack().groupby(level=0)
		qkvf_df = {}
		for name, df in qkvf:
			qkvf_df[name] = df
		k1_vf = qkvf_df['k1']
		k2_vf = qkvf_df['k2']
		k3_vf = qkvf_df['k3']
		k1_vf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvf_k1.csv")
		k2_vf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvf_k2.csv")
		k3_vf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvf_k3.csv")


		# Transport component quantity Q_kvh: recycling --> hybrid
		vh = m.getAttr('X', Q_kvh)
		qkvh = pd.DataFrame.from_dict(vh, orient="index")
		qkvh.index = pd.MultiIndex.from_tuples(qkvh.index)
		qkvh = qkvh.unstack().groupby(level=0)
		qkvh_df = {}
		for name, df in qkvh:
			qkvh_df[name] = df
		k1_vh = qkvh_df['k1']
		k2_vh = qkvh_df['k2']
		k3_vh = qkvh_df['k3']
		k1_vh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvh_k1.csv")
		k2_vh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvh_k2.csv")
		k3_vh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvh_k3.csv")



		print("=======================================================================================")
		print("=============================== Optimal solution found! ===============================")
		print("=======================================================================================")


	# If set time limit is reached
	# if m.Status == GRB.TIME_LIMIT:

	# 	gap = m.MIPGap
	# 	time = m.Runtime
	# 	num_var = m.NumVars
	# 	num_constr = m.NumConstrs
	# 	nodes = m.NodeCount
	# 	solution = m.getAttr('X')
	# 	total_cost = m.ObjVal

	# 	results_foldername = f'M_j_b_{int(change * 100)}/'
	# 	results_path = os.path.join(results, results_foldername)
	# 	os.makedirs(results_path, exist_ok=True)

	# 	comparison.at['Gesamtkosten', f'{change * 100}%'] = round(total_cost)
	# 	comparison.at['Einrichtungskosten', f'{change * 100}%'] = round(EK.getValue())
	# 	comparison.at['Produktionskosten', f'{change * 100}%'] = round(PK.getValue())
	# 	comparison.at['Transportkosten', f'{change * 100}%'] = round(TK.getValue())
	# 	comparison.at['Emissionskosten', f'{change * 100}%'] = round(KK.getValue())
	# 	comparison.at['CO2-Ausstoß', f'{change * 100}%'] = round(CO2.X)
	# 	comparison.at['Optimality Gap', f'{change * 100}%'] = gap
	# 	comparison.at['Run Time', f'{change * 100}%'] = time
	# 	comparison.at['Variables', f'{change * 100}%'] = num_var
	# 	comparison.at['Constraints', f'{change * 100}%'] = num_constr
	# 	comparison.at['Nodes', f'{change * 100}%'] = nodes
	
	# 	# Activation decisions
	# 	xf = m.getAttr('X', X_f)
	# 	actv_xf = pd.DataFrame.from_dict(xf, orient="index")
	# 	actv_xf.index = pd.MultiIndex.from_tuples(actv_xf.index)
	# 	actv_xf = actv_xf.unstack()
		
	# 	xg = m.getAttr('X', X_g)
	# 	actv_xg = pd.DataFrame.from_dict(xg, orient="index")
	# 	actv_xg.index = pd.MultiIndex.from_tuples(actv_xg.index)
	# 	actv_xg = actv_xg.unstack()

	# 	xh = m.getAttr('X', X_h)
	# 	actv_xh = pd.DataFrame.from_dict(xh, orient="index")
	# 	actv_xh.index = pd.MultiIndex.from_tuples(actv_xh.index)
	# 	actv_xh = actv_xh.unstack()

	# 	xj = m.getAttr('X', X_j)
	# 	actv_xj = pd.DataFrame.from_dict(xj, orient="index")
	# 	actv_xj.index = pd.MultiIndex.from_tuples(actv_xj.index)
	# 	actv_xj = actv_xj.unstack()

	# 	xu = m.getAttr('X', X_u)
	# 	actv_xu = pd.DataFrame.from_dict(xu, orient="index")
	# 	actv_xu.index = pd.MultiIndex.from_tuples(actv_xu.index)
	# 	actv_xu = actv_xu.unstack()

	# 	xv = m.getAttr('X', X_v)
	# 	actv_xv = pd.DataFrame.from_dict(xv, orient="index")
	# 	actv_xv.index = pd.MultiIndex.from_tuples(actv_xv.index)
	# 	actv_xv = actv_xv.unstack()

	# 	xw = m.getAttr('X', X_w)
	# 	actv_xw = pd.DataFrame.from_dict(xw, orient="index")
	# 	actv_xw.index = pd.MultiIndex.from_tuples(actv_xw.index)
	# 	actv_xw = actv_xw.unstack()

	# 	activation_matrix = pd.concat([actv_xf, actv_xg, actv_xh, actv_xj, actv_xu, actv_xv, actv_xw]).transpose().head(1)
	# 	activation_matrix.to_csv(results_path + f"M_j_b_{int(change * 100)}_activation_matrix.csv")


	# 	# Transport quantity Q_klf: supplier --> manu
	# 	lf = m.getAttr('X', Q_klf)
	# 	qklf = pd.DataFrame.from_dict(lf, orient="index")
	# 	qklf.index = pd.MultiIndex.from_tuples(qklf.index)
	# 	qklf = qklf.unstack().groupby(level=0)
	# 	qklf_df = {}
	# 	for name, df in qklf:
	# 		qklf_df[name] = df
	# 	k1_lf = qklf_df['k1']
	# 	k2_lf = qklf_df['k2']
	# 	k3_lf = qklf_df['k3']
	# 	k1_lf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klf_k1.csv")
	# 	k2_lf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klf_k2.csv")
	# 	k3_lf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klf_k3.csv")


	# 	# Transport quantity Q_klh: supplier --> hybrid
	# 	lh = m.getAttr('X', Q_klh)
	# 	qklh = pd.DataFrame.from_dict(lh, orient="index")
	# 	qklh.index = pd.MultiIndex.from_tuples(qklh.index)
	# 	qklh = qklh.unstack().groupby(level=0)
	# 	qklh_df = {}
	# 	for name, df in qklh:
	# 		qklh_df[name] = df
	# 	k1_lh = qklh_df['k1']
	# 	k2_lh = qklh_df['k2']
	# 	k3_lh = qklh_df['k3']
	# 	k1_lh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klh_k1.csv")
	# 	k2_lh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klh_k2.csv")
	# 	k3_lh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_klh_k3.csv")


	# 	# Transport quantity Q_fi: manu --> warehouse
	# 	fi = m.getAttr('X', Q_fi)
	# 	qfi = pd.DataFrame.from_dict(fi, orient="index")
	# 	qfi.index = pd.MultiIndex.from_tuples(qfi.index)
	# 	qfi = qfi.unstack()
	# 	qfi.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_fi.csv")


	# 	# Transport quantity Q_gi: remanu --> warehouse
	# 	gi = m.getAttr('X', Q_gi)
	# 	qgi = pd.DataFrame.from_dict(gi, orient="index")
	# 	qgi.index = pd.MultiIndex.from_tuples(qgi.index)
	# 	qgi = qgi.unstack()
	# 	qgi.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_gi.csv")


	# 	# Transport quantity Q_hi: hybrid --> warehouse
	# 	hi = m.getAttr('X', Q_hi)
	# 	qhi = pd.DataFrame.from_dict(hi, orient="index")
	# 	qhi.index = pd.MultiIndex.from_tuples(qhi.index)
	# 	qhi = qhi.unstack()
	# 	qhi.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_hi.csv")


	# 	# Transport quantity Q_hi_bar: hybrid --> warehouse
	# 	hi_bar = m.getAttr('X', Q_hi_bar)
	# 	qhi_bar = pd.DataFrame.from_dict(hi_bar, orient="index")
	# 	qhi_bar.index = pd.MultiIndex.from_tuples(qhi_bar.index)
	# 	qhi_bar = qhi_bar.unstack()
	# 	qhi_bar.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_hi_bar.csv")


	# 	# Transport quantity Q_ju: collection --> disassembly
	# 	ju = m.getAttr('X', Q_ju)
	# 	qju = pd.DataFrame.from_dict(ju, orient="index")
	# 	qju.index = pd.MultiIndex.from_tuples(qju.index)
	# 	qju = qju.unstack()
	# 	qju.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_ju.csv")


	# 	# Transport component quantity Q_kuv: disassembly --> recycling
	# 	uv = m.getAttr('X', Q_kuv)
	# 	qkuv = pd.DataFrame.from_dict(uv, orient="index")
	# 	qkuv.index = pd.MultiIndex.from_tuples(qkuv.index)
	# 	qkuv = qkuv.unstack().groupby(level=0)
	# 	qkuv_df = {}
	# 	for name, df in qkuv:
	# 		qkuv_df[name] = df
	# 	k1_uv = qkuv_df['k1']
	# 	k2_uv = qkuv_df['k2']
	# 	k3_uv = qkuv_df['k3']
	# 	k1_uv.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuv_k1.csv")
	# 	k2_uv.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuv_k2.csv")
	# 	k3_uv.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuv_k3.csv")


	# 	# Transport component quantity Q_kuw: disassembly --> disposal
	# 	uw = m.getAttr('X', Q_kuw)
	# 	qkuw = pd.DataFrame.from_dict(uw, orient="index")
	# 	qkuw.index = pd.MultiIndex.from_tuples(qkuw.index)
	# 	qkuw = qkuw.unstack().groupby(level=0)
	# 	qkuw_df = {}
	# 	for name, df in qkuw:
	# 		qkuw_df[name] = df
	# 	k1_uw = qkuw_df['k1']
	# 	k2_uw = qkuw_df['k2']
	# 	k3_uw = qkuw_df['k3']
	# 	k1_uw.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuw_k1.csv")
	# 	k2_uw.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuw_k2.csv")
	# 	k3_uw.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kuw_k3.csv")


	# 	# Transport quantity Q_ug: disassembly --> remanu
	# 	ug = m.getAttr('X', Q_ug)
	# 	qug = pd.DataFrame.from_dict(ug, orient="index")
	# 	qug.index = pd.MultiIndex.from_tuples(qug.index)
	# 	qug = qug.unstack()
	# 	qug.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_ug.csv")


	# 	# Transport quantity Q_uh: disassembly --> hybrid
	# 	uh = m.getAttr('X', Q_uh)
	# 	uh = m.getAttr('X', Q_uh)
	# 	quh = pd.DataFrame.from_dict(uh, orient="index")
	# 	quh.index = pd.MultiIndex.from_tuples(quh.index)
	# 	quh = quh.unstack()
	# 	quh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_uh.csv")


	# 	# Transport component quantity Q_kvf: recycling --> manu
	# 	vf = m.getAttr('X', Q_kvf)
	# 	qkvf = pd.DataFrame.from_dict(vf, orient="index")
	# 	qkvf.index = pd.MultiIndex.from_tuples(qkvf.index)
	# 	qkvf = qkvf.unstack().groupby(level=0)
	# 	qkvf_df = {}
	# 	for name, df in qkvf:
	# 		qkvf_df[name] = df
	# 	k1_vf = qkvf_df['k1']
	# 	k2_vf = qkvf_df['k2']
	# 	k3_vf = qkvf_df['k3']
	# 	k1_vf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvf_k1.csv")
	# 	k2_vf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvf_k2.csv")
	# 	k3_vf.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvf_k3.csv")


	# 	# Transport component quantity Q_kvh: recycling --> hybrid
	# 	vh = m.getAttr('X', Q_kvh)
	# 	qkvh = pd.DataFrame.from_dict(vh, orient="index")
	# 	qkvh.index = pd.MultiIndex.from_tuples(qkvh.index)
	# 	qkvh = qkvh.unstack().groupby(level=0)
	# 	qkvh_df = {}
	# 	for name, df in qkvh:
	# 		qkvh_df[name] = df
	# 	k1_vh = qkvh_df['k1']
	# 	k2_vh = qkvh_df['k2']
	# 	k3_vh = qkvh_df['k3']
	# 	k1_vh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvh_k1.csv")
	# 	k2_vh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvh_k2.csv")
	# 	k3_vh.to_csv(results_path + f"M_j_b_{int(change * 100)}_Q_kvh_k3.csv")

	# 	print("=======================================================================================")
	# 	print("=============================== Time limit reached! ===================================")
	# 	print("=======================================================================================")


	elif m.Status == GRB.INFEASIBLE:
		m.computeIIS()
		m.write(results_path + "/model.ilp")
		for c in m.getConstrs():
			if c.IISConstr: print(f'\t{c.constrname}: {m.getRow(c)} {c.Sense} {c.RHS}')

		print("=======================================================================================")
		print("================================ Model is infeasible! =================================")
		print("=======================================================================================")
	m.reset()

	final_comparison = pd.concat([comparison], axis=1)
	final_comparison.to_csv(results + "objective_comparison.csv")