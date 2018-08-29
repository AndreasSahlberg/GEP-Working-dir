# Author: KTH dESA Last modified by Alexandros Korkovelos
# Date: 7 March 2018
# Python version: 3.5

import os
import logging
import pandas as pd
from math import ceil, pi, exp, log, sqrt
from pyproj import Proj
import numpy as np
from collections import defaultdict

logging.basicConfig(format='%(asctime)s\t\t%(message)s', level=logging.DEBUG)

# general
LHV_DIESEL = 9.9445485  # (kWh/l) lower heating value
HOURS_PER_YEAR = 8760

# Columns in settlements file must match these exactly
SET_COUNTRY = 'Country'  # This cannot be changed, lots of code will break
SET_X = 'X'  # Coordinate in kilometres
SET_Y = 'Y'  # Coordinate in kilometres
SET_X_DEG = 'X_deg'  # Coordinates in degrees
SET_Y_DEG = 'Y_deg'
SET_POP = 'Pop'  # Population in people per point (equally, people per km2)
SET_POP_CALIB = 'PopStartYear'  # Calibrated population to reference year, same units
SET_POP_FUTURE = 'PopEndYear'  # Project future population, same units
SET_GRID_DIST_CURRENT = 'GridDistCurrent'  # Distance in km from current grid
SET_GRID_DIST_PLANNED = 'GridDistPlan'  # Distance in km from current and future grid
SET_ROAD_DIST = 'RoadDist'  # Distance in km from road network
SET_NIGHT_LIGHTS = 'NightLights'  # Intensity of night time lights (from NASA), range 0 - 63
SET_TRAVEL_HOURS = 'TravelHours'  # Travel time to large city in hours
SET_GHI = 'GHI'  # Global horizontal irradiance in kWh/m2/day
SET_WINDVEL = 'WindVel' # Wind velocity in m/s
SET_WINDCF = 'WindCF'  # Wind capacity factor as percentage (range 0 - 1)
SET_HYDRO = 'Hydropower'  # Hydropower potential in kW
SET_HYDRO_DIST = 'HydropowerDist'  # Distance to hydropower site in km
SET_HYDRO_FID = 'HydropowerFID'  # the unique tag for eah hydropower, to not over-utilise
SET_SUBSTATION_DIST = 'SubstationDist'
SET_ELEVATION = 'Elevation'  # in metres
SET_SLOPE = 'Slope'  # in degrees
SET_LAND_COVER = 'LandCover'
SET_SOLAR_RESTRICTION = 'SolarRestriction'
SET_ROAD_DIST_CLASSIFIED = 'RoadDistClassified'
SET_SUBSTATION_DIST_CLASSIFIED = 'SubstationDistClassified'
SET_ELEVATION_CLASSIFIED = 'ElevationClassified'
SET_SLOPE_CLASSIFIED = 'SlopeClassified'
SET_LAND_COVER_CLASSIFIED = 'LandCoverClassified'
SET_COMBINED_CLASSIFICATION = 'GridClassification'
SET_GRID_PENALTY = 'GridPenalty'
SET_URBAN = 'IsUrban'  # Whether the site is urban (0 or 1)
SET_ENERGY_PER_CELL = 'EnergyPerSettlement'
SET_NUM_PEOPLE_PER_HH = 'NumPeoplePerHH'
SET_ELEC_CURRENT = 'ElecStart'  # If the site is currently electrified (0 or 1)
SET_ELEC_FUTURE = 'Elec_Status'  # If the site has the potential to be 'easily' electrified in future
SET_ELEC_FUTURE_GRID = "Elec_Initial_Status_Grid"
SET_ELEC_FUTURE_OFFGRID = "Elec_Init_Status_Offgrid"
SET_ELEC_FUTURE_ACTUAL = "Actual_Elec_Status_"
SET_ELEC_FINAL_GRID = "GridElecIn"
SET_ELEC_FINAL_OFFGRID = "OffGridElecIn"
SET_NEW_CONNECTIONS = 'NewConnections'  # Number of new people with electricity connections
SET_MIN_GRID_DIST = 'MinGridDist'
SET_LCOE_GRID = 'Grid_extension'  # All lcoes in USD/kWh
SET_LCOE_SA_PV = 'SA_PV'
SET_LCOE_SA_DIESEL = 'SA_Diesel'
SET_LCOE_MG_WIND = 'MG_Wind'
SET_LCOE_MG_DIESEL = 'MG_Diesel'
SET_LCOE_MG_PV = 'MG_PV'
SET_LCOE_MG_HYDRO = 'MG_Hydro'
SET_GRID_LCOE_Round1 = "Grid_lcoe_PreElec"
SET_MIN_OFFGRID = 'Minimum_Tech_Off_grid'  # The technology with lowest lcoe (excluding grid)
SET_MIN_OVERALL = 'MinimumOverall'  # Same as above, but including grid
SET_MIN_OFFGRID_LCOE = 'Minimum_LCOE_Off_grid'  # The lcoe value for minimum tech
SET_MIN_OVERALL_LCOE = 'MinimumOverallLCOE'  # The lcoe value for overall minimum
SET_MIN_OVERALL_CODE = 'MinimumOverallCode'  # And a code from 1 - 7 to represent that option
SET_MIN_CATEGORY = 'MinimumCategory'  # The category with minimum lcoe (grid, minigrid or standalone)
SET_NEW_CAPACITY = 'NewCapacity'  # Capacity in kW
SET_INVESTMENT_COST = 'InvestmentCost'  # The investment cost in USD
SET_INVESTMENT_COST_OFFGRID = "InvestmentOffGrid"
SET_CONFLICT = "Conflict"
SET_ELEC_ORDER = "ElectrificationOrder"
SET_DYNAMIC_ORDER = "Electrification_Wave"
SET_LIMIT = "ElecStatusIn"
SET_GRID_REACH_YEAR = "GridReachYear"
SET_MIN_OFFGRID_CODE = "Off_Grid_Code"
SET_ELEC_FINAL_CODE = "FinalElecCode"
SET_DIST_TO_TRANS = "TransformerDist"
SET_TOTAL_ENERGY_PER_CELL = "TotalEnergyPerCell"  # all previous + current timestep


# Columns in the specs file must match these exactly
SPE_COUNTRY = 'Country'
SPE_POP = 'PopStartYear'  # The actual population in the base year
SPE_URBAN = 'UrbanRatioStartYear'  # The ratio of urban population (range 0 - 1) in base year
SPE_POP_FUTURE = 'PopEndYear'
SPE_URBAN_FUTURE = 'UrbanRatioEndYear'
SPE_URBAN_MODELLED = 'UrbanRatioModelled'  # The urban ratio in the model after calibration (for comparison)
SPE_URBAN_CUTOFF = 'UrbanCutOff'  # The urban cutoff population calirated by the model, in people per km2
SPE_URBAN_GROWTH = 'UrbanGrowth'  # The urban growth rate as a simple multplier (urban pop future / urban pop present)
SPE_RURAL_GROWTH = 'RuralGrowth'  # Same as for urban
SPE_NUM_PEOPLE_PER_HH_RURAL = 'NumPeoplePerHHRural'
SPE_NUM_PEOPLE_PER_HH_URBAN = 'NumPeoplePerHHUrban'
SPE_DIESEL_PRICE_LOW = 'DieselPriceLow'  # Diesel price in USD/litre
SPE_DIESEL_PRICE_HIGH = 'DieselPriceHigh'  # Same, with a high forecast var
SPE_GRID_PRICE = 'GridPrice'  # Grid price of electricity in USD/kWh
SPE_GRID_CAPACITY_INVESTMENT = 'GridCapacityInvestmentCost'  # grid capacity investments costs from TEMBA USD/kW
SPE_GRID_LOSSES = 'GridLosses'  # As a ratio (0 - 1)
SPE_BASE_TO_PEAK = 'BaseToPeak'  # As a ratio (0 - 1)
SPE_EXISTING_GRID_COST_RATIO = 'ExistingGridCostRatio'
SPE_MAX_GRID_DIST = 'MaxGridDist'
SPE_ELEC = 'ElecActual'  # Actual current percentage electrified population (0 - 1)
SPE_ELEC_MODELLED = 'ElecModelled'  # The modelled version after calibration (for comparison)
SPE_MIN_NIGHT_LIGHTS = 'MinNightLights'
SPE_MAX_GRID_EXTENSION_DIST = 'MaxGridExtensionDist'
SPE_MAX_ROAD_DIST = 'MaxRoadDist'
SPE_POP_CUTOFF1 = 'PopCutOffRoundOne'
SPE_POP_CUTOFF2 = 'PopCutOffRoundTwo'
SPE_CAP_COST_MG_PV = "Cap_Cost_MG_PV"
SPE_ELEC_LIMIT = "ElecLimit"
SPE_INVEST_LIMIT ="InvestmentLimit"
SPE_DIST_TO_TRANS = "DistToTrans"

SPE_START_YEAR = "StartYear"
SPE_END_YEAR = "EndYEar"
SPE_TIMESTEP = "TimeStep"

