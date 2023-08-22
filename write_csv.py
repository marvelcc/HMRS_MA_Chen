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

C_f = {a: random.randrange(200,351)*10000 for a in manu}
C_g = {a: random.randrange(150,250)*10000 for a in remanu}
C_h = {a: random.randrange(105,200)*10000 for a in hybrid}
C_j = {a: random.randrange(100,251)*1000 for a in collect}
C_u = {a: random.randrange(100,251)*1000 for a in disassembly}
C_v = {a: random.randrange(100,251)*1000 for a in recycling}
C_w = {a: random.randrange(100,251)*1000 for a in disposal}

locations = {**C_f, **C_g, **C_h, **C_j, **C_u, **C_v, **C_w}

with open('activation_cost.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in locations.items():
        writer.writerow([key, value])

csv_file.close()

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
    
#     B_F = random.randrange(20,25)
#     B_G = random.randrange(15,20)
#     B_H = random.randrange(15,20)
#     B_H_bar = random.randrange(10,15)
#     B_J = random.randrange(5,8)
#     B_KU = random.randrange(1,4)
#     B_U = random.randrange(1,4)
#     B_V = random.randrange(1,4)
#     B_W = random.randrange(1,4)

    
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

# procurement_price = {}
# for k in component:
#     prices = [random.randint(1, 6) for t in range(T)]
#     procurement_price[k] = prices
# df_procurement = pd.DataFrame(procurement_price)
# df_procurement.to_csv('procurement_price.csv')

# -------------------------------------------------

# Create distance matrix between each location, not all combination are used

# facilities = supplier + manu + remanu + hybrid + warehouse + collect + disassembly + recycling + disposal
# distance_table = {loc1: {loc2: 0 if loc1 == loc2 else random.randint(10, 75) for loc2 in facilities} for loc1 in facilities}
# df_distance = pd.DataFrame.from_dict(distance_table, orient='index')
# df_distance.to_csv('distance_matrix.csv')

# -------------------------------------------------

# Demand of products (new and remanufactured) at every distribution center for each period
# Values subject to change according to collected real world data

# total_demand = {}
# for i in warehouse:
#     demand = [random.randint(10, 40) * 1000 for t in range(T)]
#     total_demand[i] = demand
# df_demand = pd.DataFrame(total_demand)
# df_demand.to_csv('demand.csv', index=False)

# -------------------------------------------------

# Number of returned products at each collection center for each period
# should be between 25% and 75% of sold items (according to research)
# Values subject to change according to real world data

# total_returns = {}
# for j in collect:
#     returns = [random.randint(3, 6) * 1000 for t in range(T)]
#     total_returns[j] = returns
# df_returns = pd.DataFrame(total_returns)
# df_returns.to_csv('returns.csv', index=False)

# -------------------------------------------------

# The production capacity of every location at each period
# Values subject to change according to real world data

# cap = []
# cap_bar = []
# cap_component = []
# for t in range(T):
#     capacities = {}
#     for f in manu:
#         capacities[f] = random.randint(15,25) * 1000
#     for g in remanu:
#         capacities[g] = random.randint(8,14) * 1000
#     for h in hybrid:
#         capacities[h] = random.randint(9,15) * 1000
#     for j in collect:
#         capacities[j] = random.randint(8,15) * 1000
#     for u in disassembly:
#         capacities[u] = random.randint(10,15) * 1000
#     cap.append({**capacities})

#     capacities_bar = {}
#     for h in hybrid:
#         capacities_bar[h] = random.randint(5,10) * 1000
#     cap_bar.append({**capacities_bar})

#     capacities_comp = {}
#     for Ku in disassembly:
#         capacities_comp[Ku] = random.randint(30,50) * 300
#     for Kv in recycling:
#         capacities_comp[Kv] = random.randint(15,25) * 300
#     for Kw in disposal:
#         capacities_comp[Kw] = random.randint(15,25) * 300
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


