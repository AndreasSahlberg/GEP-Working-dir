import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

messagebox.showinfo('OnSSET', 'Open the results file')
file_path = filedialog.askopenfilename()
df = pd.read_csv(file_path)

df['Tech_Change'] = 0
df.loc[(df['FinalElecCode2023'] != df['FinalElecCode2030']) & (df['FinalElecCode2023'] == 2) & (df['FinalElecCode2030'] == 3), 'Tech_Change'] = 1
df.loc[(df['FinalElecCode2023'] != df['FinalElecCode2030']) & (df['FinalElecCode2023'] == 3) & (df['FinalElecCode2030'] == 2), 'Tech_Change'] = 1
df.loc[(df['FinalElecCode2023'] == 2) & (df['FinalElecCode2030'] > 3) & (df['FinalElecCode2030'] < 99), 'Tech_Change'] = 2
df.loc[(df['FinalElecCode2023'] == 3) & (df['FinalElecCode2030'] > 3) & (df['FinalElecCode2030'] < 99), 'Tech_Change'] = 2
df.loc[(df['FinalElecCode2023'] == 2) & (df['FinalElecCode2030'] == 1), 'Tech_Change'] = 3
df.loc[(df['FinalElecCode2023'] == 3) & (df['FinalElecCode2030'] == 1), 'Tech_Change'] = 3
df.loc[(df['FinalElecCode2023'] != df['FinalElecCode2030']) & (df['FinalElecCode2023'] > 3) & (df['FinalElecCode2023'] < 99) & (df['FinalElecCode2030'] > 3) & (df['FinalElecCode2030'] < 99), 'Tech_Change'] = 4
df.loc[(df['FinalElecCode2023'] != df['FinalElecCode2030']) & (df['FinalElecCode2023'] > 3) & (df['FinalElecCode2023'] < 99) & (df['FinalElecCode2030'] == 1), 'Tech_Change'] = 5
df.loc[(df['FinalElecCode2023'] != df['FinalElecCode2030']) & (df['FinalElecCode2023'] > 3) & (df['FinalElecCode2023'] < 99) & (df['FinalElecCode2030'] == 2), 'Tech_Change'] = 6
df.loc[(df['FinalElecCode2023'] != df['FinalElecCode2030']) & (df['FinalElecCode2023'] > 3) & (df['FinalElecCode2023'] < 99) & (df['FinalElecCode2030'] == 3), 'Tech_Change'] = 6
df.loc[(df['FinalElecCode2023'] != df['FinalElecCode2030']) & (df['FinalElecCode2023'] > 1) & (df['FinalElecCode2023'] < 99) & (df['FinalElecCode2030'] > 3) & (df['FinalElecCode2030'] < 99), 'Tech_Change'] = 7
df.loc[(df['FinalElecCode2023'] != df['FinalElecCode2030']) & (df['FinalElecCode2023'] == 1) & (df['FinalElecCode2030'] == 2), 'Tech_Change'] = 8
df.loc[(df['FinalElecCode2023'] != df['FinalElecCode2030']) & (df['FinalElecCode2023'] == 1) & (df['FinalElecCode2030'] == 3), 'Tech_Change'] = 8

df['Design_Alert'] = 0
df.loc[(df['ResultsNoTimestep'] > 3) & (df['ResultsNoTimestep'] < 99) & (df['FinalElecCode2030'] == 2), 'Design_Alert'] = 1
df.loc[(df['ResultsNoTimestep'] > 3) & (df['ResultsNoTimestep'] < 99) & (df['FinalElecCode2030'] == 3), 'Design_Alert'] = 1
df.loc[(df['ResultsNoTimestep'] == 1) & (df['FinalElecCode2030'] == 2), 'Design_Alert'] = 2
df.loc[(df['ResultsNoTimestep'] == 1) & (df['FinalElecCode2030'] == 3), 'Design_Alert'] = 2
df.loc[(df['ResultsNoTimestep'] == 1) & (df['FinalElecCode2030'] > 3) & (df['FinalElecCode2030'] < 99), 'Design_Alert'] = 3
df.loc[(df['ResultsNoTimestep'] == 2) & (df['FinalElecCode2030'] > 3) & (df['FinalElecCode2030'] < 99), 'Design_Alert'] = 4
df.loc[(df['ResultsNoTimestep'] == 3) & (df['FinalElecCode2030'] > 3) & (df['FinalElecCode2030'] < 99), 'Design_Alert'] = 4
df.loc[(df['ResultsNoTimestep'] == 2) & (df['FinalElecCode2030'] == 1), 'Design_Alert'] = 5
df.loc[(df['ResultsNoTimestep'] == 3) & (df['FinalElecCode2030'] == 1), 'Design_Alert'] = 5
df.loc[(df['ResultsNoTimestep'] > 3) & (df['ResultsNoTimestep'] < 99) & (df['FinalElecCode2030'] == 1), 'Design_Alert'] = 6

# Expected residential demand in 2023 (GWh/year)
# res_demand_2023 = sum()

# Expected residential demand in 2030 (GWh/year)
# res_demand_2023 = sum()

# Theoretical grid reach 2023 (number of people
theoretical_grid_reach_2023 = df.loc[df['GridReachYear'] < 2024, 'Pop2023'].sum()

# Actual grid reach 2023
actual_grid_reach_2023 = df.loc[df['FinalElecCode2023'] == 1, 'Pop2023'].sum()

# Theoretical grid reach 2030 (number of people
theoretical_grid_reach_2030 = df.loc[df['GridReachYear'] < 2031, 'Pop2030'].sum()

# Actual grid reach 2030
actual_grid_reach_2030 = df.loc[df['FinalElecCode2030'] == 1, 'Pop2030'].sum()

