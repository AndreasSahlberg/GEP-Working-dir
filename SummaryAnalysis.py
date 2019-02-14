import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

messagebox.showinfo('OnSSET', 'Open the specs file')
scenarios_path = filedialog.askopenfilename()

ScenarioInfo = pd.read_excel(scenarios_path)
Scenarios = ScenarioInfo['Scenario']
countryID = 'mw'

Summary_comparison = []
Summary_comparison.append('Scenario_code') # 0
Summary_comparison.append('PopLever') #1
Summary_comparison.append('Target_tier_lever')  # 2
Summary_comparison.append('5_year_target_lever')  # 3
Summary_comparison.append('Grid_cost_lever')  # 4
Summary_comparison.append('PV_cost_lever')  # 5
Summary_comparison.append('Diesel_price_lever')  # 6

Summary_comparison.append('Total_investment_cost')  # 7
Summary_comparison.append('Investment_cost_grid_2030')  # 8
Summary_comparison.append('Investment_cost_MG_2030')  # 9
Summary_comparison.append('Investment_cost_SA_2030')  # 10
Summary_comparison.append('Population_grid_2030')  # 11
Summary_comparison.append('Population_MG_2030')  # 12
Summary_comparison.append('Population_SA_2030')  # 13
Summary_comparison.append('Capacity_requirements_2030')  # 14
Summary_comparison.append('Capacity_grid_2030')  # 15
Summary_comparison.append('Capacity_MG_2030')  # 16
Summary_comparison.append('Capacity_SA_2030')  # 17

total_rows = len(Summary_comparison)
total_col = list(range(96))
df_summary = pd.DataFrame(columns=total_col)

for row in range(0, total_rows):
    df_summary.loc[Summary_comparison[row]] = "Nan"

elements = ["1.Population", "2.New_Connections", "3.Capacity", "4.Investment"]
techs = ["Grid", "SA_Diesel", "SA_PV", "MG_Diesel", "MG_PV", "MG_Wind", "MG_Hydro"]
years = ['2023', '2030']

for scenario in Scenarios:
    popIndex = ScenarioInfo.iloc[scenario]['Population_Growth']
    tierIndex = ScenarioInfo.iloc[scenario]['Target_electricity_consumption_level']
    fiveyearIndex = ScenarioInfo.iloc[scenario]['Electrification_target_5_years']
    gridIndex = ScenarioInfo.iloc[scenario]['Grid_electricity_generation_cost']
    pvIndex = ScenarioInfo.iloc[scenario]['PV_cost_adjust']
    dieselIndex = ScenarioInfo.iloc[scenario]['Diesel_price']
    productiveIndex = ScenarioInfo.iloc[scenario]['Productive_uses_demand']
    prioIndex = ScenarioInfo.iloc[scenario]['Prioritization_algorithm']

    summary_csv = os.path.join('{}-1_{}_{}_{}_{}_{}_{}_{}_{}_summary.csv'.format(countryID, popIndex, tierIndex,fiveyearIndex, gridIndex, pvIndex,dieselIndex, productiveIndex,prioIndex))
    summary = pd.read_csv(summary_csv, index_col=0)

    total_cost = 0
    total_capacity = 0

    for year in years:
        for tech in techs:
            total_cost += summary[year]["4.Investment" + "_" + tech] / 1000000
            total_capacity += summary[year]["3.Capacity" + "_" + tech] / 1000

    investment_cost_grid = 0
    investment_cost_MG = 0
    investment_cost_SA = 0
    capacity_grid = 0
    capacity_MG = 0
    capacity_SA = 0
    techs = ["Grid", "SA_Diesel", "SA_PV", "MG_Diesel", "MG_PV", "MG_Wind", "MG_Hydro"]
    for year in years:
        investment_cost_grid += summary[year]["4.Investment" + "_" + "Grid"] / 1000000
        capacity_grid += summary[year]["3.Capacity" + "_" + "Grid"] / 1000
        investment_cost_MG += summary[year]["4.Investment" + "_" + "MG_Diesel"] / 1000000
        investment_cost_MG += summary[year]["4.Investment" + "_" + "MG_PV"] / 1000000
        investment_cost_MG += summary[year]["4.Investment" + "_" + "MG_Wind"] / 1000000
        investment_cost_MG += summary[year]["4.Investment" + "_" + "MG_Hydro"] / 1000000
        investment_cost_SA += summary[year]["4.Investment" + "_" + "SA_Diesel"] / 1000000
        investment_cost_SA += summary[year]["4.Investment" + "_" + "SA_PV"] / 1000000
        capacity_MG += summary[year]["3.Capacity" + "_" + "MG_Diesel"] / 1000
        capacity_MG += summary[year]["3.Capacity" + "_" + "MG_PV"] / 1000
        capacity_MG += summary[year]["3.Capacity" + "_" + "MG_Wind"] / 1000
        capacity_MG += summary[year]["3.Capacity" + "_" + "MG_Hydro"] / 1000
        capacity_SA += summary[year]["3.Capacity" + "_" + "SA_Diesel"] / 1000
        capacity_SA += summary[year]["3.Capacity" + "_" + "SA_PV"] / 1000
        # pop_grid += summary[year]["1.Population"]

    pop_grid = summary["2030"]["1.Population_Grid"]
    pop_MG = summary["2030"]["1.Population_MG_Diesel"] + summary["2030"]["1.Population_MG_PV"] + summary["2030"]["1.Population_MG_Wind"] + summary["2030"]["1.Population_MG_Hydro"]
    pop_sa = summary["2030"]["1.Population_SA_Diesel"] + summary["2030"]["1.Population_SA_PV"]

    df_summary[scenario][0] = summary_csv
    df_summary[scenario][1] = popIndex
    df_summary[scenario][2] = tierIndex
    df_summary[scenario][3] = fiveyearIndex
    df_summary[scenario][4] = gridIndex
    df_summary[scenario][5] = pvIndex
    df_summary[scenario][6] = dieselIndex

    df_summary[scenario][7] = total_cost
    df_summary[scenario][8] = investment_cost_grid
    df_summary[scenario][9] = investment_cost_MG
    df_summary[scenario][10] = investment_cost_SA
    df_summary[scenario][11] = pop_grid
    df_summary[scenario][12] = pop_MG
    df_summary[scenario][13] = pop_sa
    df_summary[scenario][14] = total_capacity
    df_summary[scenario][15] = capacity_grid
    df_summary[scenario][16] = capacity_MG
    df_summary[scenario][17] = capacity_SA

df_summary.to_csv('SummariesComparison.csv', index=Summary_comparison)