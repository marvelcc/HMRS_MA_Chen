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

# C_f = {a: round(random.normalvariate(200, 20)) * 10000 for a in manu}
# C_g = {a: round(random.normalvariate(150, 15)) * 10000 for a in remanu}
# C_h = {a: round(random.normalvariate(100, 10)) * 10000 for a in hybrid}
# C_j = {a: round(random.normalvariate(40, 4)) * 10000 for a in collect}
# C_u = {a: round(random.normalvariate(100, 10)) * 10000 for a in disassembly}
# C_v = {a: round(random.normalvariate(80, 8)) * 10000 for a in recycling}
# C_w = {a: round(random.normalvariate(40, 4)) * 10000 for a in disposal}

# locations = {**C_f, **C_g, **C_h, **C_j, **C_u, **C_v, **C_w}

# with open('activation_cost.csv', 'w') as csv_file:
#     writer = csv.writer(csv_file)
#     for key, value in locations.items():
#         writer.writerow([key, value])

# csv_file.close()

# -------------------------------------------------

# Production/processing cost for each type of facility
# Values subject to change according to collected real world data

# B_F_t = []
# B_H_t = []
# B_G_t = []
# B_H_bar_t = []
# B_J_t = []
# B_KU_t = []
# B_U_t = []
# B_V_t = []
# B_W_t = []

# for t in range(T):
    
#     B_F = random.randrange(20,40)
#     B_G = random.randrange(10,20)
#     B_H = random.randrange(20,40)
#     B_H_bar = random.randrange(10,20)
#     B_J = random.randrange(4,8)
#     B_KU = random.randrange(2,4)
#     B_U = random.randrange(10,20)
#     B_V = random.randrange(8,16)
#     B_W = random.randrange(4,8)

    
#     B_F_t.append(B_F)
#     B_H_t.append(B_H)
#     B_G_t.append(B_G)
#     B_H_bar_t.append(B_H_bar)
#     B_J_t.append(B_J)
#     B_KU_t.append(B_KU)
#     B_U_t.append(B_U)
#     B_V_t.append(B_V)
#     B_W_t.append(B_W)

# processing_cost = {'B_F': B_F_t, 'B_G': B_G_t, 'B_H': B_H_t, 'B_H_bar': B_H_bar_t, 'B_J': B_J_t, 'B_KU': B_KU_t, 'B_U': B_U_t, 'B_V': B_V_t, 'B_W': B_W_t}
# df_processing = pd.DataFrame(processing_cost)
# df_processing.to_csv('processing_cost.csv')

# -------------------------------------------------

# Procurement cost of each component at each period
# Values subject to change according to collected real world data

# price_ranges = {'k1': (6, 10), 'k2': (4, 8), 'k3': (1, 3)}
# df_procurement = pd.DataFrame()
# for k in component:
#     min_price, max_price = price_ranges[k]
#     prices = [random.randint(min_price, max_price) for _ in range(T)]
#     df_procurement[k] = prices
# df_procurement.to_csv('procurement_price.csv')

# -------------------------------------------------

# Create distance matrix between each location, not all combination are used

# facilities = supplier + manu + remanu + hybrid + warehouse + collect + disassembly + recycling + disposal
# distance_table = {loc1: {loc2: 0 if loc1 == loc2 else random.randint(10, 35) * 10 for loc2 in facilities} for loc1 in facilities}
# df_distance = pd.DataFrame.from_dict(distance_table, orient='index')
# df_distance.to_csv('distance_matrix.csv')

# -------------------------------------------------

# Demand of products (new and remanufactured) at every distribution center for each period
# Values subject to change according to collected real world data

# total_demand = {}
# for i in warehouse:
#     demand = [round(random.normalvariate(120, 12)) * 10 for t in range(T)]
#     total_demand[i] = demand
# df_demand = pd.DataFrame(total_demand)
# df_demand.to_csv('demand.csv')

# -------------------------------------------------

# Number of returned products at each collection center for each period
# should be between 25% and 75% of sold items (according to research)
# Values subject to change according to real world data

# total_returns = {}
# for j in collect:
#     returns = [random.randint(20, 60) * 10 for t in range(T)]
#     total_returns[j] = returns
# df_returns = pd.DataFrame(total_returns)
# df_returns.to_csv('returns.csv')

# -------------------------------------------------

# The production capacity of every location at each period
# Values subject to change according to real world data

# cap = []
# cap_bar = []
# cap_component = []
# for t in range(T):
#     capacities = {}
#     for f in manu:
#         capacities[f] = round(random.normalvariate(120, 12)) * 10
#     for g in remanu:
#         capacities[g] = round(random.normalvariate(60, 6)) * 10
#     for h in hybrid:
#         capacities[h] = round(random.normalvariate(60, 6)) * 10
#     for j in collect:
#         capacities[j] = round(random.normalvariate(100, 10)) * 10
#     for u in disassembly:
#         capacities[u] = round(random.normalvariate(80, 8)) * 10
#     cap.append({**capacities})

#     capacities_bar = {}
#     for h in hybrid:
#         capacities_bar[h] = round(random.normalvariate(30, 3)) * 10
#     cap_bar.append({**capacities_bar})

#     capacities_comp = {}
#     for Ku in disassembly:
#         capacities_comp[Ku] = round(random.normalvariate(60, 6)) * 100
#     for Kv in recycling:
#         capacities_comp[Kv] = round(random.normalvariate(45, 4.5)) * 100
#     for Kw in disposal:
#         capacities_comp[Kw] = round(random.normalvariate(70, 7)) * 100
#     cap_component.append({**capacities_comp})

# df_prod_cap = pd.DataFrame(cap)
# df_prod_cap.to_csv('production_capacity.csv')

# df_prod_cap = pd.DataFrame(cap_bar)
# df_prod_cap.to_csv('production_capacity_bar.csv')

# df_prod_cap = pd.DataFrame(cap_component)
# df_prod_cap.to_csv('production_capacity_k.csv')

# -------------------------------------------------

# The ratio between EoU, EoL and to-be-disposed components
# Ratio subject to change

# ratio = []
# for t in range(T):
#     a = round(random.uniform(0.5, 0.7), 2)
#     b = round(random.uniform(0.15, 0.4), 2)
#     c = 1 - a - b
#     if c < 0.1:
#         c = 0.1
#     ratio.append({'a': a, 'b': b, 'c': c})

# df_ratio = pd.DataFrame(ratio)
# df_ratio.to_csv('ratio.csv')

# -------------------------------------------------