# Unelectrified 2023 (number of people)
unelectrified_2023 = df.loc[df['FinalElecCode2023'] == 99, 'Pop2023'].sum()

# Grid intensification 2023
intensification_2023 = df.loc[(df['FinalElecCode2023'] == 1) & (df['FinalElecCode2018'] == 1), 'NewConnections2023'].sum()

# Grid intensification 2030
intensification_2030 = df.loc[(df['FinalElecCode2030'] == 1) & (df['FinalElecCode2023'] == 1), 'NewConnections2030'].sum()

# Off-grid calculations 2023
off_grid_pop_2023 = df.loc[df['FinalElecCode2023'] == 2, 'NewConnections2023'].sum() + df.loc[df['FinalElecCode2023'] == 3, 'NewConnections2023'].sum() + df.loc[df['FinalElecCode2023'] == 4, 'NewConnections2023'].sum() + df.loc[df['FinalElecCode2023'] == 5, 'NewConnections2023'].sum() + df.loc[df['FinalElecCode2023'] == 6, 'NewConnections2023'].sum() + df.loc[df['FinalElecCode2023'] == 7, 'NewConnections2023'].sum()
sa_pop_2023 = df.loc[df['FinalElecCode2023'] == 2, 'NewConnections2023'].sum() + df.loc[df['FinalElecCode2023'] == 3, 'NewConnections2023'].sum()
mg_pop_2023 = df.loc[df['FinalElecCode2023'] == 4, 'NewConnections2023'].sum() + df.loc[df['FinalElecCode2023'] == 5, 'NewConnections2023'].sum() + df.loc[df['FinalElecCode2023'] == 6, 'NewConnections2023'].sum() + df.loc[df['FinalElecCode2023'] == 7, 'NewConnections2023'].sum()
sa_share_2023 = sa_pop_2023 / (sa_pop_2023 + mg_pop_2023) * 100
mg_share_2023 = 100 - sa_share_2023
sa_diesel_pop_2023 = df.loc[df['FinalElecCode2023'] == 2, 'NewConnections2023'].sum()
sa_pv_pop_2023 = df.loc[df['FinalElecCode2023'] == 3, 'NewConnections2023'].sum()
mg_diesel_pop_2023 = df.loc[df['FinalElecCode2023'] == 4, 'NewConnections2023'].sum()
mg_pv_pop_2023 = df.loc[df['FinalElecCode2023'] == 5, 'NewConnections2023'].sum()
mg_wind_pop_2023 = df.loc[df['FinalElecCode2023'] == 6, 'NewConnections2023'].sum()
mg_hydro_pop_2023 = df.loc[df['FinalElecCode2023'] == 7, 'NewConnections2023'].sum()

# Offgrid calculations 2030
off_grid_pop_2030 = off_grid_pop_2023 + df.loc[df['FinalElecCode2030'] == 2, 'NewConnections2030'].sum() + df.loc[df['FinalElecCode2030'] == 3, 'NewConnections2030'].sum() + df.loc[df['FinalElecCode2030'] == 4, 'NewConnections2030'].sum() + df.loc[df['FinalElecCode2030'] == 5, 'NewConnections2030'].sum() + df.loc[df['FinalElecCode2030'] == 6, 'NewConnections2030'].sum() + df.loc[df['FinalElecCode2030'] == 7, 'NewConnections2030'].sum()
sa_pop_2030 = df.loc[df['FinalElecCode2030'] == 2, 'NewConnections2030'].sum() + df.loc[df['FinalElecCode2030'] == 3, 'NewConnections2030'].sum()
mg_pop_2030 = df.loc[df['FinalElecCode2030'] == 4, 'NewConnections2030'].sum() + df.loc[df['FinalElecCode2030'] == 5, 'NewConnections2030'].sum() + df.loc[df['FinalElecCode2030'] == 6, 'NewConnections2030'].sum() + df.loc[df['FinalElecCode2030'] == 7, 'NewConnections2030'].sum()
sa_share_2030 = sa_pop_2030 / (sa_pop_2030 + mg_pop_2030) * 100
mg_share_2030 = 100 - sa_share_2030
sa_diesel_pop_2030 = df.loc[df['FinalElecCode2030'] == 2, 'NewConnections2030'].sum() + sa_diesel_pop_2023
sa_pv_pop_2030 = df.loc[df['FinalElecCode2030'] == 3, 'NewConnections2030'].sum() + sa_pv_pop_2023
mg_diesel_pop_2030 = df.loc[df['FinalElecCode2030'] == 4, 'NewConnections2030'].sum() + mg_diesel_pop_2023
mg_pv_pop_2030 = df.loc[df['FinalElecCode2030'] == 5, 'NewConnections2030'].sum() + mg_pv_pop_2023
mg_wind_pop_2030 = df.loc[df['FinalElecCode2030'] == 6, 'NewConnections2030'].sum() + mg_wind_pop_2023
mg_hydro_pop_2030 = df.loc[df['FinalElecCode2030'] == 7, 'NewConnections2030'].sum() + mg_hydro_pop_2023

# Total energy demand in 2023 (GWh)
df.loc[df['Actual_Elec_Status_2023'] == 1, 'TotalDemand'] = df['PerCapitaDemand'] * df['Pop2023']
total_demand_2023 = df['TotalDemand'].sum()/1000000

# Total energy demand in 2030 (GWh)
df.loc[df['Actual_Elec_Status_2030'] == 1, 'TotalDemand'] = df['PerCapitaDemand'] * df['Pop2030']
total_demand_2030 = df['TotalDemand'].sum()/1000000

messagebox.showinfo('OnSSET', 'Name the output file')
output_dir = filedialog.asksaveasfilename()
settlements_out_csv = output_dir + '.csv'
df.to_csv(settlements_out_csv, index=False)
