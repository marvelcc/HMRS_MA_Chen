import csv
import random
import pandas as pd

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
T = 12

# -------------------------------------------------

# Activation cost of each facility
# Values subject to change according to collected real world data

# C_f = {a: random.randrange(200,351)*10000 for a in manu}
# C_g = {a: random.randrange(200,351)*10000 for a in remanu}
# C_h = {a: random.randrange(200,351)*10000 for a in hybrid}
# C_j = {a: random.randrange(100,251)*1000 for a in collect}
# C_u = {a: random.randrange(100,251)*1000 for a in disassembly}
# C_v = {a: random.randrange(100,251)*1000 for a in recycling}
# C_w = {a: random.randrange(100,251)*1000 for a in disposal}

# locations = {**C_f, **C_g, **C_h, **C_j, **C_u, **C_v, **C_w}

# with open('activation_cost.csv', 'w') as csv_file:
#     writer = csv.writer(csv_file)
#     for key, value in locations.items():
#         writer.writerow([key, value])

# csv_file.close()

# -------------------------------------------------

# Production/processing cost for each type of facility
# Values subject to change according to collected real world data

# periods = []
# B_F_t = []
# B_H_t = []
# B_G_t = []
# B_H_bar_t = []
# B_J_t = []
# B_KU_t = []
# B_U_t = []
# B_V_t = []
# B_T_t = []

# for t in range(T):
#     period = t + 1
#     B_F = random.randrange(20,25)
#     B_G = random.randrange(15,20)
#     B_H = random.randrange(15,20)
#     B_H_bar = random.randrange(10,15)
#     B_J = random.randrange(5,8)
#     B_KU = random.randrange(1,4)
#     B_U = random.randrange(1,4)
#     B_V = random.randrange(1,4)
#     B_T = random.randrange(1,4)

#     periods.append(period)
#     B_F_t.append(B_F)
#     B_H_t.append(B_H)
#     B_G_t.append(B_G)
#     B_H_bar_t.append(B_H_bar)
#     B_J_t.append(B_J)
#     B_KU_t.append(B_KU)
#     B_U_t.append(B_U)
#     B_V_t.append(B_V)
#     B_T_t.append(B_T)

# processing_cost = {'period': periods, 'B_F': B_F_t, 'B_G': B_G_t, 'B_H': B_H_t, 'B_H_bar': B_H_bar_t, 'B_J': B_J_t, 'B_KU': B_KU_t, 'B_U': B_U_t, 'B_V': B_V_t, 'B_T': B_T_t}
# df_processing = pd.DataFrame(processing_cost)
# df_processing.to_csv('processing_cost.csv', index=False)

# -------------------------------------------------

# Procurement cost of each component at each period
# Values subject to change according to collected real world data

# procurement_price = {'period': list(range(1, T+1))}
# for k in component:
#     prices = [random.randint(1, 6) for t in range(T)]
#     procurement_price[k] = prices
# df_procurement = pd.DataFrame(procurement_price)
# df_procurement.to_csv('procurement_price.csv', index=False)

# -------------------------------------------------

# Create distance matrix between each location, not all combination are used

# facilities = manu + remanu + hybrid + collect + disassembly + recycling + disposal
# distance_table = {loc1: {loc2: 0 if loc1 == loc2 else random.randint(10, 75) for loc2 in facilities} for loc1 in facilities}
# df_distance = pd.DataFrame.from_dict(distance_table, orient='index')
# df_distance.to_csv('distance_matrix.csv')

# -------------------------------------------------

# Demand of products (new and remanufactured) at every distribution center for each period
# Values subject to change according to collected real world data

# total_demand = {'period': list(range(1, T+1))}
# for i in warehouse:
#     demand = [random.randint(10, 40) * 1000 for t in range(T)]
#     total_demand[i] = demand
# df_demand = pd.DataFrame(total_demand)
# df_demand.to_csv('demand.csv', index=False)

# -------------------------------------------------

# Number of returned products at each collection center for each period
# should be between 25% and 75% of sold items (according to research)
# Values subject to change according to real world data

# total_returns = {'period': list(range(1, T+1))}
# for j in collect:
#     returns = [random.randint(8, 20) * 1000 for t in range(T)]
#     total_returns[j] = returns
# df_returns = pd.DataFrame(total_returns)
# df_returns.to_csv('returns.csv', index=False)

# -------------------------------------------------

# The production capacity of every location at each period
# Values subject to change according to real world data

# cap = []
# for t in range(T):
#     capacities = {}
#     for f in manu:
#         capacities[f] = random.randint(15,25) * 1000
#     for g in remanu:
#         capacities[g] = random.randint(8,14) * 1000
#     for h in hybrid:
#         capacities[h] = random.randint(9,15) * 1000
#     for h_bar in hybrid:
#         capacities[h_bar] = random.randint(5,10) * 1000
#     for j in collect:
#         capacities[j] = random.randint(8,15) * 1000
#     for u in disassembly:
#         capacities[u] = random.randint(10,15) * 1000
#     for Ku in disassembly:
#         capacities[Ku] = random.randint(30,50) * 300
#     for Kv in recycling:
#         capacities[Kv] = random.randint(15,25) * 300
#     for Kw in disposal:
#         capacities[Kw] = random.randint(15,25) * 300

#     cap.append({'period': t + 1, **capacities})

# df_prod_cap = pd.DataFrame(cap).set_index('period')
# df_prod_cap.to_csv('production_capacity.csv')

# -------------------------------------------------