class Technology:
    """
    Used to define the parameters for each electricity access technology, and to calculate the LCOE depending on
    input parameters.
    """

    #start_year = 2015
    #end_year = 2030
    discount_rate = 0.08
    grid_cell_area = 0.01  # in km2, normally 1km2

    mv_line_cost = 9000  # USD/km
    lv_line_cost = 5000  # USD/km
    mv_line_capacity = 50  # kW/line
    lv_line_capacity = 10  # kW/line
    lv_line_max_length = 30  # km
    hv_line_cost = 120000  # USD/km
    mv_line_max_length = 50  # km
    hv_lv_transformer_cost = 3500  # USD/unit
    mv_increase_rate = 0.1  # percentage
    existing_grid_cost_ratio = 0.1 # percentage

    def __init__(self,
                 tech_life,  # in years
                 base_to_peak_load_ratio,
                 distribution_losses=0,  # percentage
                 connection_cost_per_hh=0,  # USD/hh
                 om_costs=0.0,  # OM costs as percentage of capital costs
                 capital_cost=0,  # USD/kW
                 capacity_factor=0.9,  # percentage
                 grid_penalty_ratio=1,  # multiplier
                 efficiency=1.0,  # percentage
                 diesel_price=0.0,  # USD/litre
                 grid_price=0.0,  # USD/kWh for grid electricity
                 standalone=False,
                 existing_grid_cost_ratio=0.1,  # percentage
                 grid_capacity_investment=0.0,  # USD/kW for on-grid capacity investments (excluding grid itself)
                 diesel_truck_consumption=0,  # litres/hour
                 diesel_truck_volume=0,  # litres
                 om_of_td_lines=0):  # percentage

        self.distribution_losses = distribution_losses
        self.connection_cost_per_hh = connection_cost_per_hh
        self.base_to_peak_load_ratio = base_to_peak_load_ratio
        self.tech_life = tech_life
        self.om_costs = om_costs
        self.capital_cost = capital_cost
        self.capacity_factor = capacity_factor
        self.grid_penalty_ratio = grid_penalty_ratio
        self.efficiency = efficiency
        self.diesel_price = diesel_price
        self.grid_price = grid_price
        self.standalone = standalone
        self.existing_grid_cost_ratio = existing_grid_cost_ratio
        self.grid_capacity_investment = grid_capacity_investment
        self.diesel_truck_consumption = diesel_truck_consumption
        self.diesel_truck_volume = diesel_truck_volume
        self.om_of_td_lines = om_of_td_lines

    @classmethod
    def set_default_values(cls, start_year, end_year, discount_rate, grid_cell_area, mv_line_cost, lv_line_cost,
                           mv_line_capacity, lv_line_capacity, lv_line_max_length, hv_line_cost, mv_line_max_length,
                           hv_lv_transformer_cost, mv_increase_rate):
        cls.start_year = start_year
        cls.end_year = end_year
        cls.discount_rate = discount_rate
        cls.grid_cell_area = grid_cell_area
        cls.mv_line_cost = mv_line_cost
        cls.lv_line_cost = lv_line_cost
        cls.mv_line_capacity = mv_line_capacity
        cls.lv_line_capacity = lv_line_capacity
        cls.lv_line_max_length = lv_line_max_length
        cls.hv_line_cost = hv_line_cost
        cls.mv_line_max_length = mv_line_max_length
        cls.hv_lv_transformer_cost = hv_lv_transformer_cost
        cls.mv_increase_rate = mv_increase_rate

    def get_lcoe(self, energy_per_cell, people, num_people_per_hh, start_year, end_year, new_connections, total_energy_per_cell, prev_code, conflict_status=0, additional_mv_line_length=0, capacity_factor=0, grid_penalty_ratio=1,
                 mv_line_length=0, travel_hours=0, elec_loop = 0, get_investment_cost=False):
        """
        Calculates the LCOE depending on the parameters. Optionally calculates the investment cost instead.

        The only required parameters are energy_per_cell, people and num_people_per_hh
        additional_mv_line_length required for grid
        capacity_factor required for PV and wind
        mv_line_length required for hydro
        travel_hours required for diesel
        """

        if people == 0:
            # If there are no people, the investment cost is zero.
            if get_investment_cost:
                return 0
            # Otherwise we set the people low (prevent div/0 error) and continue.
            else:
                people = 0.00001

        if energy_per_cell == 0:
            # If there is no demand, the investment cost is zero.
            if get_investment_cost:
                return 0
            # Otherwise we set the people low (prevent div/0 error) and continue.
            else:
                energy_per_cell = 0.000000000001

        if grid_penalty_ratio == 0:
            grid_penalty_ratio = self.grid_penalty_ratio

        # If a new capacity factor isn't given, use the class capacity factor (for hydro, diesel etc)
        if capacity_factor == 0:
            capacity_factor = self.capacity_factor

        def distribution_network(people, energy_per_cell):
            if energy_per_cell <= 0:
                energy_per_cell = 0.0001
            if people <= 0:
                people = 0.0001

            consumption = energy_per_cell # kWh/year
            average_load = consumption / (1 - self.distribution_losses) / HOURS_PER_YEAR  # kW
            peak_load = average_load / self.base_to_peak_load_ratio  # kW

            no_mv_lines = peak_load / self.mv_line_capacity
            no_lv_lines = peak_load / self.lv_line_capacity
            lv_networks_lim_capacity = no_lv_lines / no_mv_lines
            lv_networks_lim_length = ((self.grid_cell_area / no_mv_lines) / (self.lv_line_max_length / sqrt(2))) ** 2
            actual_lv_lines = min([people / num_people_per_hh, max([lv_networks_lim_capacity, lv_networks_lim_length])])
            hh_per_lv_network = (people / num_people_per_hh) / (actual_lv_lines * no_mv_lines)
            lv_unit_length = sqrt(self.grid_cell_area / (people / num_people_per_hh)) * sqrt(2) / 2
            lv_lines_length_per_lv_network = 1.333 * hh_per_lv_network * lv_unit_length
            total_lv_lines_length = no_mv_lines * actual_lv_lines * lv_lines_length_per_lv_network
            line_reach = (self.grid_cell_area / no_mv_lines) / (2 * sqrt(self.grid_cell_area / no_lv_lines))
            total_length_of_lines = min([line_reach, self.mv_line_max_length]) * no_mv_lines
            additional_hv_lines = max([0, round(sqrt(self.grid_cell_area) / (2 * min([line_reach, self.mv_line_max_length])) / 10, 3) - 1])
            hv_lines_total_length = (sqrt(self.grid_cell_area) / 2) * additional_hv_lines * sqrt(self.grid_cell_area)
            num_transformers = additional_hv_lines + no_mv_lines + (no_mv_lines * actual_lv_lines)
            generation_per_year = average_load * HOURS_PER_YEAR
            return hv_lines_total_length, total_length_of_lines, total_lv_lines_length, num_transformers, generation_per_year, peak_load

        if people != new_connections and (prev_code == 1 or prev_code == 4 or prev_code == 5 or prev_code == 6 or prev_code == 7):
            hv_lines_total_length1, total_length_of_lines1, total_lv_lines_length1, \
            num_transformers1, generation_per_year1, peak_load1 = distribution_network(people, total_energy_per_cell)

            hv_lines_total_length2, total_length_of_lines2, total_lv_lines_length2, \
            num_transformers2, generation_per_year2, peak_load2 = distribution_network(people=(people - new_connections),
                                                                           energy_per_cell=(total_energy_per_cell - energy_per_cell))
            hv_lines_total_length = hv_lines_total_length1 - hv_lines_total_length2
            total_length_of_lines = total_length_of_lines1 - total_length_of_lines2
            total_lv_lines_length = total_lv_lines_length1 - total_lv_lines_length2
            num_transformers = num_transformers1 - num_transformers2
            generation_per_year = generation_per_year1 - generation_per_year2
            peak_load = peak_load1 - peak_load2
        else:
            hv_lines_total_length, total_length_of_lines, total_lv_lines_length, \
            num_transformers, generation_per_year, peak_load = distribution_network(people, energy_per_cell)

        # The investment and O&M costs are different for grid and non-grid solutions
        if self.grid_price > 0:
            if conflict_status == 1:
                td_investment_cost = hv_lines_total_length * (self.hv_line_cost * 1.1)+ \
                                 total_length_of_lines * (self.mv_line_cost * 1.1) + \
                                 total_lv_lines_length * (self.lv_line_cost * 1.1) + \
                                 num_transformers * self.hv_lv_transformer_cost + \
                                 (people / num_people_per_hh) * self.connection_cost_per_hh + \
                                 additional_mv_line_length * ((self.mv_line_cost * 1.1) * \
                                                              (1 + self.mv_increase_rate)**((additional_mv_line_length/5)-1))
                td_investment_cost = td_investment_cost * grid_penalty_ratio
                td_om_cost = td_investment_cost * (self.om_of_td_lines * 1.1)
                if elec_loop > 0:
                    total_investment_cost = td_investment_cost * (self.existing_grid_cost_ratio * elec_loop)  # Should be 1+existing_grid_cost_ratio?
                    total_om_cost = td_om_cost * (self.existing_grid_cost_ratio * elec_loop)
                    fuel_cost = self.grid_price
                else:
                    total_investment_cost = td_investment_cost
                    total_om_cost = td_om_cost
                    fuel_cost = self.grid_price

            elif conflict_status == 2:
                td_investment_cost = hv_lines_total_length * (self.hv_line_cost * 1.25) + \
                                     total_length_of_lines * (self.mv_line_cost * 1.25) + \
                                     total_lv_lines_length * (self.lv_line_cost * 1.25) + \
                                     num_transformers * self.hv_lv_transformer_cost + \
                                     (people / num_people_per_hh) * self.connection_cost_per_hh + \
                                     additional_mv_line_length * ((self.mv_line_cost * 1.25) * \
                                                                  (1 + self.mv_increase_rate) ** (
                                                                  (additional_mv_line_length / 5) - 1))
                td_investment_cost = td_investment_cost * grid_penalty_ratio
                td_om_cost = td_investment_cost * (self.om_of_td_lines * 1.25)
                if elec_loop > 0:
                    total_investment_cost = td_investment_cost * (self.existing_grid_cost_ratio * elec_loop)
                    total_om_cost = td_om_cost * (self.existing_grid_cost_ratio * elec_loop)
                    fuel_cost = self.grid_price
                else:
                    total_investment_cost = td_investment_cost
                    total_om_cost = td_om_cost
                    fuel_cost = self.grid_price

            elif conflict_status == 3:
                td_investment_cost = hv_lines_total_length * (self.hv_line_cost * 1.5) + \
                                     total_length_of_lines * (self.mv_line_cost * 1.5) + \
                                     total_lv_lines_length * (self.lv_line_cost * 1.5) + \
                                     num_transformers * self.hv_lv_transformer_cost + \
                                     (people / num_people_per_hh) * self.connection_cost_per_hh + \
                                     additional_mv_line_length * ((self.mv_line_cost * 1.5) * \
                                                                  (1 + self.mv_increase_rate) ** (
                                                                  (additional_mv_line_length / 5) - 1))
                td_investment_cost = td_investment_cost * grid_penalty_ratio
                td_om_cost = td_investment_cost * (self.om_of_td_lines * 1.5)
                if elec_loop > 0:
                    total_investment_cost = td_investment_cost * (self.existing_grid_cost_ratio * elec_loop)
                    total_om_cost = td_om_cost * (self.existing_grid_cost_ratio * elec_loop)
                    fuel_cost = self.grid_price
                else:
                    total_investment_cost = td_investment_cost
                    total_om_cost = td_om_cost
                    fuel_cost = self.grid_price

            elif conflict_status == 4:
                td_investment_cost = hv_lines_total_length * (self.hv_line_cost * 2) + \
                                     total_length_of_lines * (self.mv_line_cost * 2) + \
                                     total_lv_lines_length * (self.lv_line_cost * 2) + \
                                     num_transformers * self.hv_lv_transformer_cost + \
                                     (people / num_people_per_hh) * self.connection_cost_per_hh + \
                                     additional_mv_line_length * ((self.mv_line_cost * 2) * \
                                                                  (1 + self.mv_increase_rate) ** (
                                                                  (additional_mv_line_length / 5) - 1))
                td_investment_cost = td_investment_cost * grid_penalty_ratio
                td_om_cost = td_investment_cost * (self.om_of_td_lines * 2)
                if elec_loop > 0:
                    total_investment_cost = td_investment_cost * (self.existing_grid_cost_ratio * elec_loop)
                    total_om_cost = td_om_cost * (self.existing_grid_cost_ratio * elec_loop)
                    fuel_cost = self.grid_price
                else:
                    total_investment_cost = td_investment_cost
                    total_om_cost = td_om_cost
                    fuel_cost = self.grid_price
            else:
                td_investment_cost = hv_lines_total_length * self.hv_line_cost * (1 + self.existing_grid_cost_ratio * elec_loop) + \
                                     total_length_of_lines * self.mv_line_cost * (1 + self.existing_grid_cost_ratio * elec_loop) + \
                                     total_lv_lines_length * self.lv_line_cost + \
                                     num_transformers * self.hv_lv_transformer_cost + \
                                     (people / num_people_per_hh) * self.connection_cost_per_hh + \
                                     (1 + self.existing_grid_cost_ratio * elec_loop) * additional_mv_line_length * (
                                         self.mv_line_cost * (1 + self.mv_increase_rate) **
                                         ((additional_mv_line_length / 5) - 1))
                td_investment_cost = td_investment_cost * grid_penalty_ratio
                td_om_cost = td_investment_cost * self.om_of_td_lines
                if elec_loop > 0:
                    total_investment_cost = td_investment_cost # * (1 + self.existing_grid_cost_ratio * elec_loop)
                    total_om_cost = td_om_cost # * (1 + self.existing_grid_cost_ratio * elec_loop)
                    fuel_cost = self.grid_price
                else:
                    total_investment_cost = td_investment_cost
                    total_om_cost = td_om_cost
                    fuel_cost = self.grid_price

        else:
            if conflict_status == 1:
                total_lv_lines_length *= 0 if self.standalone else 0.75
                mv_total_line_cost = self.mv_line_cost * mv_line_length * 1.03 if self.standalone else self.mv_line_cost * mv_line_length * 1.05
                lv_total_line_cost = self.lv_line_cost * total_lv_lines_length * 1.03 if self.standalone else self.lv_line_cost * total_lv_lines_length * 1.05
                installed_capacity = peak_load / capacity_factor
                capital_investment = installed_capacity * self.capital_cost * 1.03 if self.standalone else installed_capacity * self.capital_cost * 1.05
                td_investment_cost = mv_total_line_cost + lv_total_line_cost + (people / num_people_per_hh) * self.connection_cost_per_hh
                td_om_cost = td_investment_cost * self.om_of_td_lines * 1.03 if self.standalone else td_investment_cost * self.om_of_td_lines * 1.05
                total_investment_cost = td_investment_cost + capital_investment
                total_om_cost = td_om_cost + (self.capital_cost * 1.03 * self.om_costs * 1.03 * installed_capacity) if self.standalone else td_om_cost + (self.capital_cost * 1.05 * self.om_costs * 1.05 * installed_capacity)

            elif conflict_status == 2:
                total_lv_lines_length *= 0 if self.standalone else 0.75
                mv_total_line_cost = self.mv_line_cost * mv_line_length * 1.07 if self.standalone else self.mv_line_cost * mv_line_length * 1.125
                lv_total_line_cost = self.lv_line_cost * total_lv_lines_length * 1.07 if self.standalone else self.lv_line_cost * total_lv_lines_length * 1.125
                installed_capacity = peak_load / capacity_factor
                capital_investment = installed_capacity * self.capital_cost * 1.07 if self.standalone else installed_capacity * self.capital_cost * 1.125
                td_investment_cost = mv_total_line_cost + lv_total_line_cost + (people / num_people_per_hh) * self.connection_cost_per_hh
                td_om_cost = td_investment_cost * self.om_of_td_lines * 1.07 if self.standalone else td_investment_cost * self.om_of_td_lines * 1.125
                total_investment_cost = td_investment_cost + capital_investment
                total_om_cost = td_om_cost + (self.capital_cost * 1.07 * self.om_costs * 1.07 * installed_capacity) if self.standalone else td_om_cost + (self.capital_cost * 1.125 * self.om_costs * 1.125 * installed_capacity)

            elif conflict_status == 3:
                total_lv_lines_length *= 0 if self.standalone else 0.75
                mv_total_line_cost = self.mv_line_cost * mv_line_length * 1.125 if self.standalone else self.mv_line_cost * mv_line_length * 1.25
                lv_total_line_cost = self.lv_line_cost * total_lv_lines_length * 1.125 if self.standalone else self.lv_line_cost * total_lv_lines_length * 1.25
                installed_capacity = peak_load / capacity_factor
                capital_investment = installed_capacity * self.capital_cost * 1.125 if self.standalone else installed_capacity * self.capital_cost * 1.25
                td_investment_cost = mv_total_line_cost + lv_total_line_cost + (people / num_people_per_hh) * self.connection_cost_per_hh
                td_om_cost = td_investment_cost * self.om_of_td_lines * 1.125 if self.standalone else td_investment_cost * self.om_of_td_lines * 1.25
                total_investment_cost = td_investment_cost + capital_investment
                total_om_cost = td_om_cost + (self.capital_cost * 1.125 * self.om_costs * 1.125 * installed_capacity) if self.standalone else td_om_cost + (self.capital_cost * 1.25 * self.om_costs * 1.25 * installed_capacity)

            elif conflict_status == 4:
                total_lv_lines_length *= 0 if self.standalone else 0.75
                mv_total_line_cost = self.mv_line_cost * mv_line_length * 1.25 if self.standalone else self.mv_line_cost * mv_line_length * 1.5
                lv_total_line_cost = self.lv_line_cost * total_lv_lines_length * 1.25 if self.standalone else self.lv_line_cost * total_lv_lines_length * 1.5
                installed_capacity = peak_load / capacity_factor
                capital_investment = installed_capacity * self.capital_cost * 1.25 if self.standalone else installed_capacity * self.capital_cost * 1.5
                td_investment_cost = mv_total_line_cost + lv_total_line_cost + (people / num_people_per_hh) * self.connection_cost_per_hh
                td_om_cost = td_investment_cost * self.om_of_td_lines * 1.25 if self.standalone else td_investment_cost * self.om_of_td_lines * 1.5
                total_investment_cost = td_investment_cost + capital_investment
                total_om_cost = td_om_cost + (self.capital_cost * 1.25 * self.om_costs * 1.25 * installed_capacity) if self.standalone else td_om_cost + (self.capital_cost * 1.5 * self.om_costs * 1.5 * installed_capacity)

            else:
                total_lv_lines_length *= 0 if self.standalone else 0.75
                mv_total_line_cost = self.mv_line_cost * mv_line_length
                lv_total_line_cost = self.lv_line_cost * total_lv_lines_length
                installed_capacity = peak_load / capacity_factor
                capital_investment = installed_capacity * self.capital_cost
                td_investment_cost = mv_total_line_cost + lv_total_line_cost + (people / num_people_per_hh) * self.connection_cost_per_hh
                td_om_cost = td_investment_cost * self.om_of_td_lines
                total_investment_cost = td_investment_cost + capital_investment
                total_om_cost = td_om_cost + (self.capital_cost * self.om_costs * installed_capacity)

            # If a diesel price has been passed, the technology is diesel
            # And we apply the Szabo formula to calculate the transport cost for the diesel
            # p = (p_d + 2*p_d*consumption*time/volume)*(1/mu)*(1/LHVd)
            # Otherwise it's hydro/wind etc with no fuel cost

            if self.diesel_price > 0:
                if conflict_status == 1:
                    fuel_cost = (self.diesel_price + 2 * self.diesel_price * self.diesel_truck_consumption * (travel_hours * 2) /
                                 self.diesel_truck_volume) / LHV_DIESEL / self.efficiency
                elif conflict_status == 2:
                    fuel_cost = (self.diesel_price + 2 * self.diesel_price * self.diesel_truck_consumption * (travel_hours * 3) /
                                 self.diesel_truck_volume) / LHV_DIESEL / self.efficiency
                elif conflict_status == 3:
                    fuel_cost = (self.diesel_price + 2 * self.diesel_price * self.diesel_truck_consumption * (travel_hours * 4) /
                                 self.diesel_truck_volume) / LHV_DIESEL / self.efficiency
                elif conflict_status == 4:
                    fuel_cost = (self.diesel_price + 2 * self.diesel_price * self.diesel_truck_consumption * (travel_hours * 5) /
                                 self.diesel_truck_volume) / LHV_DIESEL / self.efficiency
                else:
                    fuel_cost = (self.diesel_price + 2 * self.diesel_price * self.diesel_truck_consumption * travel_hours /
                                 self.diesel_truck_volume) / LHV_DIESEL / self.efficiency
            else:
                fuel_cost = 0

        # Perform the time-value LCOE calculation
        project_life = end_year - start_year
        reinvest_year = 0

        # If the technology life is less than the project life, we will have to invest twice to buy it again
        if self.tech_life < project_life:
            reinvest_year = self.tech_life

        year = np.arange(project_life)
        el_gen = generation_per_year * np.ones(project_life)
        el_gen[0] = 0
        discount_factor = (1 + self.discount_rate) ** year
        investments = np.zeros(project_life)
        investments[0] = total_investment_cost

        # Calculate the year of re-investment if tech_life is smaller than project life
        if reinvest_year:
            investments[reinvest_year] = total_investment_cost

        # Calculate salvage value if tech_life is bigger than project life
        salvage = np.zeros(project_life)
        if reinvest_year > 0:
            used_life = project_life - self.tech_life
        else:
            used_life = project_life - 1
        salvage[project_life - 1] = total_investment_cost * (1 - used_life / self.tech_life)

        operation_and_maintenance = total_om_cost * np.ones(project_life)
        operation_and_maintenance[0] = 0
        fuel = el_gen * fuel_cost
        fuel[0] = 0

        # So we also return the total investment cost for this number of people
        if get_investment_cost:
            discounted_investments = investments / discount_factor
            return np.sum(discounted_investments) + (self.grid_capacity_investment * peak_load)
        else:
            discounted_costs = (investments + operation_and_maintenance + fuel - salvage) / discount_factor
            discounted_generation = el_gen / discount_factor
            return np.sum(discounted_costs) / np.sum(discounted_generation)

