# Pulls all the other functions together to make magic!
#
# Author: KTH dESA Last modified by Alexandros Korkovelos
# Date: 7 March 2018
# Python version: 3.5

import os
from onsset import *
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from openpyxl import load_workbook

root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

messagebox.showinfo('OnSSET', 'Open the specs file')
specs_path = filedialog.askopenfilename()

# specs = pd.read_excel(specs_path, index_col=0)

# TODO Fix this so that it asks the user for the country I reckon.?
countries = ['Malawi'] # FIX!
# countries = str(input('countries: ')).split()
# countries = specs.index.tolist() if 'all' in countries else countries

choice = int(input('Enter 1 to split, 2 to prepare the inputs, 3 to run a scenario: '))

# TODO Do we actually need option 1 anymore? I suggest to remove it and readjust the options
if choice == 1:
    messagebox.showinfo('OnSSET', 'Open the csv file with GIS data')
    settlements_csv = filedialog.askopenfilename()
    messagebox.showinfo('OnSSET', 'Select the folder to save split countries')
    base_dir = filedialog.asksaveasfilename()

    print('\n --- Splitting --- \n')

    df = pd.read_csv(settlements_csv)

    for country in countries:
        print(country)
        df.loc[df[SET_COUNTRY] == country].to_csv(base_dir + '.csv', index=False)

elif choice == 2:
    SpecsData = pd.read_excel(specs_path, sheet_name='SpecsData')
    messagebox.showinfo('OnSSET', 'Open the file containing separated countries')
    base_dir = filedialog.askopenfilename()
    messagebox.showinfo('OnSSET', 'Browse to result folder and name the calibrated file')
    output_dir = filedialog.asksaveasfilename()

    print('\n --- Prepping --- \n')

    for country in countries:
        print(country)
        settlements_in_csv = base_dir # os.path.join(base_dir, '{}.csv'.format(country))
        settlements_out_csv = output_dir + '.csv' # os.path.join(output_dir, '{}.csv'.format(country))

        onsseter = SettlementProcessor(settlements_in_csv)

        num_people_per_hh_rural = float(SpecsData.iloc[0][SPE_NUM_PEOPLE_PER_HH_RURAL])
        num_people_per_hh_urban = float(SpecsData.iloc[0][SPE_NUM_PEOPLE_PER_HH_URBAN])

        onsseter.prepare_wtf_tier_columns(num_people_per_hh_rural, num_people_per_hh_urban)
        onsseter.condition_df(country)
        onsseter.grid_penalties()
        onsseter.calc_wind_cfs()

        pop_actual = SpecsData.loc[0, SPE_POP]
        pop_future_high = SpecsData.loc[0, SPE_POP_FUTURE + 'High']
        pop_future_low = SpecsData.loc[0, SPE_POP_FUTURE + 'Low']
        urban_current = SpecsData.loc[0, SPE_URBAN]
        urban_future = SpecsData.loc[0, SPE_URBAN_FUTURE]
        urban_cutoff = SpecsData.loc[0, SPE_URBAN_CUTOFF]
        start_year = int(SpecsData.loc[0, SPE_START_YEAR])
        end_year = int(SpecsData.loc[0, SPE_END_YEAR])
        time_step = int(SpecsData.loc[0, SPE_TIMESTEP])

        elec_actual = SpecsData.loc[0, SPE_ELEC]
        pop_cutoff = SpecsData.loc[0, SPE_POP_CUTOFF1]
        min_night_lights = SpecsData.loc[0, SPE_MIN_NIGHT_LIGHTS]
        max_grid_dist = SpecsData.loc[0, SPE_MAX_GRID_DIST]
        max_road_dist = SpecsData.loc[0, SPE_MAX_ROAD_DIST]
        pop_tot = SpecsData.loc[0, SPE_POP]
        pop_cutoff2 = SpecsData.loc[0, SPE_POP_CUTOFF2]
        dist_to_trans = SpecsData.loc[0, SPE_DIST_TO_TRANS]

        urban_cutoff, urban_modelled = onsseter.calibrate_pop_and_urban(pop_actual, pop_future_high, pop_future_low, urban_current,
                                                                        urban_future, urban_cutoff, start_year, end_year, time_step)

        min_night_lights, dist_to_trans, max_grid_dist, max_road_dist, elec_modelled, pop_cutoff, pop_cutoff2, rural_elec_ratio, urban_elec_ratio = \
            onsseter.elec_current_and_future(elec_actual, pop_cutoff, dist_to_trans, min_night_lights, max_grid_dist,
                                             max_road_dist, pop_tot, pop_cutoff2, start_year)

        onsseter.grid_reach_estimate(start_year, gridspeed=9999)

        SpecsData.loc[0, SPE_URBAN_MODELLED] = urban_modelled
        SpecsData.loc[0, SPE_URBAN_CUTOFF] = urban_cutoff
        SpecsData.loc[0, SPE_MIN_NIGHT_LIGHTS] = min_night_lights
        SpecsData.loc[0, SPE_MAX_GRID_DIST] = max_grid_dist
        SpecsData.loc[0, SPE_MAX_ROAD_DIST] = max_road_dist
        SpecsData.loc[0, SPE_ELEC_MODELLED] = elec_modelled
        SpecsData.loc[0, SPE_POP_CUTOFF1] = pop_cutoff
        SpecsData.loc[0, SPE_POP_CUTOFF2] = pop_cutoff2
        SpecsData.loc[0, 'rural_elec_ratio'] = rural_elec_ratio
        SpecsData.loc[0, 'urban_elec_ratio'] = urban_elec_ratio

        book = load_workbook(specs_path)
        writer = pd.ExcelWriter(specs_path, engine='openpyxl')
        writer.book = book
        SpecsData.to_excel(writer, sheet_name='SpecsDataCalib', index=False)
        writer.save()
        writer.close()

        # try:
        #     SpecsData.to_excel(specs_path, sheet_name='SpecsDataCalibrated')
        # except ValueError:
        #     SpecsData.to_excel(specs_path + '.xlsx', sheet_name='SpecsDataCalibrated')

        onsseter.df.to_csv(settlements_out_csv, index=False)

elif choice == 3:


    # diesel_high = True if 'y' in input('Use high diesel value? <y/n> ') else False
    diesel_high = True
    diesel_tag = 'high' if diesel_high else 'low'
    #do_combine = True if 'y' in input('Combine countries into a single file? <y/n> ') else False

    messagebox.showinfo('OnSSET', 'Open the csv file with calibrated GIS data')
    base_dir = filedialog.askopenfilename()
    messagebox.showinfo('OnSSET', 'Browse to result folder and name the scenario to save outputs')
    # output_dir = filedialog.asksaveasfilename()
    output_dir = filedialog.askdirectory()

    print('\n --- Running scenario --- \n')

    ScenarioInfo = pd.read_excel(specs_path, sheet_name='ScenarioInfo')
    Scenarios = ScenarioInfo['Scenario']
    ScenarioParameters = pd.read_excel(specs_path, sheet_name='ScenarioParameters')
    SpecsData = pd.read_excel(specs_path, sheet_name='SpecsData')

    for scenario in Scenarios:
        # create country_specs here
        print('Scenario: ' + str(scenario+1))
        countryID = SpecsData.iloc[0]['CountryCode']

        popIndex = ScenarioInfo.iloc[scenario]['Population_Growth']
        tierIndex = ScenarioInfo.iloc[scenario]['Target_electricity_consumption_level']
        fiveyearIndex = ScenarioInfo.iloc[scenario]['Electrification_target_5_years']
        gridIndex = ScenarioInfo.iloc[scenario]['Grid_electricity_generation_cost']
        pvIndex = ScenarioInfo.iloc[scenario]['SA_PV_cost']
        dieselIndex = ScenarioInfo.iloc[scenario]['Diesel_price']
        productiveIndex = ScenarioInfo.iloc[scenario]['Productive_uses_demand']
        prioIndex = ScenarioInfo.iloc[scenario]['Prioritization_algorithm']

        end_year_pop = ScenarioParameters.iloc[popIndex]['PopEndYear']
        rural_tier = ScenarioParameters.iloc[tierIndex]['RuralTargetTier']
        urban_tier = ScenarioParameters.iloc[tierIndex]['UrbanTargetTier']
        five_year_target = ScenarioParameters.iloc[fiveyearIndex]['5YearTarget']
        grid_price = ScenarioParameters.iloc[gridIndex]['GridGenerationCost']
        # TODO we shall change this. The levers shall apply percentage increaze to both MG and SA PV systems
        sa_pv_capital_cost = ScenarioParameters.iloc[pvIndex]['SA_PV_Cost']
        diesel_price = ScenarioParameters.iloc[dieselIndex]['DieselPrice']
        productive_demand = ScenarioParameters.iloc[productiveIndex]['ProductiveDemand']
        prioritization = ScenarioParameters.iloc[prioIndex]['PrioritizationAlgorithm']

        settlements_in_csv = base_dir # os.path.join(base_dir, '{}.csv'.format(country))
        # settlements_out_csv = output_dir + '.csv' # os.path.join(output_dir, '{}_{}_{}.csv'.format(country, wb_tier_urban, diesel_tag))
        settlements_out_csv = os.path.join(output_dir, '{}-1_{}_{}_{}_{}_{}_{}_{}_{}.csv'.format(countryID, popIndex, tierIndex, fiveyearIndex, gridIndex, pvIndex, dieselIndex, productiveIndex, prioIndex))
        summary_csv = os.path.join(output_dir, '{}-1_{}_{}_{}_{}_{}_{}_{}_{}_summary.csv'.format(countryID, popIndex, tierIndex, fiveyearIndex, gridIndex, pvIndex, dieselIndex, productiveIndex, prioIndex))
        # summary_csv = output_dir + 'summary.csv'

        onsseter = SettlementProcessor(settlements_in_csv)

        start_year = SpecsData.iloc[0][SPE_START_YEAR]
        end_year = SpecsData.iloc[0][SPE_END_YEAR]
        # ToDO Do we need to define the timestep like this? Isn't it better to define the years specifically at least for GEP e.g. [2023, 2030]
        time_step = SpecsData.iloc[0][SPE_TIMESTEP]

        existing_grid_cost_ratio = SpecsData.iloc[0][SPE_EXISTING_GRID_COST_RATIO]
        num_people_per_hh_rural = float(SpecsData.iloc[0][SPE_NUM_PEOPLE_PER_HH_RURAL])
        num_people_per_hh_urban = float(SpecsData.iloc[0][SPE_NUM_PEOPLE_PER_HH_URBAN])
        max_grid_extension_dist = float(SpecsData.iloc[0][SPE_MAX_GRID_EXTENSION_DIST])
        urban_elec_ratio = float(SpecsData.iloc[0]['rural_elec_ratio'])
        rural_elec_ratio = float(SpecsData.iloc[0]['urban_elec_ratio'])
        grid_cap_gen_limit = SpecsData.loc[0, 'NewGridGenerationCapacityTimestepLimit']


        Technology.set_default_values(base_year=start_year,
                                      start_year=start_year,
                                      end_year=end_year,
                                      discount_rate=0.08,
                                      # grid_cell_area=1,
                                      mv_line_cost=9000,
                                      lv_line_cost=5000,
                                      mv_line_capacity=50,
                                      lv_line_capacity=10,
                                      lv_line_max_length=30,
                                      hv_line_cost=53000,
                                      mv_line_max_length=50,
                                      hv_lv_transformer_cost=5000,
                                      mv_increase_rate=0.1)

        grid_calc = Technology(om_of_td_lines=0.03,
                               distribution_losses=float(SpecsData.iloc[0][SPE_GRID_LOSSES]),
                               connection_cost_per_hh=125,
                               base_to_peak_load_ratio=float(SpecsData.iloc[0][SPE_BASE_TO_PEAK]),
                               capacity_factor=1,
                               tech_life=30,
                               grid_capacity_investment=float(SpecsData.iloc[0][SPE_GRID_CAPACITY_INVESTMENT]),
                               grid_penalty_ratio=1,
                               grid_price=grid_price)

        mg_hydro_calc = Technology(om_of_td_lines=0.03,
                                   distribution_losses=0.05,
                                   connection_cost_per_hh=125,
                                   base_to_peak_load_ratio=1,
                                   capacity_factor=0.5,
                                   tech_life=30,
                                   capital_cost=5000,
                                   om_costs=0.02)

        mg_wind_calc = Technology(om_of_td_lines=0.03,
                                  distribution_losses=0.05,
                                  connection_cost_per_hh=125,
                                  base_to_peak_load_ratio=0.75,
                                  capital_cost=2500,
                                  om_costs=0.02,
                                  tech_life=20)

        mg_pv_calc = Technology(om_of_td_lines=0.03,
                                distribution_losses=0.05,
                                connection_cost_per_hh=125,
                                base_to_peak_load_ratio=0.9,
                                tech_life=20,
                                om_costs=0.02,
                                capital_cost=4300) # TODO This shall e changed as per below at the SAPV

        sa_pv_calc = Technology(base_to_peak_load_ratio=0.9,
                                tech_life=15,
                                om_costs=0.018,
                                capital_cost=sa_pv_capital_cost,
                                standalone=True)

        mg_diesel_calc = Technology(om_of_td_lines=0.03,
                                    distribution_losses=0.05,
                                    connection_cost_per_hh=125,
                                    base_to_peak_load_ratio=0.5,
                                    capacity_factor=0.7,
                                    tech_life=15,
                                    om_costs=0.1,
                                    efficiency=0.33,
                                    capital_cost=721,
                                    diesel_price=diesel_price,
                                    diesel_truck_consumption=33.7,
                                    diesel_truck_volume=15000)

        sa_diesel_calc = Technology(base_to_peak_load_ratio=0.5,
                                    capacity_factor=0.5,
                                    tech_life=10,
                                    om_costs=0.1,
                                    capital_cost=938,
                                    diesel_price=diesel_price,
                                    standalone=True,
                                    efficiency=0.28,
                                    diesel_truck_consumption=14,
                                    diesel_truck_volume=300)

        # Used to identify the steps and include them in the results

        ### FIRST RUN - NO TIMESTEP

        time_step = 12
        year = 2030
        eleclimits = {2030: 1}

        # eleclimit = float(input('Provide the targeted electrification rate in {}:'.format(year)))
        eleclimit = eleclimits[year]
        # investlimit = int(input('Provide the targeted investment limit (in USD) for the year {}:'.format(year)))

        onsseter.set_scenario_variables(year, num_people_per_hh_rural, num_people_per_hh_urban, time_step, start_year,
                                        urban_elec_ratio, rural_elec_ratio, urban_tier, rural_tier, end_year_pop, productive_demand)


        onsseter.calculate_off_grid_lcoes(mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc,
                                          sa_diesel_calc, year, start_year, end_year, time_step)

        if year - time_step == start_year:
            onsseter.current_mv_line_dist()

        onsseter.pre_electrification(grid_calc, grid_price, year, time_step, start_year)



        onsseter.run_elec(grid_calc, max_grid_extension_dist, year, start_year, end_year, time_step, grid_cap_gen_limit)

        onsseter.results_columns(mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc, sa_diesel_calc,
                                 grid_calc, year)

        onsseter.calculate_investments(mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc,
                       sa_diesel_calc, grid_calc, year, end_year, time_step)

        onsseter.apply_limitations(eleclimit, year, time_step, prioritization)

        onsseter.final_decision(mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc, sa_diesel_calc,
                                grid_calc, year, end_year, time_step)

        onsseter.delete_redundant_columns(year)

        ### END OF FIRST RUN

        # yearsofanalysis = list(range((start_year + time_step), end_year + 1, time_step))

        yearsofanalysis = [2023, 2030]
        eleclimits = {2023: five_year_target, 2030: 1}
        time_steps = {2023: 5, 2030: 7}

        # This is used in the calculation of summaries at the end

        elements = ["1.Population", "2.New_Connections", "3.Capacity", "4.Investment"]
        techs = ["Grid", "SA_Diesel", "SA_PV", "MG_Diesel", "MG_PV", "MG_Wind", "MG_Hydro"]

        sumtechs = []

        for element in elements:
            for tech in techs:
                sumtechs.append(element + "_" + tech)

        sumtechs.append('Min_cluster_pop_2030')
        sumtechs.append('Max_cluster_pop_2030')
        sumtechs.append('Min_cluster_area')
        sumtechs.append('Max_cluster_area')
        sumtechs.append('Min_existing_grid_dist')
        sumtechs.append('Max_existing_grid_dist')
        sumtechs.append('Min_road_dist')
        sumtechs.append('Max_road_dist')
        sumtechs.append('Min_investment_capita_cost')
        sumtechs.append('Max_investment_capita_cost')

        total_rows = len(sumtechs)

        df_summary = pd.DataFrame(columns=yearsofanalysis)

        for row in range(0, total_rows):
            df_summary.loc[sumtechs[row]] = "Nan"

        onsseter.current_mv_line_dist()

        for year in yearsofanalysis:

            #eleclimit = float(input('Provide the targeted electrification rate in {}:'.format(year)))
            eleclimit = eleclimits[year]
            time_step = time_steps[year]
            #investlimit = int(input('Provide the targeted investment limit (in USD) for the year {}:'.format(year)))


            onsseter.set_scenario_variables(year, num_people_per_hh_rural, num_people_per_hh_urban, time_step,
                                            start_year, urban_elec_ratio, rural_elec_ratio, urban_tier, rural_tier, end_year_pop, productive_demand)

            onsseter.calculate_off_grid_lcoes(mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc, sa_diesel_calc, year, start_year, end_year, time_step)

            onsseter.pre_electrification(grid_calc, grid_price, year, time_step, start_year)

            onsseter.run_elec(grid_calc, max_grid_extension_dist, year, start_year, end_year, time_step, grid_cap_gen_limit)


            onsseter.results_columns(mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc, sa_diesel_calc, grid_calc, year)

            onsseter.calculate_investments(mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc,
                                           sa_diesel_calc, grid_calc, year, end_year, time_step)

            onsseter.apply_limitations(eleclimit, year, time_step, prioritization)

            onsseter.final_decision(mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc, sa_diesel_calc, grid_calc, year, end_year, time_step)

            onsseter.calc_summaries(df_summary, sumtechs, year)

        df_summary.to_csv(summary_csv, index=sumtechs)
        onsseter.df.to_csv(settlements_out_csv, index=False)