class SettlementProcessor:
    """
    Processes the dataframe and adds all the columns to determine the cheapest option and the final costs and summaries
    """
    def __init__(self, path):
        try:
            self.df = pd.read_csv(path)
        except FileNotFoundError:
            print('You need to first split into a base directory and prep!')
            raise

    def condition_df(self, country):
        """
        Do any initial data conditioning that may be required.
        """

        logging.info('Ensure that columns that are supposed to be numeric are numeric')
        self.df[SET_GHI] = pd.to_numeric(self.df[SET_GHI], errors='coerce')
        self.df[SET_WINDVEL] = pd.to_numeric(self.df[SET_WINDVEL], errors='coerce')
        self.df[SET_NIGHT_LIGHTS] = pd.to_numeric(self.df[SET_NIGHT_LIGHTS], errors='coerce')
        self.df[SET_ELEVATION] = pd.to_numeric(self.df[SET_ELEVATION], errors='coerce')
        self.df[SET_SLOPE] = pd.to_numeric(self.df[SET_SLOPE], errors='coerce')
        self.df[SET_LAND_COVER] = pd.to_numeric(self.df[SET_LAND_COVER], errors='coerce')
        self.df[SET_GRID_DIST_CURRENT] = pd.to_numeric(self.df[SET_GRID_DIST_CURRENT], errors='coerce')
        self.df[SET_GRID_DIST_PLANNED] = pd.to_numeric(self.df[SET_GRID_DIST_PLANNED], errors='coerce')
        self.df[SET_SUBSTATION_DIST] = pd.to_numeric(self.df[SET_SUBSTATION_DIST], errors='coerce')
        self.df[SET_ROAD_DIST] = pd.to_numeric(self.df[SET_ROAD_DIST], errors='coerce')
        self.df[SET_HYDRO_DIST] = pd.to_numeric(self.df[SET_HYDRO_DIST], errors='coerce')
        self.df[SET_HYDRO] = pd.to_numeric(self.df[SET_HYDRO], errors='coerce')
        self.df[SET_SOLAR_RESTRICTION] = pd.to_numeric(self.df[SET_SOLAR_RESTRICTION], errors='coerce')

        logging.info('Add column with country name')
        self.df['Country'] = country

        logging.info('Replace null values with zero')
        self.df.fillna(0, inplace=True)

        logging.info('Sort by country, Y and X')
        self.df.sort_values(by=[SET_COUNTRY, SET_Y, SET_X], inplace=True)

        logging.info('Add columns with location in degrees')
        project = Proj('+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')

        def get_x(row):
            x, y = project(row[SET_X] * 1000, row[SET_Y] * 1000, inverse=True)
            return x

        def get_y(row):
            x, y = project(row[SET_X] * 1000, row[SET_Y] * 1000, inverse=True)
            return y

        self.df[SET_X_DEG] = self.df.apply(get_x, axis=1)
        self.df[SET_Y_DEG] = self.df.apply(get_y, axis=1)

    def grid_penalties(self):
        """
        Add a grid penalty factor to increase the grid cost in areas that higher road distance, higher substation
        distance, unsuitable land cover, high slope angle or high elevation
        """

        def classify_road_dist(row):
            road_dist = row[SET_ROAD_DIST]
            if road_dist <= 5:
                return 5
            elif road_dist <= 10:
                return 4
            elif road_dist <= 25:
                return 3
            elif road_dist <= 50:
                return 2
            else:
                return 1

        def classify_substation_dist(row):
            substation_dist = row[SET_SUBSTATION_DIST]
            if substation_dist <= 0.5:
                return 5
            elif substation_dist <= 1:
                return 4
            elif substation_dist <= 5:
                return 3
            elif substation_dist <= 10:
                return 2
            else:
                return 1

        def classify_land_cover(row):
            land_cover = row[SET_LAND_COVER]
            if land_cover == 0:
                return 1
            elif land_cover == 1:
                return 3
            elif land_cover == 2:
                return 4
            elif land_cover == 3:
                return 3
            elif land_cover == 4:
                return 4
            elif land_cover == 5:
                return 3
            elif land_cover == 6:
                return 2
            elif land_cover == 7:
                return 5
            elif land_cover == 8:
                return 2
            elif land_cover == 9:
                return 5
            elif land_cover == 10:
                return 5
            elif land_cover == 11:
                return 1
            elif land_cover == 12:
                return 3
            elif land_cover == 13:
                return 3
            elif land_cover == 14:
                return 5
            elif land_cover == 15:
                return 3
            elif land_cover == 16:
                return 5

        def classify_elevation(row):
            elevation = row[SET_ELEVATION]
            if elevation <= 500:
                return 5
            elif elevation <= 1000:
                return 4
            elif elevation <= 2000:
                return 3
            elif elevation <= 3000:
                return 2
            else:
                return 1

        def classify_slope(row):
            slope = row[SET_SLOPE]
            if slope <= 10:
                return 5
            elif slope <= 20:
                return 4
            elif slope <= 30:
                return 3
            elif slope <= 40:
                return 2
            else:
                return 1

        def set_penalty(row):
            classification = row[SET_COMBINED_CLASSIFICATION]
            return 1 + (exp(0.85 * abs(1 - classification)) - 1) / 100

        logging.info('Classify road dist')
        self.df[SET_ROAD_DIST_CLASSIFIED] = self.df.apply(classify_road_dist, axis=1)

        logging.info('Classify substation dist')
        self.df[SET_SUBSTATION_DIST_CLASSIFIED] = self.df.apply(classify_substation_dist, axis=1)

        logging.info('Classify land cover')
        self.df[SET_LAND_COVER_CLASSIFIED] = self.df.apply(classify_land_cover, axis=1)

        logging.info('Classify elevation')
        self.df[SET_ELEVATION_CLASSIFIED] = self.df.apply(classify_elevation, axis=1)

        logging.info('Classify slope')
        self.df[SET_SLOPE_CLASSIFIED] = self.df.apply(classify_slope, axis=1)

        logging.info('Combined classification')
        self.df[SET_COMBINED_CLASSIFICATION] = (0.15 * self.df[SET_ROAD_DIST_CLASSIFIED] +
                                                0.20 * self.df[SET_SUBSTATION_DIST_CLASSIFIED] +
                                                0.20 * self.df[SET_LAND_COVER_CLASSIFIED] +
                                                0.15 * self.df[SET_ELEVATION_CLASSIFIED] +
                                                0.30 * self.df[SET_SLOPE_CLASSIFIED])

        logging.info('Grid penalty')
        self.df[SET_GRID_PENALTY] = self.df.apply(set_penalty, axis=1)

    def calc_wind_cfs(self):
        """
        Calculate the wind capacity factor based on the average wind velocity.
        """

        mu = 0.97  # availability factor
        t = 8760
        p_rated = 600
        z = 55  # hub height
        zr = 80  # velocity measurement height
        es = 0.85  # losses in wind electricity
        u_arr = range(1, 26)
        p_curve = [0, 0, 0, 0, 30, 77, 135, 208, 287, 371, 450, 514, 558,
                   582, 594, 598, 600, 600, 600, 600, 600, 600, 600, 600, 600]

        def get_wind_cf(row):
            u_zr = row[SET_WINDVEL]
            if u_zr == 0:
                return 0

            else:
                # Adjust for the correct hub height
                alpha = (0.37 - 0.088 * log(u_zr)) / (1 - 0.088 * log(zr / 10))
                u_z = u_zr * (z / zr) ** alpha

                # Rayleigh distribution and sum of series
                rayleigh = [(pi / 2) * (u / u_z ** 2) * exp((-pi / 4) * (u / u_z) ** 2) for u in u_arr]
                energy_produced = sum([mu * es * t * p * r for p, r in zip(p_curve, rayleigh)])

                return energy_produced/(p_rated * t)

        logging.info('Calculate Wind CF')
        self.df[SET_WINDCF] = self.df.apply(get_wind_cf, axis=1)

    def calibrate_pop_and_urban(self, pop_actual, pop_future, urban_current, urban_future, urban_cutoff, start_year, end_year, time_step):
        """
        Calibrate the actual current population, the urban split and forecast the future population
        """

        # Calculate the ratio between the actual population and the total population from the GIS layer
        logging.info('Calibrate current population')
        pop_ratio = pop_actual/self.df[SET_POP].sum()
        project_life = end_year - start_year

        # And use this ratio to calibrate the population in a new column
        self.df[SET_POP_CALIB] = self.df.apply(lambda row: row[SET_POP] * pop_ratio, axis=1)

        # Calculate the urban split, by calibrating the cutoff until the target ratio is achieved
        # Keep looping until it is satisfied or another break conditions is reached
        logging.info('Calibrate urban split')
        sorted_pop = self.df[SET_POP_CALIB].copy()
        sorted_pop.sort_values(inplace=True)
        urban_pop_break = (1-urban_current) * self.df[SET_POP_CALIB].sum()
        cumulative_urban_pop = 0
        ii = 0
        while cumulative_urban_pop < urban_pop_break:
            cumulative_urban_pop += sorted_pop.iloc[ii]
            ii += 1
        urban_cutoff = sorted_pop.iloc[ii-1]

        # Assign the 1 (urban)/0 (rural) values to each cell
        self.df[SET_URBAN] = self.df.apply(lambda row: 1 if row[SET_POP_CALIB] > urban_cutoff else 0, axis=1)

        # Get the calculated urban ratio, and limit it to within reasonable boundaries
        pop_urb = self.df.loc[self.df[SET_URBAN] == 1, SET_POP_CALIB].sum()
        urban_modelled = pop_urb / pop_actual

        # # Calculate the urban split, by calibrating the cutoff until the target ratio is achieved
        # # Keep looping until it is satisfied or another break conditions is reached
        # logging.info('Calibrate urban split')
        # count = 0
        # prev_vals = []  # Stores cutoff values that have already been tried to prevent getting stuck in a loop
        # accuracy = 0.005
        # max_iterations = 30
        # urban_modelled = 0
        # while True:
        #     # Assign the 1 (urban)/0 (rural) values to each cell
        #     self.df[SET_URBAN] = self.df.apply(lambda row: 1 if row[SET_POP_CALIB] > urban_cutoff else 0, axis=1)
        #
        #     # Get the calculated urban ratio, and limit it to within reasonable boundaries
        #     pop_urb = self.df.loc[self.df[SET_URBAN] == 1, SET_POP_CALIB].sum()
        #     urban_modelled = pop_urb / pop_actual
        #
        #     if urban_modelled == 0:
        #         urban_modelled = 0.05
        #     elif urban_modelled == 1:
        #         urban_modelled = 0.999
        #
        #     if abs(urban_modelled - urban_current) < accuracy:
        #         break
        #     else:
        #         urban_cutoff = sorted([0.005, urban_cutoff - urban_cutoff * 2 *
        #                                (urban_current - urban_modelled) / urban_current, 10000.0])[1]
        #
        #     if urban_cutoff in prev_vals:
        #         logging.info('NOT SATISFIED: repeating myself')
        #         break
        #     else:
        #         prev_vals.append(urban_cutoff)
        #
        #     if count >= max_iterations:
        #         logging.info('NOT SATISFIED: got to {}'.format(max_iterations))
        #         break
        #
        #     count += 1

        logging.info('The modelled urban ratio is {}. In case this is not acceptable please revise this part of the code'.format(urban_modelled))

        # Project future population, with separate growth rates for urban and rural
        logging.info('Project future population')

        urban_growth = (urban_future * pop_future) / (urban_current * pop_actual)
        rural_growth = ((1 - urban_future) * pop_future) / ((1 - urban_current) * pop_actual)

        yearly_urban_growth_rate = urban_growth**(1/project_life)
        yearly_rural_growth_rate = rural_growth**(1/project_life)

        self.df[SET_POP_FUTURE] = self.df.apply(lambda row: row[SET_POP_CALIB] * urban_growth
                                                if row[SET_URBAN] == 1
                                                else row[SET_POP_CALIB] * rural_growth,
                                                axis=1)

        yearsofanalysis = list(range((start_year + time_step),end_year+1,time_step))
        factor = 1

        for year in yearsofanalysis:
            self.df[SET_POP+"{}".format(year)] = self.df.apply(lambda row: row[SET_POP_CALIB] * (yearly_urban_growth_rate ** (time_step*factor))
                                                                                    if row[SET_URBAN] == 1
                                                                                    else row[SET_POP_CALIB] * (yearly_rural_growth_rate ** (time_step*factor)),axis=1)
            factor += 1

        self.df[SET_POP + "{}".format(start_year)] = self.df.apply(lambda row: row[SET_POP_CALIB], axis=1)

        # col_name+'_df{}'.format(i)
        # self.df[SET_POP_2020] = self.df.apply(lambda row: row[SET_POP_CALIB] * (yearly_urban_growth_rate**5) if row[SET_URBAN] == 1 else row[SET_POP_CALIB] * (yearly_rural_growth_rate**5),axis=1)
        #
        # self.df[SET_POP_2025] = self.df.apply(lambda row: row[SET_POP_CALIB] * (yearly_urban_growth_rate**10) if row[SET_URBAN] == 1 else row[SET_POP_CALIB] * (yearly_rural_growth_rate**10),axis=1)
        #
        # self.df[SET_POP_2030] = self.df.apply(lambda row: row[SET_POP_CALIB] * (yearly_urban_growth_rate**15) if row[SET_URBAN] == 1 else row[SET_POP_CALIB] * (yearly_rural_growth_rate**15), axis=1)

        return urban_cutoff, urban_modelled

    def elec_current_and_future(self, elec_actual, pop_cutoff, dist_to_trans, min_night_lights, max_grid_dist, max_road_dist, pop_tot, pop_cutoff2, start_year):
        """
        Calibrate the current electrification status, and future 'pre-electrification' status
        """

        # Calibrate current electrification
        logging.info('Calibrate current electrification')
        is_round_two = False
        grid_cutoff2 = 10
        road_cutoff2 = 10
        count = 0
        prev_vals = []
        accuracy = 0.01
        max_iterations_one = 30
        max_iterations_two = 60
        elec_modelled = 0

        while True:
            # Assign the 1 (electrified)/0 (un-electrified) values to each cell
            self.df[SET_ELEC_CURRENT] = self.df.apply(lambda row:
                                                      1
                                                      if (#row[SET_DIST_TO_TRANS] < dist_to_trans and
                                                          (row[SET_NIGHT_LIGHTS] > min_night_lights or
                                                          row[SET_POP_CALIB] > pop_cutoff and
                                                          row[SET_GRID_DIST_CURRENT] < max_grid_dist and
                                                          row[SET_ROAD_DIST] < max_road_dist))
                                                      or (row[SET_POP_CALIB] > pop_cutoff2 and
                                                          (row[SET_GRID_DIST_CURRENT] < grid_cutoff2 or
                                                          row[SET_ROAD_DIST] < road_cutoff2))
                                                      else 0,
                                                      axis=1)

            # Get the calculated electrified ratio, and limit it to within reasonable boundaries
            pop_elec = self.df.loc[self.df[SET_ELEC_CURRENT] == 1, SET_POP_CALIB].sum()
            elec_modelled = pop_elec / pop_tot

            if elec_modelled == 0:
                elec_modelled = 0.01
            elif elec_modelled == 1:
                elec_modelled = 0.99

            if abs(elec_modelled - elec_actual) < accuracy:
                break
            elif not is_round_two:
                dist_to_trans = sorted([2, dist_to_trans - dist_to_trans * 2 *
                                        (elec_actual - elec_modelled) / elec_actual, 100])[1]
                min_night_lights = sorted([5, min_night_lights - min_night_lights * 2 *
                                           (elec_actual - elec_modelled) / elec_actual, 60])[1]
                max_grid_dist = sorted([5, max_grid_dist + max_grid_dist * 2 *
                                        (elec_actual - elec_modelled) / elec_actual, 50])[1]
                max_road_dist = sorted([0.5, max_road_dist + max_road_dist * 2 *
                                        (elec_actual - elec_modelled) / elec_actual, 50])[1]
            elif elec_modelled - elec_actual < 0:
                pop_cutoff2 = sorted([0.01, pop_cutoff2 - pop_cutoff2 *
                                      (elec_actual - elec_modelled) / elec_actual, 100000])[1]
            elif elec_modelled - elec_actual > 0:
                pop_cutoff = sorted([0.01, pop_cutoff - pop_cutoff * 0.5 *
                                     (elec_actual - elec_modelled) / elec_actual, 10000])[1]

            constraints = '{}{}{}{}{}'.format(pop_cutoff, min_night_lights, max_grid_dist, max_road_dist, pop_cutoff2)
            if constraints in prev_vals and not is_round_two:
                logging.info('Repeating myself, on to round two')
                prev_vals = []
                is_round_two = True
            elif constraints in prev_vals and is_round_two:
                logging.info('NOT SATISFIED: repeating myself')
                print('2. Modelled electrification rate = {}'.format(elec_modelled))
                if 'y' in input('Do you want to rerun calibration with new input values? <y/n>'):
                    count = 0
                    is_round_two = False
                    dist_to_trans = float(input('Enter value for dist_to_trans: '))
                    pop_cutoff = float(input('Enter value for pop_cutoff: '))
                    min_night_lights = float(input('Enter value for min_night_lights: '))
                    max_grid_dist = float(input('Enter value for max_grid_dist: '))
                    max_road_dist = float(input('Enter value for max_road_dist: '))
                    pop_cutoff2 = float(input('Enter value for pop_cutoff2: '))
                else:
                    break
            else:
                prev_vals.append(constraints)

            if count >= max_iterations_one and not is_round_two:
                logging.info('Got to {}, on to round two'.format(max_iterations_one))
                is_round_two = True
            elif count >= max_iterations_two and is_round_two:
                logging.info('NOT SATISFIED: Got to {}'.format(max_iterations_two))
                print('2. Modelled electrification rate = {}'.format(elec_modelled))
                if 'y' in input('Do you want to rerun calibration with new input values? <y/n>'):
                    count = 0
                    is_round_two = False
                    dist_to_trans = int(input('Enter value for dist_to_trans: '))
                    pop_cutoff = int(input('Enter value for pop_cutoff: '))
                    min_night_lights = int(input('Enter value for min_night_lights: '))
                    max_grid_dist = int(input('Enter value for max_grid_dist: '))
                    max_road_dist = int(input('Enter value for max_road_dist: '))
                    pop_cutoff2 = int(input('Enter value for pop_cutoff2: '))
                else:
                    break

            count += 1

        logging.info('The modelled electrification rate achieved is {}. If this is not acceptable please revise this part of the algorithm'.format(elec_modelled))

        self.df[SET_ELEC_FUTURE_GRID + "{}".format(start_year)] = self.df.apply(lambda row: 1 if row[SET_ELEC_CURRENT] == 1 else 0, axis=1)
        self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(start_year)] = self.df.apply(lambda row: 0, axis=1)
        self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(start_year)] = self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_GRID + "{}".format(start_year)] == 1 or
                                                                                             row[SET_ELEC_FUTURE_OFFGRID + "{}".format(start_year)] == 1 else 0, axis=1)
        self.df[SET_ELEC_FINAL_CODE + "{}".format(start_year)] = self.df.apply(lambda row: 1 if row[SET_ELEC_CURRENT] == 1 else 99, axis=1)

        return min_night_lights, dist_to_trans, max_grid_dist, max_road_dist, elec_modelled, pop_cutoff, pop_cutoff2

    @staticmethod
    def separate_elec_status(elec_status):
        """
        Separate out the electrified and unelectrified states from list.
        """

        electrified = []
        unelectrified = []

        for i, status in enumerate(elec_status):
            if status:
                electrified.append(i)
            else:
                unelectrified.append(i)
        return electrified, unelectrified

    @staticmethod
    def get_2d_hash_table(x, y, unelectrified, distance_limit):
        """
        Generates the 2D Hash Table with the unelectrified locations hashed into the table for easy O(1) access.
        """

        hash_table = defaultdict(lambda: defaultdict(list))
        for unelec_row in unelectrified:
            hash_x = int(x[unelec_row] / distance_limit)
            hash_y = int(y[unelec_row] / distance_limit)
            hash_table[hash_x][hash_y].append(unelec_row)
        return hash_table

    @staticmethod
    def get_unelectrified_rows(hash_table, elec_row, x, y, distance_limit):
        """
        Returns all the unelectrified locations close to the electrified location
        based on the distance boundary limit specified by asking the 2D hash table.
        """

        unelec_list = []
        hash_x = int(x[elec_row] / distance_limit)
        hash_y = int(y[elec_row] / distance_limit)

        unelec_list.extend(hash_table.get(hash_x, {}).get(hash_y, []))
        unelec_list.extend(hash_table.get(hash_x, {}).get(hash_y - 1, []))
        unelec_list.extend(hash_table.get(hash_x, {}).get(hash_y + 1, []))

        unelec_list.extend(hash_table.get(hash_x + 1, {}).get(hash_y, []))
        unelec_list.extend(hash_table.get(hash_x + 1, {}).get(hash_y - 1, []))
        unelec_list.extend(hash_table.get(hash_x + 1, {}).get(hash_y + 1, []))

        unelec_list.extend(hash_table.get(hash_x - 1, {}).get(hash_y, []))
        unelec_list.extend(hash_table.get(hash_x - 1, {}).get(hash_y - 1, []))
        unelec_list.extend(hash_table.get(hash_x - 1, {}).get(hash_y + 1, []))

        return unelec_list

    def pre_electrification(self, grid_calc, grid_price, year, time_step, start_year):

        """" ... """

        logging.info('Define the initial electrification status')

        # Update electrification status based on already existing
        if (year - time_step) == start_year:
            self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)] = self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_GRID + "{}".format(year - time_step)] == 1 else 0, axis=1)
        else:
            self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)] = self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_GRID + "{}".format(year - time_step)] == 1 or
                                                                                          (row[SET_ELEC_FINAL_CODE + "{}".format(year - time_step)] == 1 & row[SET_LIMIT + "{}".format(year - time_step)] == 1) else 0, axis=1)

        if (year - time_step) == start_year:
            self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] = self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_OFFGRID + "{}".format(year - time_step)] == 1 else 0, axis=1)
        else:
            self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] = self.df.apply(lambda row: 1 if (row[SET_ELEC_FUTURE_OFFGRID + "{}".format(year - time_step)] == 1 and
                                                                                                   row[SET_ELEC_FUTURE_GRID + "{}".format(year)] != 1) or
                                                                                                  (row[SET_ELEC_FINAL_CODE + "{}".format(year - time_step)] != 1 and
                                                                                                   row[SET_LIMIT + "{}".format(year - time_step)] == 1) else 0, axis=1)

        if (year - time_step) == start_year:
            self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 1 else 0, axis=1)
        else:
            self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = self.df.apply(lambda row: 1 if (row[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 1) or
                                                                                                 (row[SET_ELEC_FUTURE_GRID + "{}".format(year)] == 1) or
                                                                                                 (row[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] == 1) else 0, axis=1)


        self.df[SET_LCOE_GRID + "{}".format(year)] = self.df.apply(lambda row: grid_price if row[SET_ELEC_FUTURE_GRID + "{}".format(year)] == 1 else 99, axis=1)

    def elec_extension(self, grid_calc, max_dist, year, start_year, end_year, timestep, grid_cap_gen_limit):
        """
        Iterate through all electrified settlements and find which settlements can be economically connected to the grid
        Repeat with newly electrified settlements until no more are added
        """
        new_grid_capacity = 0
        grid_capacity_limit = grid_cap_gen_limit  # kW per 5 years
        x = (self.df[SET_X]/1000).tolist()
        y = (self.df[SET_Y]/1000).tolist()
        pop = self.df[SET_POP + "{}".format(year)].tolist()
        prev_pop = self.df[SET_POP + "{}".format(year - timestep)].tolist()
        confl = self.df[SET_CONFLICT].tolist()
        travl = self.df[SET_TRAVEL_HOURS].tolist()
        enerperhh = self.df[SET_ENERGY_PER_CELL + "{}".format(year)]
        nupppphh = self.df[SET_NUM_PEOPLE_PER_HH]
        prev_code = self.df[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)]
        new_connections = self.df[SET_NEW_CONNECTIONS + "{}".format(year)]
        total_energy_per_cell = self.df[SET_TOTAL_ENERGY_PER_CELL]
        if year-timestep == start_year:
            elecorder = self.df[SET_ELEC_ORDER].tolist()
        else:
            elecorder = self.df[SET_ELEC_ORDER + "{}".format(year - timestep)].tolist()
        #urban = self.df[SET_URBAN].tolist()
        grid_penalty_ratio = self.df[SET_GRID_PENALTY].tolist()
        status = self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)].tolist()
        min_code_lcoes = self.df[SET_MIN_OFFGRID_LCOE + "{}".format(year)].tolist()
        new_lcoes = self.df[SET_LCOE_GRID + "{}".format(year)].tolist()
        grid_reach = self.df[SET_GRID_REACH_YEAR].tolist()

        urban_initially_electrified = sum(self.df.loc[
                                              (self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 1) & (
                                                          self.df[SET_URBAN] == 1)][
                                              SET_ENERGY_PER_CELL + "{}".format(year)])
        rural_initially_electrified = sum(self.df.loc[
                                              (self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 1) & (
                                                          self.df[SET_URBAN] == 0)][
                                              SET_ENERGY_PER_CELL + "{}".format(year)])
        consumption = rural_initially_electrified + urban_initially_electrified
        average_load = consumption / (1 - grid_calc.distribution_losses) / HOURS_PER_YEAR  # kW
        peak_load = average_load / grid_calc.base_to_peak_load_ratio  # kW
        grid_capacity_limit -= peak_load

        cell_path_real = list(np.zeros(len(status)).tolist())
        cell_path_adjusted = list(np.zeros(len(status)).tolist())
        electrified, unelectrified = self.separate_elec_status(status)

        close = []
        elec_nodes2 = []
        changes = []
        for elec in electrified:
            elec_nodes2.append((x[elec], y[elec]))
        elec_nodes2 = np.asarray(elec_nodes2)

        def closest_elec(unelec_node, elec_nodes):
            deltas = elec_nodes - unelec_node
            dist_2 = np.einsum('ij,ij->i', deltas, deltas)
            min_dist = np.argmin(dist_2)
            return min_dist

        logging.info('Initially {} electrified'.format(len(electrified)))
        loops = 1

        for unelec in unelectrified:
            if year >= grid_reach[unelec]:
                consumption = enerperhh[unelec]  # kWh/year
                average_load = consumption / (1 - grid_calc.distribution_losses) / HOURS_PER_YEAR  # kW
                peak_load = average_load / grid_calc.base_to_peak_load_ratio  # kW

                node = (x[unelec], y[unelec])
                closest_elec_node = closest_elec(node, elec_nodes2)
                dist = sqrt((x[electrified[closest_elec_node]] - x[unelec]) ** 2
                            + (y[electrified[closest_elec_node]] - y[unelec]) ** 2)
                if dist <= max_dist:
                    dist_adjusted = grid_penalty_ratio[unelec] * dist

                    if year-timestep == start_year:
                        elec_loop_value = 0
                    else:
                        elec_loop_value = elecorder[electrified[closest_elec_node]] + 1

                    grid_lcoe = grid_calc.get_lcoe(energy_per_cell=enerperhh[unelec],
                                                   start_year=year - timestep,
                                                   end_year=end_year,
                                                   people=pop[unelec],
                                                   new_connections=new_connections[unelec],
                                                   total_energy_per_cell=total_energy_per_cell[unelec],
                                                   prev_code=prev_code[unelec],
                                                   num_people_per_hh=nupppphh[unelec],
                                                   conflict_status=confl[unelec],
                                                   travel_hours=travl[unelec],
                                                   additional_mv_line_length=dist,
                                                   elec_loop=elec_loop_value)
                                                   # elec_loop=loops)

                    if grid_lcoe < min_code_lcoes[unelec]:
                        if (grid_lcoe < new_lcoes[unelec]) and (new_grid_capacity + peak_load < grid_capacity_limit):
                            new_lcoes[unelec] = grid_lcoe
                            cell_path_real[unelec] = dist
                            cell_path_adjusted[unelec] = dist_adjusted
                            new_grid_capacity += peak_load
                            if unelec not in changes:
                                changes.append(unelec)
                        else:
                            close.append(unelec)
                    else:
                        close.append(unelec)
                else:
                    close.append(unelec)
        electrified = changes[:]
        unelectrified = close
        
        while len(electrified) > 0:
            logging.info('Electrification loop {} with {} electrified'.format(loops, len(electrified)))

            loops += 1
            hash_table = self.get_2d_hash_table(x, y, electrified, max_dist)

            elec_nodes2 = []
            for elec in electrified:
                elec_nodes2.append((x[elec], y[elec]))
            elec_nodes2 = np.asarray(elec_nodes2)
            changes = []
            if len(elec_nodes2) > 0:
                for unelec in unelectrified:
                    if year >= grid_reach[unelec]:
                        consumption = enerperhh[unelec]  # kWh/year
                        average_load = consumption / (1 - grid_calc.distribution_losses) / HOURS_PER_YEAR  # kW
                        peak_load = average_load / grid_calc.base_to_peak_load_ratio  # kW

                        node = (x[unelec], y[unelec])
                        closest_elec_node = closest_elec(node, elec_nodes2)
                        dist = sqrt((x[electrified[closest_elec_node]] - x[unelec]) ** 2
                                    + (y[electrified[closest_elec_node]] - y[unelec]) ** 2)
                        prev_dist = cell_path_real[closest_elec_node]
                        if dist + prev_dist < max_dist:
                            grid_lcoe = grid_calc.get_lcoe(energy_per_cell=enerperhh[unelec],
                                                           start_year=year - timestep,
                                                           end_year=end_year,
                                                           people=pop[unelec],
                                                           new_connections=new_connections[unelec],
                                                           total_energy_per_cell=total_energy_per_cell[unelec],
                                                           prev_code=prev_code[unelec],
                                                           num_people_per_hh=nupppphh[unelec],
                                                           conflict_status=confl[unelec],
                                                           travel_hours=travl[unelec],
                                                           additional_mv_line_length=dist,
                                                           elec_loop=elecorder[electrified[closest_elec_node]] + 1)

                            if grid_lcoe < min_code_lcoes[unelec]:
                                if (grid_lcoe < new_lcoes[unelec]) and (new_grid_capacity + peak_load < grid_capacity_limit):
                                    new_lcoes[unelec] = grid_lcoe
                                    cell_path_real[unelec] = dist + prev_dist
                                    elecorder[unelec] = loops
                                    new_grid_capacity += peak_load
                                    if unelec not in changes:
                                        changes.append(unelec)
                        elif (new_grid_capacity + peak_load < grid_capacity_limit):
                            electrified_hashed = self.get_unelectrified_rows(hash_table, unelec, x, y, max_dist)
                            grid_capacity_addition_loop = 0
                            for elec in electrified_hashed:
                                prev_dist = cell_path_real[elec]
                                dist = sqrt((x[elec] - x[unelec]) ** 2 + (y[elec] - y[unelec]) ** 2)
                                if prev_dist + dist < max_dist:

                                    grid_lcoe = grid_calc.get_lcoe(energy_per_cell=enerperhh[unelec],
                                                                   start_year=year - timestep,
                                                                   end_year=end_year,
                                                                   people=pop[unelec],
                                                                   new_connections=new_connections[unelec],
                                                                   total_energy_per_cell=total_energy_per_cell[unelec],
                                                                   prev_code=prev_code[unelec],
                                                                   num_people_per_hh=nupppphh[unelec],
                                                                   conflict_status=confl[unelec],
                                                                   travel_hours=travl[unelec],
                                                                   additional_mv_line_length=dist,
                                                                   elec_loop=elecorder[elec] + 1)
                            if grid_lcoe < min_code_lcoes[unelec]:
                                if grid_lcoe < new_lcoes[unelec]:
                                    new_lcoes[unelec] = grid_lcoe
                                    cell_path_real[unelec] = dist + prev_dist
                                    elecorder[unelec] = loops
                                    if grid_capacity_addition_loop == 0:
                                        new_grid_capacity += peak_load
                                        grid_capacity_addition_loop += 1
                                    if unelec not in changes:
                                        changes.append(unelec)

            electrified = changes[:]
            unelectrified = set(unelectrified).difference(electrified)

        return new_lcoes, cell_path_real, elecorder

    def run_elec(self, grid_calc, max_dist, year, start_year, end_year, timestep, grid_cap_gen_limit):
        """
        Runs the grid extension algorithm
        """
        logging.info('Electrification algorithm starts running')

        self.df[SET_LCOE_GRID + "{}".format(year)], self.df[SET_MIN_GRID_DIST + "{}".format(year)], self.df[SET_ELEC_ORDER + "{}".format(year)] = self.elec_extension(grid_calc, max_dist, year, start_year, end_year, timestep, grid_cap_gen_limit)



    def set_scenario_variables(self, energy_per_pp_rural, energy_per_pp_urban, year, num_people_per_hh_rural, num_people_per_hh_urban, time_step, start_year):
        """
        Set the basic scenario parameters that differ based on urban/rural
        So that they are in the table and can be read directly to calculate LCOEs
        """

        logging.info('Calculate new connections')
        # Calculate new connections for grid related purposes

        self.df.loc[self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 1, SET_NEW_CONNECTIONS + "{}".format(year)] = (self.df[SET_POP + "{}".format(year)] - self.df[SET_POP + "{}".format(year - time_step)])
        self.df.loc[self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 0, SET_NEW_CONNECTIONS + "{}".format(year)] = self.df[SET_POP + "{}".format(year)]
        self.df.loc[self.df[SET_NEW_CONNECTIONS + "{}".format(year)] < 0, SET_NEW_CONNECTIONS + "{}".format(year)] = 0

        logging.info('Setting electrification demand as per target per year')

        # Define if a settlement is Urban or Rural
        self.df.loc[self.df[SET_URBAN] == 0, SET_NUM_PEOPLE_PER_HH] = num_people_per_hh_rural
        self.df.loc[self.df[SET_URBAN] == 1, SET_NUM_PEOPLE_PER_HH] = num_people_per_hh_urban

        self.df.loc[self.df[SET_URBAN] == 0, SET_ENERGY_PER_CELL + "{}".format(year)] = energy_per_pp_rural * self.df[SET_NEW_CONNECTIONS + "{}".format(year)]
        self.df.loc[self.df[SET_URBAN] == 1, SET_ENERGY_PER_CELL + "{}".format(year)] = energy_per_pp_urban * self.df[SET_NEW_CONNECTIONS + "{}".format(year)]

        if year - time_step == start_year:
            self.df.loc[self.df[SET_URBAN] == 0, SET_TOTAL_ENERGY_PER_CELL] = energy_per_pp_rural * self.df[SET_POP + "{}".format(year)]
            self.df.loc[self.df[SET_URBAN] == 1, SET_TOTAL_ENERGY_PER_CELL] = energy_per_pp_urban * self.df[SET_POP + "{}".format(year)]
            # self.df[SET_TOTAL_ENERGY_PER_CELL] = self.df[SET_ENERGY_PER_CELL + "{}".format(year)]
        else:
            self.df[SET_TOTAL_ENERGY_PER_CELL] += self.df[SET_ENERGY_PER_CELL + "{}".format(year)]

        # #Calculate new connections for off-grid related purposes
        # self.df.loc[self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year - timestep)] == 1, SET_NEW_CONNECTIONS + "{}".format(year)] = self.df[SET_POP + "{}".format(year)] - self.df[SET_POP + "{}".format(year - timestep)]
        # self.df.loc[self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year - timestep)] == 0, SET_NEW_CONNECTIONS + "{}".format(year)] = self.df[SET_POP + "{}".format(year)]

        #self.df.loc[self.df[SET_ELEC_FUTURE + "{}".format(year - timestep)] == 1, SET_NEW_CONNECTIONS + "{}".format(year)] = self.df[SET_POP + "{}".format(year)] - self.df[SET_POP + "{}".format(year - timestep)]
        #self.df.loc[self.df[SET_ELEC_FUTURE + "{}".format(year - timestep)] == 0, SET_NEW_CONNECTIONS + "{}".format(year)] = self.df[SET_POP + "{}".format(year)]

    def grid_reach_estimate(self, start_year, gridspeed):
        """ Estimates the year of grid arrival based on geospatial characteristics and grid expansion speed in km/year"""

        logging.info('Estimate year of grid reach')
        self.df[SET_GRID_REACH_YEAR] = self.df.apply(lambda row: int(start_year + (row[SET_GRID_DIST_PLANNED] * row[SET_COMBINED_CLASSIFICATION] / gridspeed)) if
                                                     row[SET_ELEC_FUTURE_GRID + "{}".format(start_year)] == 0 else start_year,
                                                     axis=1)

    def calculate_off_grid_lcoes(self, mg_hydro_calc, mg_wind_calc, mg_pv_calc,
                                 sa_pv_calc, mg_diesel_calc, sa_diesel_calc, year, start_year, end_year, timestep):
        """
        Calcuate the LCOEs for all off-grid technologies, and calculate the minimum, so that the electrification
        algorithm knows where the bar is before it becomes economical to electrify
        """

        # A df with all hydropower sites, to ensure that they aren't assigned more capacity than is available
        hydro_used = 'HydropowerUsed'  # the amount of the hydro potential that has been assigned
        hydro_df = self.df[[SET_HYDRO_FID, SET_HYDRO]].drop_duplicates(subset=SET_HYDRO_FID)
        hydro_df[hydro_used] = 0
        hydro_df = hydro_df.set_index(SET_HYDRO_FID)

        max_hydro_dist = 5  # the max distance in km to consider hydropower viable

        def hydro_lcoe(row):
            if row[SET_HYDRO_DIST] < max_hydro_dist:
                # calculate the capacity that would be added by the settlement
                additional_capacity = ((row[SET_NEW_CONNECTIONS + "{}".format(year)] * row[SET_ENERGY_PER_CELL + "{}".format(year)])
                                        /(HOURS_PER_YEAR * mg_hydro_calc.capacity_factor * mg_hydro_calc.base_to_peak_load_ratio))

                # and add it to the tracking df
                hydro_df.loc[row[SET_HYDRO_FID], hydro_used] += additional_capacity

                # if it exceeds the available capacity, it's not an option
                if hydro_df.loc[row[SET_HYDRO_FID], hydro_used] > hydro_df.loc[row[SET_HYDRO_FID], SET_HYDRO]:
                    return 99

                else:
                    return mg_hydro_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                                  start_year = year - timestep,
                                                  end_year= end_year,
                                                  people=row[SET_POP + "{}".format(year)],
                                                  new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                                  total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                                  prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                                  num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                                  conflict_status=row[SET_CONFLICT],
                                                  mv_line_length=row[SET_HYDRO_DIST])
            else:
                return 99

        logging.info('Calculate minigrid hydro LCOE')
        self.df[SET_LCOE_MG_HYDRO + "{}".format(year)] = self.df.apply(hydro_lcoe, axis=1)

        num_hydro_limited = hydro_df.loc[hydro_df[hydro_used] > hydro_df[SET_HYDRO]][SET_HYDRO].count()
        logging.info('{} potential hydropower sites were utilised to maximum capacity'.format(num_hydro_limited))

        logging.info('Calculate minigrid PV LCOE')
        self.df[SET_LCOE_MG_PV + "{}".format(year)] = self.df.apply(
            lambda row: mg_pv_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                            start_year = year - timestep,
                                            end_year = end_year,
                                            people=row[SET_POP + "{}".format(year)],
                                            new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                            total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                            prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                            num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                            conflict_status=row[SET_CONFLICT],
                                            capacity_factor=row[SET_GHI] / HOURS_PER_YEAR) if (row[SET_SOLAR_RESTRICTION] == 1 and row[SET_GHI] > 1000) else 99, axis=1)


        logging.info('Calculate minigrid wind LCOE')
        self.df[SET_LCOE_MG_WIND + "{}".format(year)] = self.df.apply(
            lambda row: mg_wind_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                              start_year = year - timestep,
                                              end_year= end_year,
                                              people=row[SET_POP + "{}".format(year)],
                                              new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                              total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                              prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                              num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                              conflict_status=row[SET_CONFLICT],
                                              capacity_factor=row[SET_WINDCF])
            if row[SET_WINDCF] > 0.1 else 99,
            axis=1)

        logging.info('Calculate minigrid diesel LCOE')
        self.df[SET_LCOE_MG_DIESEL + "{}".format(year)] = self.df.apply(
            lambda row:mg_diesel_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                               start_year=year - timestep,
                                               end_year= end_year,
                                               people=row[SET_POP + "{}".format(year)],
                                               new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                               total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                               prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                               num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                               conflict_status=row[SET_CONFLICT],
                                               travel_hours=row[SET_TRAVEL_HOURS]), axis=1)

        logging.info('Calculate standalone diesel LCOE')
        self.df[SET_LCOE_SA_DIESEL + "{}".format(year)] = self.df.apply(
            lambda row:sa_diesel_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                               start_year=year - timestep,
                                               end_year=end_year,
                                               people=row[SET_POP + "{}".format(year)],
                                               new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                               total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                               prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                               num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                               conflict_status=row[SET_CONFLICT],
                                               travel_hours=row[SET_TRAVEL_HOURS]), axis=1)

        logging.info('Calculate standalone PV LCOE')
        self.df[SET_LCOE_SA_PV + "{}".format(year)] = self.df.apply(
            lambda row: sa_pv_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                            start_year=year - timestep,
                                            end_year=end_year,
                                            people=row[SET_POP + "{}".format(year)],
                                            new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                            total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                            prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                            num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                            conflict_status=row[SET_CONFLICT],
                                            capacity_factor=row[SET_GHI] / HOURS_PER_YEAR) if row[SET_GHI] > 1000 else 99, axis=1)

        logging.info('Determine minimum technology (off-grid)')
        self.df[SET_MIN_OFFGRID + "{}".format(year)] = self.df[[SET_LCOE_SA_DIESEL + "{}".format(year), SET_LCOE_SA_PV + "{}".format(year), SET_LCOE_MG_WIND + "{}".format(year),
                                            SET_LCOE_MG_DIESEL + "{}".format(year), SET_LCOE_MG_PV + "{}".format(year), SET_LCOE_MG_HYDRO + "{}".format(year)]].T.idxmin()

        logging.info('Determine minimum tech LCOE')
        self.df[SET_MIN_OFFGRID_LCOE + "{}".format(year)] = self.df.apply(lambda row: (row[row[SET_MIN_OFFGRID + "{}".format(year)]]), axis=1)

        codes = {SET_LCOE_MG_HYDRO + "{}".format(year): 7,
                 SET_LCOE_MG_WIND + "{}".format(year): 6,
                 SET_LCOE_MG_PV + "{}".format(year): 5,
                 SET_LCOE_MG_DIESEL + "{}".format(year): 4,
                 SET_LCOE_SA_DIESEL + "{}".format(year): 2,
                 SET_LCOE_SA_PV + "{}".format(year): 3}

        self.df.loc[self.df[SET_MIN_OFFGRID + "{}".format(year)] == SET_LCOE_MG_HYDRO + "{}".format(
            year), SET_MIN_OFFGRID_CODE + "{}".format(year)] = codes[SET_LCOE_MG_HYDRO + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OFFGRID + "{}".format(year)] == SET_LCOE_SA_PV + "{}".format(
            year), SET_MIN_OFFGRID_CODE + "{}".format(year)] = codes[SET_LCOE_SA_PV + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OFFGRID + "{}".format(year)] == SET_LCOE_MG_WIND + "{}".format(
            year), SET_MIN_OFFGRID_CODE + "{}".format(year)] = codes[SET_LCOE_MG_WIND + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OFFGRID + "{}".format(year)] == SET_LCOE_MG_PV + "{}".format(
            year), SET_MIN_OFFGRID_CODE + "{}".format(year)] = codes[SET_LCOE_MG_PV + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OFFGRID + "{}".format(year)] == SET_LCOE_MG_DIESEL + "{}".format(
            year), SET_MIN_OFFGRID_CODE + "{}".format(year)] = codes[SET_LCOE_MG_DIESEL + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OFFGRID + "{}".format(year)] == SET_LCOE_SA_DIESEL + "{}".format(
            year), SET_MIN_OFFGRID_CODE + "{}".format(year)] = codes[SET_LCOE_SA_DIESEL + "{}".format(year)]

    def results_columns(self, mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc, sa_diesel_calc, grid_calc, year):
        """
        Once the grid extension algorithm has been run, determine the minimum overall option, and calculate the
        capacity and investment requirements for each settlement
        """

        logging.info('Determine minimum overall')
        self.df[SET_MIN_OVERALL + "{}".format(year)] = self.df[[SET_LCOE_GRID + "{}".format(year),
                                                                SET_LCOE_SA_DIESEL + "{}".format(year),
                                                                SET_LCOE_SA_PV + "{}".format(year),
                                                                SET_LCOE_MG_WIND + "{}".format(year),
                                                                SET_LCOE_MG_DIESEL + "{}".format(year),
                                                                SET_LCOE_MG_PV + "{}".format(year),
                                                                SET_LCOE_MG_HYDRO + "{}".format(year)]].T.idxmin()

        logging.info('Determine minimum overall LCOE')
        self.df[SET_MIN_OVERALL_LCOE + "{}".format(year)] = self.df.apply(lambda row: (row[row[SET_MIN_OVERALL + "{}".format(year)]]), axis=1)

        logging.info('Add technology codes')
        codes = {SET_LCOE_GRID + "{}".format(year): 1,
                 SET_LCOE_MG_HYDRO + "{}".format(year): 7,
                 SET_LCOE_MG_WIND + "{}".format(year): 6,
                 SET_LCOE_MG_PV + "{}".format(year): 5,
                 SET_LCOE_MG_DIESEL + "{}".format(year): 4,
                 SET_LCOE_SA_DIESEL + "{}".format(year): 2,
                 SET_LCOE_SA_PV + "{}".format(year): 3}

        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_GRID + "{}".format(year), SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_GRID + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_HYDRO + "{}".format(year), SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_MG_HYDRO + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_SA_PV + "{}".format(year), SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_SA_PV + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_WIND + "{}".format(year), SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_MG_WIND + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_PV + "{}".format(year), SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_MG_PV + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_DIESEL + "{}".format(year), SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_MG_DIESEL + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_SA_DIESEL + "{}".format(year), SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_SA_DIESEL + "{}".format(year)]

        # logging.info('Determine minimum category')
        # self.df[SET_MIN_CATEGORY + "{}".format(year)] = self.df[SET_MIN_OVERALL + "{}".format(year)].str.extract('(SA|MG|Grid)', expand=False)
        #
        # logging.info('Calculate new capacity')
        # self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_GRID + "{}".format(year), SET_NEW_CAPACITY + "{}".format(year)] = (
        #     (self.df[SET_NEW_CONNECTIONS + "{}".format(year)] * self.df[SET_ENERGY_PER_CELL + "{}".format(year)] / self.df[SET_NUM_PEOPLE_PER_HH]) /
        #     (HOURS_PER_YEAR * grid_calc.capacity_factor * grid_calc.base_to_peak_load_ratio))
        # self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_HYDRO + "{}".format(year), SET_NEW_CAPACITY + "{}".format(year)] = (
        #     (self.df[SET_NEW_CONNECTIONS + "{}".format(year)] * self.df[SET_ENERGY_PER_CELL + "{}".format(year)] / self.df[SET_NUM_PEOPLE_PER_HH]) /
        #     (HOURS_PER_YEAR * mg_hydro_calc.capacity_factor * mg_hydro_calc.base_to_peak_load_ratio))
        # self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_PV + "{}".format(year), SET_NEW_CAPACITY + "{}".format(year)] = (
        #     (self.df[SET_NEW_CONNECTIONS + "{}".format(year)] * self.df[SET_ENERGY_PER_CELL + "{}".format(year)] / self.df[SET_NUM_PEOPLE_PER_HH]) /
        #     (HOURS_PER_YEAR * (self.df[SET_GHI] / HOURS_PER_YEAR) * mg_pv_calc.base_to_peak_load_ratio))
        # self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_WIND + "{}".format(year), SET_NEW_CAPACITY + "{}".format(year)] = (
        #     (self.df[SET_NEW_CONNECTIONS + "{}".format(year)] * self.df[SET_ENERGY_PER_CELL + "{}".format(year)] / self.df[SET_NUM_PEOPLE_PER_HH]) /
        #     (HOURS_PER_YEAR * self.df[SET_WINDCF] * mg_wind_calc.base_to_peak_load_ratio))
        # self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_DIESEL + "{}".format(year), SET_NEW_CAPACITY + "{}".format(year)] = (
        #     (self.df[SET_NEW_CONNECTIONS + "{}".format(year)] * self.df[SET_ENERGY_PER_CELL + "{}".format(year)] / self.df[SET_NUM_PEOPLE_PER_HH]) /
        #     (HOURS_PER_YEAR * mg_diesel_calc.capacity_factor * mg_diesel_calc.base_to_peak_load_ratio))
        # self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_SA_DIESEL + "{}".format(year), SET_NEW_CAPACITY + "{}".format(year)] = (
        #     (self.df[SET_NEW_CONNECTIONS + "{}".format(year)] * self.df[SET_ENERGY_PER_CELL + "{}".format(year)] / self.df[SET_NUM_PEOPLE_PER_HH]) /
        #     (HOURS_PER_YEAR * sa_diesel_calc.capacity_factor * sa_diesel_calc.base_to_peak_load_ratio))
        # self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_SA_PV + "{}".format(year), SET_NEW_CAPACITY + "{}".format(year)] = (
        #     (self.df[SET_NEW_CONNECTIONS + "{}".format(year)] * self.df[SET_ENERGY_PER_CELL + "{}".format(year)] / self.df[SET_NUM_PEOPLE_PER_HH]) /
        #     (HOURS_PER_YEAR * (self.df[SET_GHI] / HOURS_PER_YEAR) * sa_pv_calc.base_to_peak_load_ratio))
        #
        #
        # logging.info('Calculate investment cost')
        # self.df[SET_INVESTMENT_COST + "{}".format(year)] = self.df.apply(res_investment_cost, axis=1)

    def apply_limitations(self, eleclimit, year):

        logging.info('Determine electrification limits')

        self.df[SET_LIMIT + "{}".format(year)] = self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] == 1 else 0, axis=1)
        conflictlimit = self.df[SET_CONFLICT].min()
        mintraveldistance = self.df[SET_TRAVEL_HOURS].min()
        max_loop = self.df[SET_ELEC_ORDER + "{}".format(year)].max()
        iteration = 0

        elecrate = sum(self.df[self.df[SET_LIMIT + "{}".format(year)] == 1][SET_POP + "{}".format(year)]) / self.df[SET_POP + "{}".format(year)].sum()
        #totalinvest = sum(self.df[self.df[SET_LIMIT + "{}".format(year)] == 1][SET_INVESTMENT_COST + "{}".format(year)])

        if elecrate < eleclimit:
            still_looking = True
        else:
            still_looking = False
            print("The investment cap does not allow further electrification expansion in year:{}".format(year))
        elec_loop = 0
        while still_looking:
            if elec_loop <= max_loop:
                self.df.loc[(self.df[SET_LCOE_GRID + "{}".format(year)] < 99) &
                            (self.df[SET_ELEC_ORDER + "{}".format(year)] == elec_loop) &
                            (self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] != 1) &
                            (self.df[SET_TRAVEL_HOURS] < mintraveldistance) &
                            (self.df[SET_CONFLICT] <= conflictlimit), SET_LIMIT + "{}".format(year)] = 1
            else:
                self.df.loc[(self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] != 1) &
                            (self.df[SET_TRAVEL_HOURS] < mintraveldistance) &
                            (self.df[SET_CONFLICT] <=  conflictlimit), SET_LIMIT + "{}".format(year)] = 1

            elecrate = sum(self.df[self.df[SET_LIMIT + "{}".format(year)] == 1][SET_POP + "{}".format(year)]) / self.df[SET_POP + "{}".format(year)].sum()

            iteration += 1

            if elecrate < eleclimit:
                mintraveldistance += 0.1
                if iteration > 200:
                    mintraveldistance += 0.4
                if iteration > 400:
                    mintraveldistance += 0.9
                if iteration > 500:
                    iteration = 0
                    conflictlimit += 1
                    mintraveldistance = self.df[SET_TRAVEL_HOURS].min()
                    if conflictlimit > 0:
                        elec_loop +=1
                else:
                    pass
            else:
                still_looking = False

        print("The electrification rate achieved is {}".format(elecrate))

    def final_decision(self,mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc, sa_diesel_calc, grid_calc, year, end_year, timestep):
        """" ... """

        logging.info('Determine final electrification decision')

        self.df[SET_ELEC_FINAL_GRID + "{}".format(year)] = self.df.apply(lambda row:
                                                                         1
                                                                         if (row[SET_ELEC_FUTURE_GRID + "{}".format(year)] == 1) or
                                                                            (row[SET_LIMIT + "{}".format(year)] == 1 and
                                                                             row[SET_MIN_OVERALL_CODE + "{}".format(year)] == 1 and
                                                                             row[SET_GRID_REACH_YEAR] < year)
                                                                         else 0, axis=1)
        self.df[SET_ELEC_FINAL_OFFGRID + "{}".format(year)] = self.df.apply(lambda row:
                                                                         1
                                                                         if (row[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] == 1 and
                                                                             row[SET_MIN_OVERALL_CODE + "{}".format(year)] != 1) or
                                                                            (row[SET_LIMIT + "{}".format(year)] == 1 and
                                                                             row[SET_ELEC_FINAL_GRID + "{}".format(year)] == 0) or
                                                                            (row[SET_LIMIT + "{}".format(year)] == 1 and
                                                                             row[SET_MIN_OVERALL_CODE + "{}".format(
                                                                                 year)] == 1 and
                                                                             row[SET_GRID_REACH_YEAR] > year)
                                                                         else 0, axis=1)

        self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 1) & (self.df[SET_ELEC_FINAL_GRID + "{}".format(year)] == 1), SET_ELEC_FINAL_CODE + "{}".format(year)] = 1

        # self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 1) &
        #             (self.df[SET_ELEC_FINAL_OFFGRID + "{}".format(year)] == 1) &
        #             (self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] == 1), SET_ELEC_FINAL_CODE + "{}".format(year)] = self.df[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)]
        #
        # self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 1) &
        #             (self.df[SET_ELEC_FINAL_OFFGRID + "{}".format(year)] == 1) &
        #             (self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] == 0), SET_ELEC_FINAL_CODE + "{}".format(year)] = self.df[SET_MIN_OFFGRID_CODE + "{}".format(year)]

        self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 1) & (self.df[SET_ELEC_FINAL_OFFGRID + "{}".format(year)] == 1), SET_ELEC_FINAL_CODE + "{}".format(year)] = self.df[SET_MIN_OFFGRID_CODE + "{}".format(year)]

        self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 0) &
                    (self.df[SET_ELEC_FINAL_GRID + "{}".format(year)] == 0) &
                    (self.df[SET_ELEC_FINAL_OFFGRID + "{}".format(year)] == 0), SET_ELEC_FINAL_CODE + "{}".format(year)] = 99

        logging.info('Calculate new capacity')

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 1, SET_NEW_CAPACITY + "{}".format(year)] = (
            (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
            (HOURS_PER_YEAR * grid_calc.capacity_factor * grid_calc.base_to_peak_load_ratio * (1 - grid_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 7, SET_NEW_CAPACITY + "{}".format(year)] = (
            (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
            (HOURS_PER_YEAR * mg_hydro_calc.capacity_factor * mg_hydro_calc.base_to_peak_load_ratio * (1 - mg_hydro_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 5, SET_NEW_CAPACITY + "{}".format(year)] = (
            (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
            (HOURS_PER_YEAR * (self.df[SET_GHI] / HOURS_PER_YEAR) * mg_pv_calc.base_to_peak_load_ratio * (1 - mg_pv_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 6, SET_NEW_CAPACITY + "{}".format(year)] = (
            (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
            (HOURS_PER_YEAR * self.df[SET_WINDCF] * mg_wind_calc.base_to_peak_load_ratio * (1 - mg_wind_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 4, SET_NEW_CAPACITY + "{}".format(year)] = (
            (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
            (HOURS_PER_YEAR * mg_diesel_calc.capacity_factor * mg_diesel_calc.base_to_peak_load_ratio * (1 - mg_diesel_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 2, SET_NEW_CAPACITY + "{}".format(year)] = (
            (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
            (HOURS_PER_YEAR * sa_diesel_calc.capacity_factor * sa_diesel_calc.base_to_peak_load_ratio * (1 - sa_diesel_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 3, SET_NEW_CAPACITY + "{}".format(year)] = (
            (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
            (HOURS_PER_YEAR * (self.df[SET_GHI] / HOURS_PER_YEAR) * sa_pv_calc.base_to_peak_load_ratio * (1 - sa_pv_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 99, SET_NEW_CAPACITY + "{}".format(year)] = 0

        def res_investment_cost(row):
            min_code = row[SET_ELEC_FINAL_CODE + "{}".format(year)]

            if min_code == 2:
                return sa_diesel_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                               start_year=year - timestep,
                                               end_year= end_year,
                                               people=row[SET_POP + "{}".format(year)],
                                               new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                               total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                               prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                               num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                               travel_hours=row[SET_TRAVEL_HOURS],
                                               conflict_status=row[SET_CONFLICT],
                                               get_investment_cost=True)

            elif min_code == 3:
                return sa_pv_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                           start_year=year - timestep,
                                           end_year=end_year,
                                           people=row[SET_POP + "{}".format(year)],
                                           new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                           total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                           prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                           num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                           capacity_factor=row[SET_GHI] / HOURS_PER_YEAR,
                                           conflict_status=row[SET_CONFLICT],
                                           get_investment_cost=True)

            elif min_code == 6:
                return mg_wind_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                             start_year=year - timestep,
                                             end_year=end_year,
                                             people=row[SET_POP + "{}".format(year)],
                                             new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                             total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                             prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                             num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                             capacity_factor=row[SET_WINDCF],
                                             conflict_status=row[SET_CONFLICT],
                                             get_investment_cost=True)

            elif min_code == 4:
                return mg_diesel_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                               start_year=year - timestep,
                                               end_year=end_year,
                                               people=row[SET_POP + "{}".format(year)],
                                               new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                               total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                               prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                               num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                               travel_hours=row[SET_TRAVEL_HOURS],
                                               conflict_status=row[SET_CONFLICT],
                                               get_investment_cost=True)

            elif min_code == 5:
                return mg_pv_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                           start_year=year - timestep,
                                           end_year=end_year,
                                           people=row[SET_POP + "{}".format(year)],
                                           new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                           total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                           prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                           num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                           capacity_factor=row[SET_GHI] / HOURS_PER_YEAR,
                                           conflict_status=row[SET_CONFLICT],
                                           get_investment_cost=True)

            elif min_code == 7:
                return mg_hydro_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                              start_year=year - timestep,
                                              end_year=end_year,
                                              people=row[SET_POP + "{}".format(year)],
                                              new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                              total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                              prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                              num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                              conflict_status=row[SET_CONFLICT],
                                              mv_line_length=row[SET_HYDRO_DIST],
                                              get_investment_cost=True)

            elif min_code == 1:
                return grid_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                          start_year=year - timestep,
                                          end_year=end_year,
                                          people=row[SET_POP + "{}".format(year)],
                                          new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                          total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                          prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                          num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                          conflict_status=row[SET_CONFLICT],
                                          additional_mv_line_length=row[SET_MIN_GRID_DIST + "{}".format(year)],
                                          elec_loop=row[SET_ELEC_ORDER + "{}".format(year)],
                                          get_investment_cost=True)
            else:
                return 0
                raise ValueError('A technology has not been accounted for in res_investment_cost()')

        logging.info('Calculate investment cost')
        self.df[SET_INVESTMENT_COST + "{}".format(year)] = self.df.apply(res_investment_cost, axis=1)

        # Update the actual electrification column with results
        self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = self.df[SET_LIMIT + "{}".format(year)]

    def calc_summaries(self, df_summary, sumtechs, year):

        """The next section calculates the summaries for technology split, consumption added and total investment cost"""

        logging.info('Calculate summaries')

        # Population Summaries

        df_summary[year][sumtechs[0]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 1) &
                                                                   (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_POP  + "{}".format(year)])

        df_summary[year][sumtechs[1]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 2) &
                                                                   (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_POP  + "{}".format(year)])

        df_summary[year][sumtechs[2]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 3) &
                                                                   (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_POP  + "{}".format(year)])

        df_summary[year][sumtechs[3]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 4) &
                                                                   (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_POP  + "{}".format(year)])

        df_summary[year][sumtechs[4]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 5) &
                                                                   (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_POP  + "{}".format(year)])

        df_summary[year][sumtechs[5]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 6) &
                                                                   (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_POP  + "{}".format(year)])

        df_summary[year][sumtechs[6]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 7) &
                                                                   (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_POP  + "{}".format(year)])

        # New_Connection Summaries

        df_summary[year][sumtechs[7]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 1) &
                                                            (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[8]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 2) &
                                                        (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[9]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 3) &
                                                             (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[10]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 4) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[11]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 5) &
                                                             (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[12]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 6) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[13]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 7) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CONNECTIONS + "{}".format(year)])

        # Capacity Summaries

        df_summary[year][sumtechs[14]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 1) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CAPACITY  + "{}".format(year)])

        df_summary[year][sumtechs[15]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 2) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CAPACITY  + "{}".format(year)])

        df_summary[year][sumtechs[16]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 3) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CAPACITY  + "{}".format(year)])

        df_summary[year][sumtechs[17]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 4) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CAPACITY  + "{}".format(year)])

        df_summary[year][sumtechs[18]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 5) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CAPACITY  + "{}".format(year)])

        df_summary[year][sumtechs[19]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 6) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CAPACITY  + "{}".format(year)])

        df_summary[year][sumtechs[20]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 7) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_NEW_CAPACITY  + "{}".format(year)])

        # Investment Summaries

        df_summary[year][sumtechs[21]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 1) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[22]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 2) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[23]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 3) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[24]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 4) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[25]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 5) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[26]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 6) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[27]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 7) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)][SET_INVESTMENT_COST + "{}".format(year)])
