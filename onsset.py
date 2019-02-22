# Author: KTH dESA Last modified by Alexandros Korkovelos
# Date: 07 February 2019
# Python version: 3.5

import os
import logging
import pandas as pd
from math import ceil, pi, exp, log, sqrt, radians, cos, sin, asin
# from pyproj import Proj
import numpy as np
from collections import defaultdict

logging.basicConfig(format='%(asctime)s\t\t%(message)s', level=logging.DEBUG)

# General
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
SET_WINDVEL = 'WindVel'  # Wind velocity in m/s
SET_WINDCF = 'WindCF'  # Wind capacity factor as percentage (range 0 - 1)
SET_HYDRO = 'Hydropower'  # Hydropower potential in kW
SET_HYDRO_DIST = 'HydropowerDist'  # Distance to hydropower site in km
SET_HYDRO_FID = 'HydropowerFID'  # the unique tag for eah hydropower, to not over-utilise
SET_SUBSTATION_DIST = 'SubstationDist'
SET_ELEVATION = 'Elevation'  # in metres
SET_SLOPE = 'Slope'  # in degrees
SET_LAND_COVER = 'LandCover'
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
SET_RESIDENTIAL_DEMAND = "ResidentialDemand"
SET_AGRI_DEMAND = "AgriDemand"
SET_HEALTH_DEMAND = "HealthDemand"
SET_EDU_DEMAND = "EducationDemand"
SET_COMMERCIAL_DEMAND = "CommercialDemand"
SET_GRID_CELL_AREA = 'GridCellArea'
SET_MV_CONNECT_DIST = 'MVConnectDist'
SET_HV_DIST_CURRENT = 'CurrentHVLineDist'
SET_HV_DIST_PLANNED = 'PlannedHVLineDist'
SET_MV_DIST_CURRENT = 'CurrentMVLineDist'
SET_MV_DIST_PLANNED = 'PlannedMVLineDist'
SET_ELEC_POP = 'ElecPop'
SET_WTFtier = "ResidentialDemandTier"
SET_INVEST_PER_CAPITA = "InvestmentCapita"

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
SPE_ELEC_URBAN = 'Urban_elec_ratio'   # Actual electrification for urban areas
SPE_ELEC_RURAL = 'Rural_elec_ratio'   # Actual electrification for rural areas
SPE_MIN_NIGHT_LIGHTS = 'MinNightLights'
SPE_MAX_GRID_EXTENSION_DIST = 'MaxGridExtensionDist'
SPE_MAX_ROAD_DIST = 'MaxRoadDist'
SPE_POP_CUTOFF1 = 'PopCutOffRoundOne'
SPE_POP_CUTOFF2 = 'PopCutOffRoundTwo'
SPE_ELEC_LIMIT = "ElecLimit"
SPE_INVEST_LIMIT = "InvestmentLimit"
SPE_DIST_TO_TRANS = "DistToTrans"

SPE_START_YEAR = "StartYear"
SPE_END_YEAR = "EndYEar"
SPE_TIMESTEP = "TimeStep"


class Technology:
    """
    Used to define the parameters for each electricity access technology, and to calculate the LCOE depending on
    input parameters.
    """

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
    def set_default_values(cls, base_year, start_year, end_year, discount_rate):
        cls.base_year = base_year
        cls.start_year = start_year
        cls.end_year = end_year
        cls.discount_rate = discount_rate


    def get_lcoe(self, energy_per_cell, people, num_people_per_hh, start_year, end_year, new_connections,
                 total_energy_per_cell, prev_code, grid_cell_area, conf_status=0, additional_mv_line_length=0,
                 capacity_factor=0,
                 grid_penalty_ratio=1, mv_line_length=0, travel_hours=0, elec_loop=0, productive_nodes=0,
                 additional_transformer=0,
                 get_investment_cost=False,
                 get_investment_cost_lv=False, get_investment_cost_mv=False, get_investment_cost_hv=False,
                 get_investment_cost_transformer=False, get_investment_cost_connection=False):
        """
        Calculates the LCOE depending on the parameters. Optionally calculates the investment cost instead.

        The only required parameters are energy_per_cell, people and num_people_per_hh
        additional_mv_line_length required for grid
        capacity_factor required for PV and wind
        mv_line_length required for hydro
        travel_hours required for diesel
        """

        # RUN_PARAM: Here are the assumptions related to cost and physical properties of grid extension elements
        # REVIEW - A final revision is needed before publishing
        HV_line_type = 69                   # kV
        HV_line_cost = 28000                # $/km for 69kV

        MV_line_type = 33                   # kV
        MV_line_amperage_limit = 8.0        # Ampere (A)
        MV_line_cost = 13000                # $/km  for 11-33 kV

        LV_line_type = 0.240                # kV
        LV_line_cost = 10000                # $/km for 0.4 kV
        LV_line_max_length = 0.5            # km

        service_Transf_type = 50            # kVa
        service_Transf_cost = 3500          # $/unit
        max_nodes_per_serv_trans = 300      # maximum number of nodes served by each service transformer
        MV_LV_sub_station_type = 400        # kVa
        MV_LV_sub_station_cost = 10000      # $/unit
        MV_MV_sub_station_cost = 10000      # $/unit
        HV_LV_sub_station_type = 1000       # kVa
        HV_LV_sub_station_cost = 25000      # $/unit
        HV_MV_sub_station_cost = 25000      # $/unit

        power_factor = 0.9
        load_moment = 9643                  # for 50mm aluminum conductor under 5% voltage drop (kW m)
        # simultaneous_usage = 0.06         # Not used eventually - maybe in an updated version

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

        if grid_cell_area <= 0:
            grid_cell_area = 0.001

        if grid_penalty_ratio == 0:
            grid_penalty_ratio = self.grid_penalty_ratio

        # If a new capacity factor isn't given, use the class capacity factor (for hydro, diesel etc)
        if capacity_factor == 0:
            capacity_factor = self.capacity_factor

        def distribution_network(people, energy_per_cell):
            if energy_per_cell <= 0:
                energy_per_cell = 0.0001
            try:
                int(energy_per_cell)
            except ValueError:
                energy_per_cell = 0.0001


            if people <= 0:
                people = 0.0001

            consumption = energy_per_cell  # kWh/year
            average_load = consumption / (1 - self.distribution_losses) / HOURS_PER_YEAR  # kW
            peak_load = average_load / self.base_to_peak_load_ratio  # kW
            try:
                int(peak_load)
            except ValueError:
                peak_load = 1

            # Sizing HV/MV
            HV_to_MV_lines = HV_line_cost / MV_line_cost
            max_MV_load = MV_line_amperage_limit * MV_line_type * HV_to_MV_lines

            MV_km = 0
            HV_km = 0
            if peak_load <= max_MV_load and additional_mv_line_length < 50 and self.grid_price > 0:
                MV_amperage = MV_LV_sub_station_type / MV_line_type
                No_of_MV_lines = ceil(peak_load / (MV_amperage * MV_line_type))
                MV_km = additional_mv_line_length * No_of_MV_lines
            elif self.grid_price > 0:
                HV_amperage = HV_LV_sub_station_type / HV_line_type
                No_of_HV_lines = ceil(peak_load / (HV_amperage * HV_line_type))
                HV_km = additional_mv_line_length * No_of_HV_lines

            Smax = peak_load / power_factor
            max_tranformer_area = pi * LV_line_max_length ** 2
            total_nodes = (people / num_people_per_hh) + productive_nodes


            try:
                no_of_service_transf = ceil(max(Smax / service_Transf_type, total_nodes / max_nodes_per_serv_trans,
                                            grid_cell_area / max_tranformer_area))
            except ValueError:
                no_of_service_transf = 1
            transformer_radius = ((grid_cell_area / no_of_service_transf) / pi) ** 0.5
            transformer_nodes = total_nodes / no_of_service_transf
            transformer_load = peak_load / no_of_service_transf
            cluster_radius = (grid_cell_area / pi) ** 0.5

            # Sizing LV lines in settlement
            if 2 / 3 * cluster_radius * transformer_load * 1000 < load_moment:
                cluster_lv_lines_length = 2 / 3 * cluster_radius * no_of_service_transf
                cluster_mv_lines_length = 0
            else:
                cluster_lv_lines_length = 0
                # cluster_mv_lines_length = 2 / 3 * cluster_radius * no_of_service_transf
                cluster_mv_lines_length = 2 * transformer_radius * no_of_service_transf

            hh_area = grid_cell_area / total_nodes
            hh_diameter = 2 * ((hh_area / pi) ** 0.5)

            transformer_lv_lines_length = hh_diameter * total_nodes
            No_of_HV_MV_subs = 0
            No_of_MV_MV_subs = 0
            No_of_HV_LV_subs = 0
            No_of_MV_LV_subs = 0
            No_of_HV_MV_subs += additional_transformer  # to connect the MV line to the HV grid

            if cluster_mv_lines_length > 0 and HV_km > 0:
                No_of_HV_MV_subs = ceil(peak_load/HV_LV_sub_station_type)  # 1
            elif cluster_mv_lines_length > 0 and MV_km > 0:
                No_of_MV_MV_subs = ceil(peak_load/MV_LV_sub_station_type)  # 1
            elif cluster_lv_lines_length > 0 and HV_km > 0:
                No_of_HV_LV_subs = ceil(peak_load/HV_LV_sub_station_type)  # 1
            else:
                No_of_MV_LV_subs = ceil(peak_load/MV_LV_sub_station_type)  # 1

            LV_km = cluster_lv_lines_length + transformer_lv_lines_length
            MV_km  # += cluster_mv_lines_length

            return HV_km, MV_km, cluster_mv_lines_length, LV_km, no_of_service_transf, \
                   No_of_HV_MV_subs, No_of_MV_MV_subs, No_of_HV_LV_subs, No_of_MV_LV_subs, \
                   consumption, peak_load, total_nodes
        # REVIEW - Andreas, the new connections column was modified; Please check whether this has created any problem in this version of the code as I find it hard to follow without comments. I assume this is to secure we do not oversize the network .? I believe it is fine though
        if people != new_connections and (prev_code == 1 or prev_code == 4 or prev_code == 5 or
                                          prev_code == 6 or prev_code == 7):
            HV_km1, MV_km1, cluster_mv_lines_length1, cluster_lv_lines_length1, no_of_service_transf1, \
            No_of_HV_MV_subs1, No_of_MV_MV_subs1, No_of_HV_LV_subs1, No_of_MV_LV_subs1, \
            generation_per_year1, peak_load1, total_nodes1 = distribution_network(people, total_energy_per_cell)

            HV_km2, MV_km2, cluster_mv_lines_length2, cluster_lv_lines_length2, no_of_service_transf2, \
            No_of_HV_MV_subs2, No_of_MV_MV_subs2, No_of_HV_LV_subs2, No_of_MV_LV_subs2, \
            generation_per_year2, peak_load2, total_nodes2 = \
                distribution_network(people=(people - new_connections),
                                     energy_per_cell=(total_energy_per_cell - energy_per_cell))
            hv_lines_total_length = max(HV_km1 - HV_km2, 0)
            mv_lines_connection_length = max(MV_km1 - MV_km2, 0)
            mv_lines_distribution_length = max(cluster_lv_lines_length1 - cluster_lv_lines_length2, 0)
            total_lv_lines_length = max(cluster_lv_lines_length1 - cluster_lv_lines_length2, 0)
            num_transformers = max(no_of_service_transf1 - no_of_service_transf2, 0)
            generation_per_year = max(generation_per_year1 - generation_per_year2, 0)
            peak_load = max(peak_load1 - peak_load2, 0)
            No_of_HV_LV_substation = max(No_of_HV_LV_subs1 - No_of_HV_LV_subs2, 0)
            No_of_HV_MV_substation = max(No_of_HV_MV_subs1 - No_of_HV_MV_subs2, 0)
            No_of_MV_MV_substation = max(No_of_MV_MV_subs1 - No_of_MV_MV_subs2, 0)
            No_of_MV_LV_substation = max(No_of_MV_LV_subs1 - No_of_MV_LV_subs2, 0)
            total_nodes = max(total_nodes1 - total_nodes2, 0)
        else:
            hv_lines_total_length, mv_lines_connection_length, mv_lines_distribution_length, total_lv_lines_length, num_transformers, \
            No_of_HV_MV_substation, No_of_MV_MV_substation, No_of_HV_LV_substation, No_of_MV_LV_substation, \
            generation_per_year, peak_load, total_nodes = distribution_network(people, energy_per_cell)

        try:
            int(conf_status)
        except ValueError:
            conf_status = 0
        conf_grid_pen = {0: 1, 1: 1.1, 2: 1.25, 3: 1.5, 4: 2}
        # The investment and O&M costs are different for grid and non-grid solutions
        if self.grid_price > 0:
            td_investment_cost = (hv_lines_total_length * HV_line_cost * (1 + self.existing_grid_cost_ratio * elec_loop) +
                                 mv_lines_connection_length * MV_line_cost * (1 + self.existing_grid_cost_ratio * elec_loop) +
                                 total_lv_lines_length * LV_line_cost +
                                 mv_lines_distribution_length * MV_line_cost +
                                 num_transformers * service_Transf_cost +
                                 total_nodes * self.connection_cost_per_hh +
                                 No_of_HV_LV_substation * HV_LV_sub_station_cost +
                                 No_of_HV_MV_substation * HV_MV_sub_station_cost +
                                 No_of_MV_MV_substation * MV_MV_sub_station_cost +
                                 No_of_MV_LV_substation * MV_LV_sub_station_cost) * conf_grid_pen[conf_status]
            td_investment_cost = td_investment_cost * grid_penalty_ratio
            td_om_cost = td_investment_cost * self.om_of_td_lines

            total_investment_cost = td_investment_cost
            total_om_cost = td_om_cost
            fuel_cost = self.grid_price  # / (1 - self.distribution_losses) REVIEW
        else:
            # TODO: Possibly add substation here for mini-grids
            conflict_sa_pen = {0: 1, 1: 1.03, 2: 1.07, 3: 1.125, 4: 1.25}
            conflict_mg_pen = {0: 1, 1: 1.05, 2: 1.125, 3: 1.25, 4: 1.5}
            total_lv_lines_length *= 0 if self.standalone else 1
            mv_lines_distribution_length *= 0 if self.standalone else 1
            mv_total_line_cost = MV_line_cost * mv_lines_distribution_length * conflict_mg_pen[conf_status]
            lv_total_line_cost = LV_line_cost * total_lv_lines_length * conflict_mg_pen[conf_status]
            service_transformer_total_cost = 0 if self.standalone else num_transformers * service_Transf_cost * conflict_mg_pen[conf_status]
            installed_capacity = peak_load / capacity_factor
            capital_investment = installed_capacity * self.capital_cost * conflict_sa_pen[conf_status] if self.standalone \
                else installed_capacity * self.capital_cost * conflict_mg_pen[conf_status]
            td_investment_cost = mv_total_line_cost + lv_total_line_cost + total_nodes * self.connection_cost_per_hh + service_transformer_total_cost
            td_om_cost = td_investment_cost * self.om_of_td_lines * conflict_sa_pen[conf_status] if self.standalone \
                else td_investment_cost * self.om_of_td_lines * conflict_mg_pen[conf_status]
            total_investment_cost = td_investment_cost + capital_investment
            total_om_cost = td_om_cost + (self.capital_cost * conflict_sa_pen[conf_status] * self.om_costs *
                                          conflict_sa_pen[conf_status] * installed_capacity) if self.standalone \
                else td_om_cost + (self.capital_cost * conflict_mg_pen[conf_status] * self.om_costs *
                                   conflict_mg_pen[conf_status] * installed_capacity)

            # If a diesel price has been passed, the technology is diesel
            # And we apply the Szabo formula to calculate the transport cost for the diesel
            # p = (p_d + 2*p_d*consumption*time/volume)*(1/mu)*(1/LHVd)
            # Otherwise it's hydro/wind etc with no fuel cost
            conf_diesel_pen = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}

            if self.diesel_price > 0:
                fuel_cost = (self.diesel_price + 2 * self.diesel_price * self.diesel_truck_consumption * (
                        travel_hours * conf_diesel_pen[conf_status]) /
                             self.diesel_truck_volume) / LHV_DIESEL / self.efficiency
            else:
                fuel_cost = 0

        # Perform the time-value LCOE calculation
        project_life = end_year - self.base_year + 1
        reinvest_year = 0
        step = start_year - self.base_year
        # If the technology life is less than the project life, we will have to invest twice to buy it again
        if self.tech_life + step < project_life:
            reinvest_year = self.tech_life + step

        year = np.arange(project_life)
        el_gen = generation_per_year * np.ones(project_life)
        el_gen[0:step] = 0
        discount_factor = (1 + self.discount_rate) ** year
        investments = np.zeros(project_life)
        investments[step] = total_investment_cost

        # Calculate the year of re-investment if tech_life is smaller than project life
        if reinvest_year:
            investments[reinvest_year] = total_investment_cost

        # Calculate salvage value if tech_life is bigger than project life
        salvage = np.zeros(project_life)
        if reinvest_year > 0:
            used_life = (project_life - step) - self.tech_life
        else:
            used_life = project_life - step - 1
        salvage[-1] = total_investment_cost * (1 - used_life / self.tech_life)
        # salvage[project_life - 1] = total_investment_cost * (1 - used_life / self.tech_life)
        operation_and_maintenance = total_om_cost * np.ones(project_life)
        operation_and_maintenance[0:step] = 0
        fuel = el_gen * fuel_cost
        fuel[0:step] = 0

        # So we also return the total investment cost for this number of people
        if get_investment_cost:
            discounted_investments = investments / discount_factor
            return np.sum(discounted_investments) + (self.grid_capacity_investment * peak_load)
        elif get_investment_cost_lv:
            return total_lv_lines_length * (LV_line_cost * conf_grid_pen[conf_status])
        elif get_investment_cost_mv:
            return (mv_lines_connection_length * MV_line_cost * (1 + self.existing_grid_cost_ratio * elec_loop) +
                    mv_lines_distribution_length * MV_line_cost) * conf_grid_pen[conf_status]
        elif get_investment_cost_hv:
            return hv_lines_total_length * (HV_line_cost * conf_grid_pen[conf_status]) * \
                   (1 + self.existing_grid_cost_ratio * elec_loop)
        elif get_investment_cost_transformer:
            return (No_of_HV_LV_substation * HV_LV_sub_station_cost +
                    No_of_HV_MV_substation * HV_MV_sub_station_cost +
                    No_of_MV_MV_substation * MV_MV_sub_station_cost +
                    No_of_MV_LV_substation * MV_LV_sub_station_cost) * conf_grid_pen[conf_status]
        elif get_investment_cost_connection:
            return total_nodes * self.connection_cost_per_hh
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
        # self.df[SET_GRID_DIST_CURRENT] = pd.to_numeric(self.df[SET_GRID_DIST_CURRENT], errors='coerce')
        # self.df[SET_GRID_DIST_PLANNED] = pd.to_numeric(self.df[SET_GRID_DIST_PLANNED], errors='coerce')
        self.df[SET_SUBSTATION_DIST] = pd.to_numeric(self.df[SET_SUBSTATION_DIST], errors='coerce')
        self.df[SET_ROAD_DIST] = pd.to_numeric(self.df[SET_ROAD_DIST], errors='coerce')
        self.df[SET_HYDRO_DIST] = pd.to_numeric(self.df[SET_HYDRO_DIST], errors='coerce')
        self.df[SET_HYDRO] = pd.to_numeric(self.df[SET_HYDRO], errors='coerce')

        logging.info('Add column with country name')
        self.df[SET_COUNTRY] = country

        logging.info('Adding column "ElectrificationOrder"')
        self.df[SET_ELEC_ORDER] = 0

        logging.info('Replace null values with zero')
        self.df.fillna(0, inplace=True)

        logging.info('Sort by country, Y and X')
        self.df.sort_values(by=[SET_COUNTRY, SET_Y_DEG, SET_X_DEG], inplace=True)

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

                return energy_produced / (p_rated * t)

        logging.info('Calculate Wind CF')
        self.df[SET_WINDCF] = self.df.apply(get_wind_cf, axis=1)

    def prepare_wtf_tier_columns (self, num_people_per_hh_rural, num_people_per_hh_urban):
        """ Prepares the five Residential Demand Tier Targets based customized for each country
        """
        # The MTF approach is given as per yearly household consumption (BEYOND CONNECTIONS Energy Access Redefined, ESMAP, 2015). Tiers in kWh/capita/year depends on the average ppl/hh which is different in every country
        logging.info('Populate ResidentialDemandTier columns')
        tier_num = [1,2,3,4,5]
        ppl_hh_average = (num_people_per_hh_urban + num_people_per_hh_rural) / 2
        tier_1 = 38.7 / ppl_hh_average  # 38.7 refers to kWh/household/year. It is the mean value between Tier 1 and Tier 2
        tier_2 = 219 / ppl_hh_average
        tier_3 = 803 / ppl_hh_average
        tier_4 = 2117 / ppl_hh_average
        tier_5 = 2993 / ppl_hh_average

        wb_tiers_all = {1: tier_1, 2: tier_2, 3: tier_3, 4: tier_4, 5: tier_5}

        for num in tier_num:
            self.df[SET_WTFtier + "{}".format(num)] = wb_tiers_all[num]


    def calibrate_pop_and_urban(self, pop_actual, pop_future_high, pop_future_low, urban_current, urban_future,
                                urban_cutoff, start_year, end_year):
        """
        Calibrate the actual current population, the urban split and forecast the future population
        """

        logging.info('Calibrate current population')
        project_life = end_year - start_year
        # Calculate the ratio between the actual population and the total population from the GIS layer
        pop_ratio = pop_actual / self.df[SET_POP].sum()
        # And use this ratio to calibrate the population in a new column
        self.df[SET_POP_CALIB] = self.df.apply(lambda row: row[SET_POP] * pop_ratio, axis=1)
        if max(self.df[SET_URBAN]) == 2:
            calibrate = True if 'n' in input(
                'Use urban definition from GIS layer <y/n> (n=model calibration):') else False
        else:
            calibrate = True
# RUN_PARAM: This is where manual calibration of urban/rural population takes place. The model uses 0, 1, 2 as GHS population layer does. As of this version, urban are only rows with value equal to 2
        if calibrate:
            urban_modelled = 2
            factor = 1
            while abs(urban_modelled - urban_current) > 0.01:
                self.df[SET_URBAN] = 0
                self.df.loc[(self.df[SET_POP_CALIB] > 5000 * factor) & (self.df[SET_POP_CALIB] / self.df[SET_GRID_CELL_AREA] > 350 * factor), SET_URBAN] = 1
                self.df.loc[(self.df[SET_POP_CALIB] > 50000 * factor) & (self.df[SET_POP_CALIB] / self.df[SET_GRID_CELL_AREA] > 1500 * factor), SET_URBAN] = 2
                pop_urb = self.df.loc[self.df[SET_URBAN] > 1, SET_POP_CALIB].sum()
                urban_modelled = pop_urb / pop_actual
                if urban_modelled > urban_current:
                    factor *= 1.1
                else:
                    factor *= 0.9
                # print(urban_modelled, factor)

        # Get the calculated urban ratio, and limit it to within reasonable boundaries
        pop_urb = self.df.loc[self.df[SET_URBAN] > 1, SET_POP_CALIB].sum()
        urban_modelled = pop_urb / pop_actual

        print('The modelled urban ratio is {:.2f}. '
                     'In case this is not acceptable please revise this part of the code'.format(urban_modelled))

        # Project future population, with separate growth rates for urban and rural
        logging.info('Project future population')

        if calibrate:
            urban_growth_high = (urban_future * pop_future_high) / (urban_modelled * pop_actual)
            rural_growth_high = ((1 - urban_future) * pop_future_high) / ((1 - urban_modelled) * pop_actual)

            yearly_urban_growth_rate_high = urban_growth_high ** (1 / project_life)
            yearly_rural_growth_rate_high = rural_growth_high ** (1 / project_life)

            urban_growth_low = (urban_future * pop_future_low) / (urban_modelled * pop_actual)
            rural_growth_low = ((1 - urban_future) * pop_future_low) / ((1 - urban_modelled) * pop_actual)

            yearly_urban_growth_rate_low = urban_growth_low ** (1 / project_life)
            yearly_rural_growth_rate_low = rural_growth_low ** (1 / project_life)
        else:
            urban_growth_high = pop_future_high / pop_actual
            rural_growth_high = pop_future_high / pop_actual

            yearly_urban_growth_rate_high = urban_growth_high ** (1 / project_life)
            yearly_rural_growth_rate_high = rural_growth_high ** (1 / project_life)

            urban_growth_low = pop_future_low / pop_actual
            rural_growth_low = pop_future_low / pop_actual

            yearly_urban_growth_rate_low = urban_growth_low ** (1 / project_life)
            yearly_rural_growth_rate_low = rural_growth_low ** (1 / project_life)

    # RUN_PARAM: Define here the years for which results should be provided in the output file.
        yearsofanalysis = [2023, 2030]

        for year in yearsofanalysis:
            self.df[SET_POP + "{}".format(year) + 'High'] = self.df.apply(lambda row: row[SET_POP_CALIB] *
                                                                             (yearly_urban_growth_rate_high ** (
                                                                                     year - start_year))
            if row[SET_URBAN] > 1
            else row[SET_POP_CALIB] *
                 (yearly_rural_growth_rate_high ** (year - start_year)),
                                                                 axis=1)

            self.df[SET_POP + "{}".format(year) + 'Low'] = self.df.apply(lambda row: row[SET_POP_CALIB] *
                                                                             (yearly_urban_growth_rate_low ** (
                                                                                     year - start_year))
            if row[SET_URBAN] > 1
            else row[SET_POP_CALIB] *
                 (yearly_rural_growth_rate_low ** (year - start_year)),
                                                                 axis=1)

        self.df[SET_POP + "{}".format(start_year)] = self.df.apply(lambda row: row[SET_POP_CALIB], axis=1)

        return urban_cutoff, urban_modelled

    def elec_current_and_future(self, elec_actual, elec_actual_urban, elec_actual_rural, pop_cutoff, dist_to_trans, min_night_lights,
                                max_grid_dist, max_road_dist, pop_tot, pop_cutoff2, start_year):
        """
        Calibrate the current electrification status, and future 'pre-electrification' status
        """
        #REVIEW: The way this works now, for all urban or rural settlements that fit the conditioning, the population SET_ELEC_POP is reduced by equal amount so that we match urban/rural national statistics respectively.
        #TODO We might need to improve this in the future if new data arrive
        urban_pop = (self.df.loc[self.df[SET_URBAN] > 1, SET_POP_CALIB].sum())  # Calibrate current electrification
        rural_pop = (self.df.loc[self.df[SET_URBAN] <= 1, SET_POP_CALIB].sum())  # Calibrate current electrification
        total_pop = self.df[SET_POP_CALIB].sum()
        total_elec_ratio = elec_actual
        urban_elec_ratio = elec_actual_urban
        rural_elec_ratio = elec_actual_rural
        factor = (total_pop * total_elec_ratio) / (urban_pop * urban_elec_ratio + rural_pop * rural_elec_ratio)
        urban_elec_ratio *= factor
        rural_elec_ratio *= factor
        # print('factor: ' + str(factor))
        self.df[SET_ELEC_POP] = self.df[SET_POP_CALIB] * self.df['NTLBin'] / self.df['NTLArea']
        self.df.loc[self.df['NTLArea'] <= 0, [SET_ELEC_POP]] = 0

        logging.info('Calibrate current electrification')
        is_round_two = False
        grid_cutoff2 = 10
        road_cutoff2 = 10
        count = 0
        prev_vals = []
        accuracy = 0.01
        max_iterations_one = 30
        max_iterations_two = 60
        self.df[SET_ELEC_CURRENT] = 0

        # This if function here skims through T&D columns to identify if any non 0 values exist; Then it defines priority accordingly.
        if max(self.df[SET_DIST_TO_TRANS]) > 0:
            self.df['GridDistCalibElec'] = self.df[SET_DIST_TO_TRANS]
            priority = 1
        elif max(self.df[SET_MV_DIST_CURRENT]) > 0:
            self.df['GridDistCalibElec'] = self.df[SET_MV_DIST_CURRENT]
            priority = 1
        else:
            self.df['GridDistCalibElec'] = self.df[SET_HV_DIST_CURRENT]
            priority = 2

        condition = 0
        #priority = 2
        while condition == 0:
            # Assign the 1 (electrified)/0 (un-electrified) values to each cell
            urban_electrified = urban_pop * urban_elec_ratio
            rural_electrified = rural_pop * rural_elec_ratio
            # RUN_PARAM: Calibration parameters if MV lines or transrofmer location is available
            if priority == 1:
                print('We have identified the existence of transformers or MV lines as input data; therefore we proceed using those for the calibration')
                self.df.loc[(self.df['GridDistCalibElec'] < 2) & (self.df[SET_NIGHT_LIGHTS] > 0) & (self.df[SET_POP_CALIB] > 500), SET_ELEC_CURRENT] = 1  # REVIEW 500 vs 300
                urban_elec_modelled = self.df.loc[(self.df[SET_ELEC_CURRENT] == 1) & (self.df[SET_URBAN] > 1), SET_ELEC_POP].sum()
                rural_elec_modelled = self.df.loc[(self.df[SET_ELEC_CURRENT] == 1) & (self.df[SET_URBAN] <= 1), SET_ELEC_POP].sum()
                urban_elec_factor = urban_elec_modelled / urban_electrified
                rural_elec_factor = rural_elec_modelled / rural_electrified
                if urban_elec_factor > 1:
                    self.df.loc[(self.df[SET_ELEC_CURRENT] == 1) & (self.df[SET_URBAN] > 1), SET_ELEC_POP] *= (1/urban_elec_factor)
                else:
                    print("The urban settlements identified as electrified are lower than in statistics; Please re-adjust the calibration conditions")

                if rural_elec_factor > 1:
                    self.df.loc[(self.df[SET_ELEC_CURRENT] == 1) & (self.df[SET_URBAN] <= 1), SET_ELEC_POP] *= (1/rural_elec_factor)
                else:
                    print("The rural settlements identified as electrified are lower than in statistics; Please re-adjust the calibration conditions")

                pop_elec = self.df.loc[self.df[SET_ELEC_CURRENT] == 1, SET_ELEC_POP].sum()
                elec_modelled = pop_elec / pop_tot

            # RUN_PARAM: Calibration parameters if only HV lines are available
            else:
                print('No transformers or MV lines were identified as input data; therefore we proceed to the calibration with HV line info')
                self.df.loc[(self.df['GridDistCalibElec'] < 5) & (self.df[SET_NIGHT_LIGHTS] > 0) & (self.df[SET_POP_CALIB] > 300), SET_ELEC_CURRENT] = 1

                urban_elec_modelled = self.df.loc[(self.df[SET_ELEC_CURRENT] == 1) & (self.df[SET_URBAN] > 1), SET_ELEC_POP].sum()
                rural_elec_modelled = self.df.loc[(self.df[SET_ELEC_CURRENT] == 1) & (self.df[SET_URBAN] <= 1), SET_ELEC_POP].sum()
                urban_elec_factor = urban_elec_modelled / urban_electrified
                rural_elec_factor = rural_elec_modelled / rural_electrified
                if urban_elec_factor > 1:
                    self.df.loc[(self.df[SET_ELEC_CURRENT] == 1) & (self.df[SET_URBAN] > 1), SET_ELEC_POP] *= (
                    1 / urban_elec_factor)
                else:
                    print("The urban settlements identified as electrified are lower than in statistics; Please re-adjust the calibration conditions")

                if rural_elec_factor > 1:
                    self.df.loc[(self.df[SET_ELEC_CURRENT] == 1) & (self.df[SET_URBAN] <= 1), SET_ELEC_POP] *= (
                    1 / rural_elec_factor)
                else:
                    print("The rural settlements identified as electrified are lower than in statistics; Please re-adjust the calibration conditions")

                pop_elec = self.df.loc[self.df[SET_ELEC_CURRENT] == 1, SET_ELEC_POP].sum()
                elec_modelled = pop_elec / pop_tot

            urban_elec_ratio = self.df.loc[(self.df[SET_ELEC_CURRENT] == 1) & (self.df[SET_URBAN] > 1), SET_ELEC_POP].sum() / urban_pop
            rural_elec_ratio = self.df.loc[(self.df[SET_ELEC_CURRENT] == 1) & (self.df[SET_URBAN] <= 1), SET_ELEC_POP].sum() / rural_pop

            print('The modelled electrification rate achieved is {0:.2f}.'
                         'Urban elec. rate is {1:.2f} and Rural elec. rate is {2:.2f}. \n'
                         'If this is not acceptable please revise this part of the algorithm'.format(elec_modelled, urban_elec_ratio, rural_elec_ratio))
            condition = 1

        self.df[SET_ELEC_FUTURE_GRID + "{}".format(start_year)] = \
            self.df.apply(lambda row: 1 if row[SET_ELEC_CURRENT] == 1 else 0, axis=1)
        self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(start_year)] = self.df.apply(lambda row: 0, axis=1)
        self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(start_year)] = \
            self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_GRID + "{}".format(start_year)] == 1 or
                                           row[SET_ELEC_FUTURE_OFFGRID + "{}".format(start_year)] == 1 else 0, axis=1)
        self.df[SET_ELEC_FINAL_CODE + "{}".format(start_year)] = \
            self.df.apply(lambda row: 1 if row[SET_ELEC_CURRENT] == 1 else 99, axis=1)

        return min_night_lights, dist_to_trans, max_grid_dist, max_road_dist, elec_modelled, pop_cutoff, pop_cutoff2, rural_elec_ratio, urban_elec_ratio

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
            # self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)] = \
            #     self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_GRID + "{}".format(year - time_step)] == 1
            #     else 0,
            #                   axis=1)
            self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)] = 0
            self.df.loc[self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - time_step)] == 1, SET_ELEC_FUTURE_GRID + "{}".format(year)] = 1
        else:
            # self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)] = \
            #     self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_GRID + "{}".format(year - time_step)] == 1 or
            #                                    (row[SET_ELEC_FINAL_CODE + "{}".format(year - time_step)] == 1 and
            #                                     row[SET_LIMIT + "{}".format(year - time_step)] == 1)
            #     else 0,
            #                   axis=1)
            self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)] = 0
            self.df.loc[self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - time_step)] == 1, SET_ELEC_FUTURE_GRID + "{}".format(year)] = 1
            self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year - time_step)] == 1) & (self.df[SET_LIMIT + "{}".format(year - time_step)] == 1), SET_ELEC_FUTURE_GRID + "{}".format(year)] = 1

        if (year - time_step) == start_year:
            # self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] = \
            #     self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_OFFGRID + "{}".format(year - time_step)] == 1
            #     else 0,
            #                   axis=1)
            self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] = 0
            self.df.loc[self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year - time_step)] == 1, SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] = 1
        else:
            # self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] = \
                # self.df.apply(lambda row: 1 if (row[SET_ELEC_FUTURE_OFFGRID + "{}".format(year - time_step)] == 1 and
                #                                 row[SET_ELEC_FUTURE_GRID + "{}".format(year)] != 1) or
                #                                (row[SET_ELEC_FINAL_CODE + "{}".format(year - time_step)] != 1 and
                #                                 row[SET_LIMIT + "{}".format(year - time_step)] == 1)
                # else 0,
                #               axis=1)
            self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] = 0
            self.df.loc[(self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year - time_step)] == 1) & (self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - time_step)] != 1), SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] = 1
            self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year - time_step)] != 1) & (self.df[SET_LIMIT + "{}".format(year - time_step)] == 1), SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] = 1

        if (year - time_step) == start_year:
            # self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = \
            #     self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 1
            #     else 0,
            #                   axis=1)
            self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = 0
            self.df.loc[self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 1, SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = 1
        else:
            # self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = \
            #     self.df.apply(lambda row: 1 if (row[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 1) or
            #                                    (row[SET_ELEC_FUTURE_GRID + "{}".format(year)] == 1) or
            #                                    (row[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] == 1)
            #     else 0,
            #                   axis=1)
            self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = 0
            self.df.loc[self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 1, SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = 1
            self.df.loc[self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - time_step)] == 1, SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = 1
            self.df.loc[self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year - time_step)] == 1, SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = 1

        # self.df[SET_LCOE_GRID + "{}".format(year)] = \
            # self.df.apply(lambda row: grid_price if row[SET_ELEC_FUTURE_GRID + "{}".format(year)] == 1
            # else 99,
            #               axis=1)
        self.df[SET_LCOE_GRID + "{}".format(year)] = 99
        self.df.loc[self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)] == 1, SET_LCOE_GRID + "{}".format(year)] = grid_price

    def current_mv_line_dist(self):
        logging.info('Determine current MV line length')
        self.df[SET_MV_CONNECT_DIST] = 0
        self.df.loc[self.df[SET_ELEC_CURRENT] == 1, SET_MV_CONNECT_DIST] = self.df[SET_HV_DIST_CURRENT]

    def pre_new_lines(self, grid_calc, max_dist, year, start_year, end_year, timestep, grid_cap_gen_limit):
        new_grid_capacity = 0
        grid_capacity_limit = grid_cap_gen_limit  # kW per 5 years
        x = (self.df[SET_X_DEG]).tolist()
        y = (self.df[SET_Y_DEG]).tolist()
        pop = self.df[SET_POP + "{}".format(year)].tolist()
        confl = self.df[SET_CONFLICT].tolist()
        travl = self.df[SET_TRAVEL_HOURS].tolist()
        enerperhh = self.df[SET_ENERGY_PER_CELL + "{}".format(year)]
        nupppphh = self.df[SET_NUM_PEOPLE_PER_HH]
        grid_cell_area = self.df['GridCellArea']
        prev_code = self.df[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)]
        new_connections = self.df[SET_NEW_CONNECTIONS + "{}".format(year)]
        total_energy_per_cell = self.df[SET_TOTAL_ENERGY_PER_CELL]
        if year - timestep == start_year:
            elecorder = self.df[SET_ELEC_ORDER].tolist()
        else:
            elecorder = self.df[SET_ELEC_ORDER + "{}".format(year - timestep)].tolist()
        grid_penalty_ratio = self.df[SET_GRID_PENALTY].tolist()
        status = self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)].tolist()
        min_code_lcoes = self.df[SET_MIN_OFFGRID_LCOE + "{}".format(year)].tolist()
        new_lcoes = self.df[SET_LCOE_GRID + "{}".format(year)].tolist()
        grid_reach = self.df[SET_GRID_REACH_YEAR].tolist()
        cell_path_real = self.df[SET_MV_CONNECT_DIST].tolist()
        planned_hv_dist = self.df[SET_HV_DIST_PLANNED].tolist()

        urban_initially_electrified = sum(self.df.loc[
                                              (self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 1) & (
                                                      self.df[SET_URBAN] == 2)][
                                              SET_ENERGY_PER_CELL + "{}".format(year)])
        rural_initially_electrified = sum(self.df.loc[
                                              (self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 1) & (
                                                      self.df[SET_URBAN] < 2)][
                                              SET_ENERGY_PER_CELL + "{}".format(year)])
        consumption = rural_initially_electrified + urban_initially_electrified
        average_load = consumption / (1 - grid_calc.distribution_losses) / HOURS_PER_YEAR  # kW
        peak_load = average_load / grid_calc.base_to_peak_load_ratio  # kW
        grid_capacity_limit -= peak_load

        cell_path_adjusted = list(np.zeros(len(status)).tolist())
        electrified, unelectrified = self.separate_elec_status(status)

        for unelec in unelectrified:
            grid_lcoe = 99
            if year >= grid_reach[unelec]:
                consumption = enerperhh[unelec]  # kWh/year
                average_load = consumption / (1 - grid_calc.distribution_losses) / HOURS_PER_YEAR  # kW
                peak_load = average_load / grid_calc.base_to_peak_load_ratio  # kW

                dist = planned_hv_dist[unelec]
                dist_adjusted = grid_penalty_ratio[unelec] * dist
                if dist <= max_dist:
                    elec_loop_value = 0

                    grid_lcoe = grid_calc.get_lcoe(energy_per_cell=enerperhh[unelec],
                                                   start_year=year - timestep,
                                                   end_year=end_year,
                                                   people=pop[unelec],
                                                   new_connections=new_connections[unelec],
                                                   total_energy_per_cell=total_energy_per_cell[unelec],
                                                   prev_code=prev_code[unelec],
                                                   num_people_per_hh=nupppphh[unelec],
                                                   grid_cell_area=grid_cell_area[unelec],
                                                   conf_status=confl[unelec],
                                                   travel_hours=travl[unelec],
                                                   additional_mv_line_length=dist_adjusted,
                                                   elec_loop=elec_loop_value,
                                                   additional_transformer=1)
                    grid_lcoe = 99 # FIX
                    if grid_lcoe < min_code_lcoes[unelec]:
                        status[unelec] = 1
                        cell_path_real[unelec] = dist
        return status, cell_path_real

    def elec_extension(self, grid_calc, max_dist, year, start_year, end_year, timestep, grid_cap_gen_limit):
        """
        Iterate through all electrified settlements and find which settlements can be economically connected to the grid
        Repeat with newly electrified settlements until no more are added
        """
        new_grid_capacity = 0
        grid_capacity_limit = grid_cap_gen_limit  # kW per 5 years
        # x = (self.df[SET_X]/1000).tolist()
        # y = (self.df[SET_Y]/1000).tolist()
        x = (self.df[SET_X_DEG]).tolist()
        y = (self.df[SET_Y_DEG]).tolist()
        pop = self.df[SET_POP + "{}".format(year)].tolist()
        # prev_pop = self.df[SET_POP + "{}".format(year - timestep)].tolist()
        confl = self.df[SET_CONFLICT].tolist()
        travl = self.df[SET_TRAVEL_HOURS].tolist()
        enerperhh = self.df[SET_ENERGY_PER_CELL + "{}".format(year)]
        nupppphh = self.df[SET_NUM_PEOPLE_PER_HH]
        grid_cell_area = self.df['GridCellArea']
        prev_code = self.df[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)]
        new_connections = self.df[SET_NEW_CONNECTIONS + "{}".format(year)]
        total_energy_per_cell = self.df[SET_TOTAL_ENERGY_PER_CELL]
        if year - timestep == start_year:
            elecorder = self.df[SET_ELEC_ORDER].tolist()
        else:
            elecorder = self.df[SET_ELEC_ORDER + "{}".format(year - timestep)].tolist()
        # urban = self.df[SET_URBAN].tolist()
        grid_penalty_ratio = self.df[SET_GRID_PENALTY].tolist()
        status = self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)].tolist()
        min_code_lcoes = self.df[SET_MIN_OFFGRID_LCOE + "{}".format(year)].tolist()
        min_off_grid_code = self.df[SET_MIN_OFFGRID_CODE + "{}".format(year)].tolist()
        new_lcoes = self.df[SET_LCOE_GRID + "{}".format(year)].tolist()
        grid_reach = self.df[SET_GRID_REACH_YEAR].tolist()
        # cell_path_real = list(np.zeros(len(status)).tolist())
        cell_path_real = self.df[SET_MV_CONNECT_DIST].tolist()
        # planned_hv_dist = self.df[SET_SUBSTATION_DIST].tolist()  # If connecting from substation
        planned_hv_dist = self.df[SET_HV_DIST_PLANNED].tolist()  # If connecting from anywhere on the HV line

        urban_initially_electrified = sum(self.df.loc[
                                              (self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 1) & (
                                                      self.df[SET_URBAN] == 2)][
                                              SET_ENERGY_PER_CELL + "{}".format(year)])
        rural_initially_electrified = sum(self.df.loc[
                                              (self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 1) & (
                                                      self.df[SET_URBAN] < 2)][
                                              SET_ENERGY_PER_CELL + "{}".format(year)])
        consumption = rural_initially_electrified + urban_initially_electrified
        average_load = consumption / (1 - grid_calc.distribution_losses) / HOURS_PER_YEAR  # kW
        peak_load = average_load / grid_calc.base_to_peak_load_ratio  # kW
        grid_capacity_limit -= peak_load

        cell_path_adjusted = list(np.zeros(len(status)).tolist())
        electrified, unelectrified = self.separate_elec_status(status)

        filtered_unelectrified = []
        for unelec in unelectrified:
            grid_lcoe = grid_calc.get_lcoe(energy_per_cell=enerperhh[unelec],
                                           start_year=year - timestep,
                                           end_year=end_year,
                                           people=pop[unelec],
                                           new_connections=new_connections[unelec],
                                           total_energy_per_cell=total_energy_per_cell[unelec],
                                           prev_code=prev_code[unelec],
                                           num_people_per_hh=nupppphh[unelec],
                                           grid_cell_area=grid_cell_area[unelec],
                                           conf_status=confl[unelec],
                                           travel_hours=travl[unelec],
                                           additional_mv_line_length=0,
                                           elec_loop=0)
            if grid_lcoe < min_code_lcoes[unelec]:
                filtered_unelectrified.append(unelec)
        unelectrified = filtered_unelectrified

        close = []
        elec_nodes2 = []
        changes = []
        for elec in electrified:
            elec_nodes2.append((x[elec], y[elec]))
        elec_nodes2 = np.asarray(elec_nodes2)

        def haversine(lon1, lat1, lon2, lat2):
            """
            Calculate the great circle distance between two points
            on the earth (specified in decimal degrees)
            """
            # convert decimal degrees to radians
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

            # haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            r = 6371  # Radius of earth in kilometers. Use 3956 for miles
            return c * r

        def closest_elec(unelec_node, elec_nodes):
            deltas = elec_nodes - unelec_node
            dist_2 = np.einsum('ij,ij->i', deltas, deltas)
            min_dist = np.argmin(dist_2)
            return min_dist

        logging.info('Initially {} electrified'.format(len(electrified)))
        loops = 1

        # First round of extension from existing MV network
        for unelec in unelectrified:
            grid_lcoe = 99
            if year >= grid_reach[unelec]:
                consumption = enerperhh[unelec]  # kWh/year
                average_load = consumption / (1 - grid_calc.distribution_losses) / HOURS_PER_YEAR  # kW
                peak_load = average_load / grid_calc.base_to_peak_load_ratio  # kW

                node = (x[unelec], y[unelec])
                closest_elec_node = closest_elec(node, elec_nodes2)
                dist = haversine(x[electrified[closest_elec_node]], y[electrified[closest_elec_node]], x[unelec],
                                 y[unelec])
                dist_adjusted = grid_penalty_ratio[unelec] * dist
                if dist + cell_path_real[electrified[closest_elec_node]] <= max_dist:  #  or year - timestep == start_year: CHECK
                    if year - timestep == start_year:
                        elec_loop_value = 1
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
                                                   grid_cell_area=grid_cell_area[unelec],
                                                   conf_status=confl[unelec],
                                                   travel_hours=travl[unelec],
                                                   additional_mv_line_length=dist_adjusted,
                                                   elec_loop=elec_loop_value)

                    if grid_lcoe < min_code_lcoes[unelec]:
                        if (grid_lcoe < new_lcoes[unelec]) and (new_grid_capacity + peak_load < grid_capacity_limit):
                            new_lcoes[unelec] = grid_lcoe
                            # cell_path_real[unelec] = dist
                            cell_path_real[unelec] = dist + cell_path_real[electrified[closest_elec_node]]
                            cell_path_adjusted[unelec] = dist_adjusted
                            new_grid_capacity += peak_load
                            elecorder[unelec] = elec_loop_value
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

        #  Extension from HV lines
        for unelec in unelectrified:
            grid_lcoe = 99
            if year >= grid_reach[unelec]:
                consumption = enerperhh[unelec]  # kWh/year
                average_load = consumption / (1 - grid_calc.distribution_losses) / HOURS_PER_YEAR  # kW
                peak_load = average_load / grid_calc.base_to_peak_load_ratio  # kW

                dist = planned_hv_dist[unelec]
                dist_adjusted = grid_penalty_ratio[unelec] * dist
                if dist <= max_dist:
                    elec_loop_value = 0

                    grid_lcoe = grid_calc.get_lcoe(energy_per_cell=enerperhh[unelec],
                                                   start_year=year - timestep,
                                                   end_year=end_year,
                                                   people=pop[unelec],
                                                   new_connections=new_connections[unelec],
                                                   total_energy_per_cell=total_energy_per_cell[unelec],
                                                   prev_code=prev_code[unelec],
                                                   num_people_per_hh=nupppphh[unelec],
                                                   grid_cell_area=grid_cell_area[unelec],
                                                   conf_status=confl[unelec],
                                                   travel_hours=travl[unelec],
                                                   additional_mv_line_length=dist_adjusted,
                                                   elec_loop=elec_loop_value,
                                                   additional_transformer=1)  # 0 if connecting to substation, 1 if connecting anywhere on HV line
                    # grid_lcoe = 99 # FIX
                    if (grid_lcoe < min_code_lcoes[unelec]) and (new_grid_capacity + peak_load < grid_capacity_limit):
                        new_lcoes[unelec] = grid_lcoe
                        status[unelec] = 1
                        cell_path_real[unelec] = dist
                        cell_path_adjusted[unelec] = dist_adjusted
                        new_grid_capacity += peak_load
                        elecorder[unelec] = 0
                        if unelec not in changes:
                            changes.append(unelec)
        electrified = changes[:]
        unelectrified = set(unelectrified).difference(electrified)

        #  Second to last round of extension loops from existing and new MV liens
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
                    grid_lcoe = 99
                    if year >= grid_reach[unelec]:
                        consumption = enerperhh[unelec]  # kWh/year
                        average_load = consumption / (1 - grid_calc.distribution_losses) / HOURS_PER_YEAR  # kW
                        peak_load = average_load / grid_calc.base_to_peak_load_ratio  # kW

                        node = (x[unelec], y[unelec])
                        closest_elec_node = closest_elec(node, elec_nodes2)
                        dist = haversine(x[electrified[closest_elec_node]], y[electrified[closest_elec_node]],
                                         x[unelec], y[unelec])
                        # dist = sqrt((x[electrified[closest_elec_node]] - x[unelec]) ** 2
                        #             + (y[electrified[closest_elec_node]] - y[unelec]) ** 2)
                        dist_adjusted = grid_penalty_ratio[unelec] * dist
                        prev_dist = cell_path_real[electrified[closest_elec_node]]
                        if dist + prev_dist < max_dist:
                            grid_lcoe = grid_calc.get_lcoe(energy_per_cell=enerperhh[unelec],
                                                           start_year=year - timestep,
                                                           end_year=end_year,
                                                           people=pop[unelec],
                                                           new_connections=new_connections[unelec],
                                                           total_energy_per_cell=total_energy_per_cell[unelec],
                                                           prev_code=prev_code[unelec],
                                                           num_people_per_hh=nupppphh[unelec],
                                                           grid_cell_area=grid_cell_area[unelec],
                                                           conf_status=confl[unelec],
                                                           travel_hours=travl[unelec],
                                                           additional_mv_line_length=dist_adjusted,
                                                           elec_loop=elecorder[electrified[closest_elec_node]] + 1)
                            if grid_lcoe < min_code_lcoes[unelec]:
                                if (grid_lcoe < new_lcoes[unelec]) and \
                                        (new_grid_capacity + peak_load < grid_capacity_limit):
                                    new_lcoes[unelec] = grid_lcoe
                                    cell_path_real[unelec] = dist + cell_path_real[electrified[closest_elec_node]]
                                    cell_path_adjusted[unelec] = dist_adjusted
                                    elecorder[unelec] = elecorder[electrified[closest_elec_node]] + 1
                                    new_grid_capacity += peak_load
                                    if unelec not in changes:
                                        changes.append(unelec)
                        elif new_grid_capacity + peak_load < grid_capacity_limit and 1 > 2:
                            electrified_hashed = self.get_unelectrified_rows(hash_table, unelec, x, y, max_dist)
                            grid_capacity_addition_loop = 0
                            for elec in electrified_hashed:
                                grid_lcoe = 99
                                prev_dist = cell_path_real[elec]
                                dist = haversine(x[elec], y[elec], x[unelec], y[unelec])
                                # dist = sqrt((x[elec] - x[unelec]) ** 2 + (y[elec] - y[unelec]) ** 2)
                                dist_adjusted = grid_penalty_ratio[unelec] * dist
                                if prev_dist + dist < max_dist:
                                    grid_lcoe = grid_calc.get_lcoe(energy_per_cell=enerperhh[unelec],
                                                                   start_year=year - timestep,
                                                                   end_year=end_year,
                                                                   people=pop[unelec],
                                                                   new_connections=new_connections[unelec],
                                                                   total_energy_per_cell=total_energy_per_cell[
                                                                       unelec],
                                                                   prev_code=prev_code[unelec],
                                                                   num_people_per_hh=nupppphh[unelec],
                                                                   grid_cell_area=grid_cell_area[unelec],
                                                                   conf_status=confl[unelec],
                                                                   travel_hours=travl[unelec],
                                                                   additional_mv_line_length=dist_adjusted,
                                                                   elec_loop=elecorder[elec] + 1)
                                    if grid_lcoe < min_code_lcoes[unelec]:
                                        if grid_lcoe < new_lcoes[unelec]:
                                            new_lcoes[unelec] = grid_lcoe
                                            cell_path_real[unelec] = dist + cell_path_real[elec]
                                            cell_path_adjusted[unelec] = dist_adjusted
                                            elecorder[unelec] = elecorder[elec] + 1
                                            if grid_capacity_addition_loop == 0:
                                                new_grid_capacity += peak_load
                                                grid_capacity_addition_loop += 1
                                            if unelec not in changes:
                                                changes.append(unelec)

            electrified = changes[:]
            unelectrified = set(unelectrified).difference(electrified)

        return new_lcoes, cell_path_adjusted, elecorder, cell_path_real

    def run_elec(self, grid_calc, max_dist, year, start_year, end_year, timestep, grid_cap_gen_limit):
        """
        Runs the grid extension algorithm
        """
        logging.info('Electrification algorithm starts running')
        # pre_elec_dist = 10000
        #         # self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)], self.df[SET_MV_CONNECT_DIST] = self.pre_new_lines(grid_calc, max_dist, year, start_year, end_year,
        #         #                                                               timestep, grid_cap_gen_limit)

        self.df[SET_LCOE_GRID + "{}".format(year)], self.df[SET_MIN_GRID_DIST + "{}".format(year)], self.df[
            SET_ELEC_ORDER + "{}".format(year)], self.df[SET_MV_CONNECT_DIST] = self.elec_extension(grid_calc, max_dist, year, start_year, end_year,
                                                                      timestep, grid_cap_gen_limit)

    def set_scenario_variables(self, year, num_people_per_hh_rural, num_people_per_hh_urban, time_step, start_year,
                               urban_elec_ratio, rural_elec_ratio, urban_tier, rural_tier, end_year_pop, productive_demand):
        """
        Set the basic scenario parameters that differ based on urban/rural
        So that they are in the table and can be read directly to calculate LCOEs
        """

        if end_year_pop == 0:
            self.df[SET_POP + "{}".format(year)] = self.df[SET_POP + "{}".format(year) + 'Low']
        else:
            self.df[SET_POP + "{}".format(year)] = self.df[SET_POP + "{}".format(year) + 'High']

        logging.info('Calculate new connections')
        # Calculate new connections for grid related purposes
        # REVIEW - This was changed based on your "newly created" column SET_ELEC_POP. Please review and check whether this creates any problem at your distribution_network function using people/new connections and energy_per_settlement/total_energy_per_settlement
        if year - time_step == start_year:
            # Assign new connections to those that are already electrified to a certain percent
            self.df.loc[(self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 1), SET_NEW_CONNECTIONS + "{}".format(year)] = \
                (self.df[SET_POP + "{}".format(year)] - self.df[SET_ELEC_POP])
            # Assign new connections to those that are not currently electrified
            self.df.loc[self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 0,
                        SET_NEW_CONNECTIONS + "{}".format(year)] = self.df[SET_POP + "{}".format(year)]
            # Some conditioning to eliminate negative values if existing by mistake
            self.df.loc[self.df[SET_NEW_CONNECTIONS + "{}".format(year)] < 0,
                        SET_NEW_CONNECTIONS + "{}".format(year)] = 0

            # self.df.loc[
            #     (self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 1) & (self.df[SET_URBAN] == 2),
            #     SET_NEW_CONNECTIONS + "{}".format(year)] = \
            #     (self.df[SET_POP + "{}".format(year)] - urban_elec_ratio * self.df['ElecPop'] / self.df[SET_POP] * self.df[SET_POP + "{}".format(year - time_step)])
            # self.df.loc[
            #     (self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year - time_step)] == 1) & (self.df[SET_URBAN] < 2),
            #     SET_NEW_CONNECTIONS + "{}".format(year)] = \
            #     (self.df[SET_POP + "{}".format(year)] - rural_elec_ratio * self.df['ElecPop'] / self.df[SET_POP] * self.df[
            #         SET_POP + "{}".format(year - time_step)])

        else:
            # Assign new connections to settlements that are already electrified
            self.df.loc[self.df[SET_LIMIT + "{}".format(year - time_step)] == 1,
                        SET_NEW_CONNECTIONS + "{}".format(year)] = \
                (self.df[SET_POP + "{}".format(year)] - self.df[SET_POP + "{}".format(year - time_step)])

            # Assign new connections to settlements that were initially electrified but not prioritized during the timestep
            self.df.loc[(self.df[SET_LIMIT + "{}".format(year - time_step)] == 0) &
                        (self.df[SET_ELEC_CURRENT] == 1),
                        SET_NEW_CONNECTIONS + "{}".format(year)] = self.df[SET_POP + "{}".format(year)] - self.df[SET_ELEC_POP]

            # Assing new connections to settlements that have not been electrified
            self.df.loc[(self.df[SET_LIMIT + "{}".format(year - time_step)] == 0) & (
                    self.df[SET_ELEC_CURRENT] == 0),
                        SET_NEW_CONNECTIONS + "{}".format(year)] = self.df[SET_POP + "{}".format(year)]

            # Some conditioning to eliminate negative values if existing by mistake
            self.df.loc[self.df[SET_NEW_CONNECTIONS + "{}".format(year)] < 0, SET_NEW_CONNECTIONS + "{}".format(year)] = 0

        logging.info('Setting electrification demand as per target per year')

        if max(self.df['PerCapitaDemand']) == 0:
            # RUN_PARAM: This shall be changed if different urban/rural categorization is decided
            wb_tier_urban_centers = int(urban_tier)
            wb_tier_urban_clusters = int(rural_tier)
            wb_tier_rural = int(rural_tier)

            # if max(self.df[SET_URBAN]) == 2:
            #     wb_tier_urban_centers = int(input('Enter the tier number for urban centers: '))
            #     wb_tier_urban_clusters = int(input('Enter the tier number for urban clusters: '))
            #     wb_tier_rural = int(input('Enter the tier number for rural: '))
            # else:
            #     wb_tier_urban_clusters = int(input('Enter the tier number for urban: '))
            #     wb_tier_rural = int(input('Enter the tier number for rural: '))
            #     wb_tier_urban_centers = 5

            if wb_tier_urban_centers == 6:
                wb_tier_urban_centers = 'Custom'
            if wb_tier_urban_clusters == 6:
                wb_tier_urban_clusters = 'Custom'
            if wb_tier_rural == 6:
                wb_tier_rural = 'Custom'

            self.df['PerCapitaDemand'] = 0

            # RUN_PARAM: This shall be changed if different urban/rural categorization is decided
            # Create new columns assigning number of people per household as per Urban/Rural type
            self.df.loc[self.df[SET_URBAN] == 0, SET_NUM_PEOPLE_PER_HH] = num_people_per_hh_rural
            self.df.loc[self.df[SET_URBAN] == 1, SET_NUM_PEOPLE_PER_HH] = num_people_per_hh_rural
            self.df.loc[self.df[SET_URBAN] == 2, SET_NUM_PEOPLE_PER_HH] = num_people_per_hh_urban

            # Define per capita residential demand
            # self.df['PerCapitaDemand'] = self.df['ResidentialDemandTier1.' + str(wb_tier_urban)]
            self.df.loc[self.df[SET_URBAN] == 0, 'PerCapitaDemand'] = self.df[
                'ResidentialDemandTier' + str(wb_tier_rural)]
            self.df.loc[self.df[SET_URBAN] == 1, 'PerCapitaDemand'] = self.df[
                'ResidentialDemandTier' + str(wb_tier_urban_clusters)]
            self.df.loc[self.df[SET_URBAN] == 2, 'PerCapitaDemand'] = self.df[
                'ResidentialDemandTier' + str(wb_tier_urban_centers)]
            # if max(self.df[SET_URBAN]) == 2:
            #     self.df.loc[self.df[SET_URBAN] == 2, 'PerCapitaDemand'] = self.df['ResidentialDemandTier1.' + str(wb_tier_urban_center)]

            # Add commercial demand
            # agri = True if 'y' in input('Include agrcultural demand? <y/n> ') else False
            # if agri:
            if int(productive_demand) == 1:
                self.df['PerCapitaDemand'] += self.df['AgriDemand']

            # commercial = True if 'y' in input('Include commercial demand? <y/n> ') else False
            #if commercial:
            if int(productive_demand) == 1:
                self.df['PerCapitaDemand'] += self.df['CommercialDemand']

            # health = True if 'y' in input('Include health demand? <y/n> ') else False
            # if health:
            if int(productive_demand) == 1:
                self.df['PerCapitaDemand'] += self.df['HealthDemand']

            # edu = True if 'y' in input('Include educational demand? <y/n> ') else False
            # if edu:
            if int(productive_demand) == 1:
                self.df['PerCapitaDemand'] += self.df['EducationDemand']

        self.df.loc[self.df[SET_URBAN] == 0, SET_ENERGY_PER_CELL + "{}".format(year)] = \
            self.df['PerCapitaDemand'] * self.df[SET_NEW_CONNECTIONS + "{}".format(year)]
        self.df.loc[self.df[SET_URBAN] == 1, SET_ENERGY_PER_CELL + "{}".format(year)] = \
            self.df['PerCapitaDemand'] * self.df[SET_NEW_CONNECTIONS + "{}".format(year)]
        self.df.loc[self.df[SET_URBAN] == 2, SET_ENERGY_PER_CELL + "{}".format(year)] = \
            self.df['PerCapitaDemand'] * self.df[SET_NEW_CONNECTIONS + "{}".format(year)]

        # if year - time_step == start_year:
        self.df.loc[self.df[SET_URBAN] == 0, SET_TOTAL_ENERGY_PER_CELL] = \
            self.df['PerCapitaDemand'] * self.df[SET_POP + "{}".format(year)]
        self.df.loc[self.df[SET_URBAN] == 1, SET_TOTAL_ENERGY_PER_CELL] = \
            self.df['PerCapitaDemand'] * self.df[SET_POP + "{}".format(year)]
        self.df.loc[self.df[SET_URBAN] == 2, SET_TOTAL_ENERGY_PER_CELL] = \
            self.df['PerCapitaDemand'] * self.df[SET_POP + "{}".format(year)]


    def grid_reach_estimate(self, start_year, gridspeed):
        """ Estimates the year of grid arrival based on geospatial characteristics 
        and grid expansion speed in km/year"""

        # logging.info('Estimate year of grid reach')
        # self.df[SET_GRID_REACH_YEAR] = 0
        # self.df.loc[self.df[SET_ELEC_FUTURE_GRID + "{}".format(start_year)] == 0, SET_GRID_REACH_YEAR] = \
        #     self.df['PlannedHVLineDist'] * self.df[SET_GRID_PENALTY] / gridspeed

        self.df[SET_GRID_REACH_YEAR] = \
            self.df.apply(lambda row: int(start_year +
                                          row['PlannedHVLineDist'] * row[SET_COMBINED_CLASSIFICATION] / gridspeed)
            if row[SET_ELEC_FUTURE_GRID + "{}".format(start_year)] == 0
            else start_year,
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
                additional_capacity = ((row[SET_NEW_CONNECTIONS + "{}".format(year)] *
                                        row[SET_ENERGY_PER_CELL + "{}".format(year)]) /
                                       (HOURS_PER_YEAR * mg_hydro_calc.capacity_factor *
                                        mg_hydro_calc.base_to_peak_load_ratio))

                # and add it to the tracking df
                hydro_df.loc[row[SET_HYDRO_FID], hydro_used] += additional_capacity

                # if it exceeds the available capacity, it's not an option
                if hydro_df.loc[row[SET_HYDRO_FID], hydro_used] > hydro_df.loc[row[SET_HYDRO_FID], SET_HYDRO]:
                    return 99

                else:
                    return mg_hydro_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                                  start_year=year - timestep,
                                                  end_year=end_year,
                                                  people=row[SET_POP + "{}".format(year)],
                                                  new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                                  total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                                  prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                                  num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                                  grid_cell_area=row['GridCellArea'],
                                                  conf_status=row[SET_CONFLICT],
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
                                            start_year=year - timestep,
                                            end_year=end_year,
                                            people=row[SET_POP + "{}".format(year)],
                                            new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                            total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                            prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                            num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                            grid_cell_area=row['GridCellArea'],
                                            conf_status=row[SET_CONFLICT],
                                            capacity_factor=row[SET_GHI] / HOURS_PER_YEAR)
            if row[SET_GHI] > 1000
            else 99, axis=1)

        logging.info('Calculate minigrid wind LCOE')
        self.df[SET_LCOE_MG_WIND + "{}".format(year)] = self.df.apply(
            lambda row: mg_wind_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                              start_year=year - timestep,
                                              end_year=end_year,
                                              people=row[SET_POP + "{}".format(year)],
                                              new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                              total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                              prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                              num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                              grid_cell_area=row['GridCellArea'],
                                              conf_status=row[SET_CONFLICT],
                                              capacity_factor=row[SET_WINDCF])
            if row[SET_WINDCF] > 0.1 else 99,
            axis=1)

        logging.info('Calculate minigrid diesel LCOE')
        self.df[SET_LCOE_MG_DIESEL + "{}".format(year)] = self.df.apply(
            lambda row: mg_diesel_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                                start_year=year - timestep,
                                                end_year=end_year,
                                                people=row[SET_POP + "{}".format(year)],
                                                new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                                total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                                prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                                num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                                grid_cell_area=row['GridCellArea'],
                                                conf_status=row[SET_CONFLICT],
                                                travel_hours=row[SET_TRAVEL_HOURS]), axis=1)

        logging.info('Calculate standalone diesel LCOE')
        self.df[SET_LCOE_SA_DIESEL + "{}".format(year)] = self.df.apply(
            lambda row: sa_diesel_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                                start_year=year - timestep,
                                                end_year=end_year,
                                                people=row[SET_POP + "{}".format(year)],
                                                new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                                total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                                prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                                num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                                grid_cell_area=row['GridCellArea'],
                                                conf_status=row[SET_CONFLICT],
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
                                            grid_cell_area=row['GridCellArea'],
                                            conf_status=row[SET_CONFLICT],
                                            capacity_factor=row[SET_GHI] / HOURS_PER_YEAR) if row[SET_GHI] > 1000
            else 99,
            axis=1)

        logging.info('Determine minimum technology (off-grid)')
        self.df[SET_MIN_OFFGRID + "{}".format(year)] = self.df[[SET_LCOE_SA_DIESEL + "{}".format(year),
                                                                SET_LCOE_SA_PV + "{}".format(year),
                                                                SET_LCOE_MG_WIND + "{}".format(year),
                                                                SET_LCOE_MG_DIESEL + "{}".format(year),
                                                                SET_LCOE_MG_PV + "{}".format(year),
                                                                SET_LCOE_MG_HYDRO + "{}".format(year)]].T.idxmin()

        logging.info('Determine minimum tech LCOE')
        # self.df[SET_MIN_OFFGRID_LCOE + "{}".format(year)] = \
        #     self.df.apply(lambda row: (row[row[SET_MIN_OFFGRID + "{}".format(year)]]), axis=1)
        self.df[SET_MIN_OFFGRID_LCOE + "{}".format(year)] = self.df[[SET_LCOE_SA_DIESEL + "{}".format(year),
                                                                SET_LCOE_SA_PV + "{}".format(year),
                                                                SET_LCOE_MG_WIND + "{}".format(year),
                                                                SET_LCOE_MG_DIESEL + "{}".format(year),
                                                                SET_LCOE_MG_PV + "{}".format(year),
                                                                SET_LCOE_MG_HYDRO + "{}".format(year)]].T.min()


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

    def results_columns(self, mg_hydro_calc, mg_wind_calc, mg_pv_calc,
                        sa_pv_calc, mg_diesel_calc, sa_diesel_calc, grid_calc, year):
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
        # self.df[SET_MIN_OVERALL_LCOE + "{}".format(year)] = \
        #     self.df.apply(lambda row: (row[row[SET_MIN_OVERALL + "{}".format(year)]]), axis=1)
        self.df[SET_MIN_OVERALL_LCOE + "{}".format(year)] = self.df[[SET_LCOE_GRID + "{}".format(year),
                                                                     SET_LCOE_SA_DIESEL + "{}".format(year),
                                                                     SET_LCOE_SA_PV + "{}".format(year),
                                                                     SET_LCOE_MG_WIND + "{}".format(year),
                                                                     SET_LCOE_MG_DIESEL + "{}".format(year),
                                                                     SET_LCOE_MG_PV + "{}".format(year),
                                                                     SET_LCOE_MG_HYDRO + "{}".format(year)]].T.min()

        logging.info('Add technology codes')
        codes = {SET_LCOE_GRID + "{}".format(year): 1,
                 SET_LCOE_MG_HYDRO + "{}".format(year): 7,
                 SET_LCOE_MG_WIND + "{}".format(year): 6,
                 SET_LCOE_MG_PV + "{}".format(year): 5,
                 SET_LCOE_MG_DIESEL + "{}".format(year): 4,
                 SET_LCOE_SA_DIESEL + "{}".format(year): 2,
                 SET_LCOE_SA_PV + "{}".format(year): 3}

        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_GRID + "{}".format(year),
                    SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_GRID + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_HYDRO + "{}".format(year),
                    SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_MG_HYDRO + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_SA_PV + "{}".format(year),
                    SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_SA_PV + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_WIND + "{}".format(year),
                    SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_MG_WIND + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_PV + "{}".format(year),
                    SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_MG_PV + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_MG_DIESEL + "{}".format(year),
                    SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_MG_DIESEL + "{}".format(year)]
        self.df.loc[self.df[SET_MIN_OVERALL + "{}".format(year)] == SET_LCOE_SA_DIESEL + "{}".format(year),
                    SET_MIN_OVERALL_CODE + "{}".format(year)] = codes[SET_LCOE_SA_DIESEL + "{}".format(year)]

    def calculate_investments(self, mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc,
                              sa_diesel_calc, grid_calc, year, end_year, timestep):
        def res_investment_cost(row):
            min_code = row[SET_MIN_OVERALL_CODE + "{}".format(year)]

            if min_code == 2:
                return sa_diesel_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                               start_year=year - timestep,
                                               end_year=end_year,
                                               people=row[SET_POP + "{}".format(year)],
                                               new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                               total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                               prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                               num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                               grid_cell_area=row['GridCellArea'],
                                               travel_hours=row[SET_TRAVEL_HOURS],
                                               conf_status=row[SET_CONFLICT],
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
                                           grid_cell_area=row['GridCellArea'],
                                           capacity_factor=row[SET_GHI] / HOURS_PER_YEAR,
                                           conf_status=row[SET_CONFLICT],
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
                                             grid_cell_area=row['GridCellArea'],
                                             capacity_factor=row[SET_WINDCF],
                                             conf_status=row[SET_CONFLICT],
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
                                               grid_cell_area=row['GridCellArea'],
                                               travel_hours=row[SET_TRAVEL_HOURS],
                                               conf_status=row[SET_CONFLICT],
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
                                           grid_cell_area=row['GridCellArea'],
                                           capacity_factor=row[SET_GHI] / HOURS_PER_YEAR,
                                           conf_status=row[SET_CONFLICT],
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
                                              grid_cell_area=row['GridCellArea'],
                                              conf_status=row[SET_CONFLICT],
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
                                          grid_cell_area=row['GridCellArea'],
                                          conf_status=row[SET_CONFLICT],
                                          additional_mv_line_length=row[SET_MIN_GRID_DIST + "{}".format(year)],
                                          elec_loop=row[SET_ELEC_ORDER + "{}".format(year)],
                                          get_investment_cost=True)
            else:
                return 0

        logging.info('Calculate investment cost')
        self.df[SET_INVESTMENT_COST + "{}".format(year)] = self.df.apply(res_investment_cost, axis=1)

    def apply_limitations(self, eleclimit, year, timestep, prioritization):

        logging.info('Determine electrification limits')

        if eleclimit == 1:
            self.df[SET_LIMIT + "{}".format(year)] = 1
            elecrate = 1
        else:
            choice = int(prioritization)
            self.df[SET_LIMIT + "{}".format(year)] = 0

            #RUN_PARAM: Here one can modify the prioritization algorithm - Currently only the first option is reviewed and ready to be used
            # REVIEW - In some cases the electrification cannot be well calibrated e.g. check Malawi at 40% access rate. As it is now, it either reaches 33% or 51%
            #TODO We might need to add a step in which newly electrified cells get x% of access (x<100) so that we better calibrate the process
            if choice == 1:  # Prioritize grid intensification first, then lowest investment per capita in combination with dist to cities for better calibration
                elecrate = 0
                min_investment = 0
                min_dist_to_cities = 5
                iter_limit_1 = 0
                iter_limit_2 = 0
                self.df[SET_INVEST_PER_CAPITA + "{}".format(year)] = self.df[SET_INVESTMENT_COST + "{}".format(year)] / \
                                                                     self.df[SET_NEW_CONNECTIONS + "{}".format(year)]
                if sum(self.df[self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 1][SET_POP + "{}".format(year)]) / \
                        self.df[SET_POP + "{}".format(year)].sum() < eleclimit:
                    eleclimit -= sum(self.df[self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 1][SET_POP + "{}".format(year)]) / \
                                 self.df[SET_POP + "{}".format(year)].sum()

                    while abs(elecrate - eleclimit) > 0.01:
                        elecrate = sum(self.df[(self.df[SET_INVEST_PER_CAPITA + "{}".format(year)] < min_investment) &
                                               (self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 0) &
                                               (self.df[SET_TRAVEL_HOURS] < min_dist_to_cities)][SET_POP + "{}".format(year)]) / \
                                   self.df[SET_POP + "{}".format(year)].sum()
                        if eleclimit - elecrate > 0.05:
                            min_investment += 0.5
                        elif ((eleclimit - elecrate) > 0) and ((eleclimit - elecrate) <= 0.05) and (iter_limit_1 != 50):
                            min_dist_to_cities += 0.5
                            iter_limit_1 += 1
                        elif ((eleclimit - elecrate) < 0) and ((eleclimit - elecrate) > -0.05) and (iter_limit_2 != 50):
                            if min_dist_to_cities > 0:
                                min_dist_to_cities -= 0.5
                                iter_limit_2 += 1
                            else:
                                print("Further modification is needed in the limitation algorithm as goals is difficult to reach with the existing assumptions")
                                break
                        else:
                            print(
                                "Further modification is needed in the limitation algorithm as goals is difficult to reach with the existing assumptions")
                            break

                    # Updating (using the SET_LIMIT function) what is electrified in the year and what is not
                    self.df.loc[(self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 1), SET_LIMIT + "{}".format(year)] = 1

                    self.df.loc[(self.df[SET_INVEST_PER_CAPITA + "{}".format(year)] <= min_investment) &
                                (self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 0) &
                                (self.df[SET_TRAVEL_HOURS] <= min_dist_to_cities), SET_LIMIT + "{}".format(year)] = 1

                    self.df.loc[(self.df[SET_INVEST_PER_CAPITA + "{}".format(year)] <= min_investment) &
                                (self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 0) &
                                (self.df[SET_TRAVEL_HOURS] > min_dist_to_cities), SET_LIMIT + "{}".format(year)] = 0

                    self.df.loc[(self.df[SET_INVEST_PER_CAPITA + "{}".format(year)] > min_investment) &
                                (self.df[SET_ELEC_FUTURE_GRID + "{}".format(
                                    year - timestep)] == 0), SET_LIMIT + "{}".format(year)] = 0

                    elecrate = self.df.loc[self.df[SET_LIMIT + "{}".format(year)] == 1, SET_POP + "{}".format(year)].sum() / \
                               self.df[SET_POP + "{}".format(year)].sum()
                else:
                    print("The electrification target set is quite low and has been reached by grid intensification in already electrified areas")
                    self.df.loc[(self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 1), SET_LIMIT + "{}".format(year)] = 1
                    self.df.loc[(self.df[SET_ELEC_FUTURE_GRID + "{}".format(year - timestep)] == 0), SET_LIMIT + "{}".format(year)] = 0

                    elecrate = self.df.loc[self.df[SET_LIMIT + "{}".format(year)] == 1, SET_POP + "{}".format(year)].sum() / \
                               self.df[SET_POP + "{}".format(year)].sum()

            # TODO The algorithm needs to be updated
            # Review is required
            elif choice == 2:
                elecrate = 0
                min_investment = 0
                self.df[SET_INVEST_PER_CAPITA + "{}".format(year)] = self.df[SET_INVESTMENT_COST + "{}".format(year)] / \
                                                                     self.df[SET_NEW_CONNECTIONS + "{}".format(year)]
                while elecrate < eleclimit:
                    elecrate = sum(self.df[self.df[SET_INVEST_PER_CAPITA + "{}".format(year)] < min_investment][
                                       SET_POP + "{}".format(year)]) / self.df[SET_POP + "{}".format(year)].sum()
                    if elecrate < 0.999 * eleclimit:
                        min_investment += 1
                    else:
                        break
                self.df.loc[
                    self.df[SET_INVEST_PER_CAPITA + "{}".format(year)] <= min_investment, SET_LIMIT + "{}".format(
                        year)] = 1
                self.df.loc[
                    self.df[SET_INVEST_PER_CAPITA + "{}".format(year)] > min_investment, SET_LIMIT + "{}".format(
                        year)] = 0

            # TODO The algorithm needs to be updated
            # Review is required
            elif choice == 3:  # Prioritize lowest LCOE (Not tested)
                elecrate = 1
                min_lcoe = 0
                while elecrate >= eleclimit:
                    elecrate = sum(self.df[self.df[SET_MIN_OVERALL_LCOE + "{}".format(year)] < min_lcoe][
                                       SET_POP + "{}".format(year)]) / self.df[SET_POP + "{}".format(year)].sum()
                    if elecrate > 1.001 * eleclimit:
                        min_lcoe += 0.001
                    else:
                        break
                self.df.loc[
                    self.df[SET_MIN_OVERALL_LCOE + "{}".format(year)] <= min_lcoe, SET_LIMIT + "{}".format(year)] = 1
                self.df.loc[
                    self.df[SET_MIN_OVERALL_LCOE + "{}".format(year)] > min_lcoe, SET_LIMIT + "{}".format(year)] = 0

            # TODO The algorithm needs to be updated
            # Review is required
            elif choice == 4:  # Old method
                self.df[SET_LIMIT + "{}".format(year)] = \
                    self.df.apply(lambda row: 1 if row[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] == 1 else 0, axis=1)
                conflictlimit = self.df[SET_CONFLICT].min()
                mintraveldistance = self.df[SET_TRAVEL_HOURS].min()
                # max_loop = self.df[SET_ELEC_ORDER + "{}".format(year)].max()
                max_loop = 0
                iteration = 0

                elecrate = sum(self.df[self.df[SET_LIMIT + "{}".format(year)] == 1][SET_POP + "{}".format(year)]) / \
                           self.df[SET_POP + "{}".format(year)].sum()

                if elecrate < eleclimit:
                    still_looking = True
                else:
                    still_looking = False
                    print("The investment cap does not allow further electrification expansion in year:{}".format(year))
                elec_loop = 99
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
                                    (self.df[SET_CONFLICT] <= conflictlimit), SET_LIMIT + "{}".format(year)] = 1

                    elecrate = sum(self.df[self.df[SET_LIMIT + "{}".format(year)] == 1][SET_POP + "{}".format(year)]) / \
                               self.df[SET_POP + "{}".format(year)].sum()

                    iteration += 1

                    if elecrate < 0.9999 * eleclimit:
                        mintraveldistance += 0.05
                        if iteration > 100:
                            mintraveldistance += 0.05
                        if iteration > 200:
                            mintraveldistance += 0.95
                        if iteration > 300:
                            iteration = 0
                            conflictlimit += 1
                            mintraveldistance = self.df[SET_TRAVEL_HOURS].min()
                            if conflictlimit > 0:
                                elec_loop += 1
                    else:
                        still_looking = False

        print("The electrification rate achieved in {} is {:.1f} %".format(year, elecrate*100))


    def final_decision(self, mg_hydro_calc, mg_wind_calc, mg_pv_calc, sa_pv_calc, mg_diesel_calc,
                       sa_diesel_calc, grid_calc, year, end_year, timestep):
        """" ... """

        logging.info('Determine final electrification decision')

        # self.df[SET_ELEC_FINAL_GRID + "{}".format(year)] = \
        #         #     self.df.apply(lambda row: 1
        #         #     if (row[SET_ELEC_FUTURE_GRID + "{}".format(year)] == 1) or
        #         #        (row[SET_LIMIT + "{}".format(year)] == 1 and
        #         #         row[SET_MIN_OVERALL_CODE + "{}".format(year)] == 1 and
        #         #         row[SET_GRID_REACH_YEAR] <= year)
        #         #     else 0, axis=1)
        #         # self.df[SET_ELEC_FINAL_OFFGRID + "{}".format(year)] = \
        #         #     self.df.apply(lambda row: 1
        #         #     if (row[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] == 1 and
        #         #         row[SET_MIN_OVERALL_CODE + "{}".format(year)] != 1) or
        #         #        (row[SET_LIMIT + "{}".format(year)] == 1 and
        #         #         row[SET_ELEC_FINAL_GRID + "{}".format(year)] == 0) or
        #         #        (row[SET_LIMIT + "{}".format(year)] == 1 and
        #         #         row[SET_MIN_OVERALL_CODE + "{}".format(
        #         #             year)] == 1 and
        #         #         row[SET_GRID_REACH_YEAR] > year)
        #         #     else 0, axis=1)

        # Defining what is electrified in a given year by the grid after prioritization process has finished
        self.df[SET_ELEC_FINAL_GRID + "{}".format(year)] = 0
        self.df.loc[(self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)] == 1), SET_ELEC_FINAL_GRID + "{}".format(year)] = 1
        self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 1) & (self.df[SET_MIN_OVERALL_CODE + "{}".format(year)] == 1) & (self.df[SET_GRID_REACH_YEAR] <= year), SET_ELEC_FINAL_GRID + "{}".format(year)] = 1
       # Define what is electrified in a given year by off-grid after prioritization process has finished
        self.df[SET_ELEC_FINAL_OFFGRID + "{}".format(year)] = 0
        self.df.loc[(self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)] == 1) & (self.df[SET_MIN_OVERALL_CODE + "{}".format(year)] != 1), SET_ELEC_FINAL_OFFGRID + "{}".format(year)] = 1
        self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 1) & (self.df[SET_ELEC_FINAL_GRID + "{}".format(year)] == 0), SET_ELEC_FINAL_OFFGRID + "{}".format(year)] = 1
        self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 1) & (self.df[SET_MIN_OVERALL_CODE + "{}".format(year)] == 0) & (self.df[SET_GRID_REACH_YEAR] > year), SET_ELEC_FINAL_OFFGRID + "{}".format(year)] = 1

        #
        self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 1) & (self.df[SET_ELEC_FINAL_GRID + "{}".format(year)] == 1),
                    SET_ELEC_FINAL_CODE + "{}".format(year)] = 1

        self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 1) & (self.df[SET_ELEC_FINAL_OFFGRID + "{}".format(year)] == 1),
                    SET_ELEC_FINAL_CODE + "{}".format(year)] = self.df[SET_MIN_OFFGRID_CODE + "{}".format(year)]

        self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 0),
                    SET_ELEC_FINAL_CODE + "{}".format(year)] = 99

        # self.df.loc[(self.df[SET_LIMIT + "{}".format(year)] == 0) &
        #             (self.df[SET_ELEC_FINAL_GRID + "{}".format(year)] == 0) &
        #             (self.df[SET_ELEC_FINAL_OFFGRID + "{}".format(year)] == 0),
        #             SET_ELEC_FINAL_CODE + "{}".format(year)] = 99

        logging.info('Calculate new capacity')

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 1, SET_NEW_CAPACITY + "{}".format(year)] = (
                (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
                (HOURS_PER_YEAR * grid_calc.capacity_factor * grid_calc.base_to_peak_load_ratio *
                 (1 - grid_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 7, SET_NEW_CAPACITY + "{}".format(year)] = (
                (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
                (HOURS_PER_YEAR * mg_hydro_calc.capacity_factor * mg_hydro_calc.base_to_peak_load_ratio *
                 (1 - mg_hydro_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 5, SET_NEW_CAPACITY + "{}".format(year)] = (
                (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
                (HOURS_PER_YEAR * (self.df[SET_GHI] / HOURS_PER_YEAR) * mg_pv_calc.base_to_peak_load_ratio *
                 (1 - mg_pv_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 6, SET_NEW_CAPACITY + "{}".format(year)] = (
                (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
                (HOURS_PER_YEAR * self.df[SET_WINDCF] * mg_wind_calc.base_to_peak_load_ratio *
                 (1 - mg_wind_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 4, SET_NEW_CAPACITY + "{}".format(year)] = (
                (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
                (HOURS_PER_YEAR * mg_diesel_calc.capacity_factor * mg_diesel_calc.base_to_peak_load_ratio *
                 (1 - mg_diesel_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 2, SET_NEW_CAPACITY + "{}".format(year)] = (
                (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
                (HOURS_PER_YEAR * sa_diesel_calc.capacity_factor * sa_diesel_calc.base_to_peak_load_ratio *
                 (1 - sa_diesel_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 3, SET_NEW_CAPACITY + "{}".format(year)] = (
                (self.df[SET_ENERGY_PER_CELL + "{}".format(year)]) /
                (HOURS_PER_YEAR * (self.df[SET_GHI] / HOURS_PER_YEAR) * sa_pv_calc.base_to_peak_load_ratio *
                 (1 - sa_pv_calc.distribution_losses)))

        self.df.loc[self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 99, SET_NEW_CAPACITY + "{}".format(year)] = 0

        def res_investment_cost(row):
            min_code = row[SET_ELEC_FINAL_CODE + "{}".format(year)]

            if min_code == 2:
                return sa_diesel_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                               start_year=year - timestep,
                                               end_year=end_year,
                                               people=row[SET_POP + "{}".format(year)],
                                               new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                               total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                               prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                               num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                               grid_cell_area=row['GridCellArea'],
                                               travel_hours=row[SET_TRAVEL_HOURS],
                                               conf_status=row[SET_CONFLICT],
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
                                           grid_cell_area=row['GridCellArea'],
                                           capacity_factor=row[SET_GHI] / HOURS_PER_YEAR,
                                           conf_status=row[SET_CONFLICT],
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
                                             grid_cell_area=row['GridCellArea'],
                                             capacity_factor=row[SET_WINDCF],
                                             conf_status=row[SET_CONFLICT],
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
                                               grid_cell_area=row['GridCellArea'],
                                               travel_hours=row[SET_TRAVEL_HOURS],
                                               conf_status=row[SET_CONFLICT],
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
                                           grid_cell_area=row['GridCellArea'],
                                           capacity_factor=row[SET_GHI] / HOURS_PER_YEAR,
                                           conf_status=row[SET_CONFLICT],
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
                                              grid_cell_area=row['GridCellArea'],
                                              conf_status=row[SET_CONFLICT],
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
                                          grid_cell_area=row['GridCellArea'],
                                          conf_status=row[SET_CONFLICT],
                                          additional_mv_line_length=row[SET_MIN_GRID_DIST + "{}".format(year)],
                                          elec_loop=row[SET_ELEC_ORDER + "{}".format(year)],
                                          get_investment_cost=True)
            else:
                return 0

            logging.info('Calculate investment cost')
            self.df[SET_INVESTMENT_COST + "{}".format(year)] = self.df.apply(res_investment_cost, axis=1)

        def res_investment_cost_lv(row):
            min_code = row[SET_ELEC_FINAL_CODE + "{}".format(year)]
            if min_code == 1:
                return grid_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                          start_year=year - timestep,
                                          end_year=end_year,
                                          people=row[SET_POP + "{}".format(year)],
                                          new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                          total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                          prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                          num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                          grid_cell_area=row['GridCellArea'],
                                          conf_status=row[SET_CONFLICT],
                                          additional_mv_line_length=row[SET_MIN_GRID_DIST + "{}".format(year)],
                                          elec_loop=row[SET_ELEC_ORDER + "{}".format(year)],
                                          get_investment_cost_lv=True)
            else:
                return 0

        logging.info('Calculate LV investment cost')
        # self.df['InvestmentCostLV' + "{}".format(year)] = self.df.apply(res_investment_cost_lv, axis=1)

        def res_investment_cost_mv(row):
            min_code = row[SET_ELEC_FINAL_CODE + "{}".format(year)]
            if min_code == 1:
                return grid_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                          start_year=year - timestep,
                                          end_year=end_year,
                                          people=row[SET_POP + "{}".format(year)],
                                          new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                          total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                          prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                          num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                          grid_cell_area=row['GridCellArea'],
                                          conf_status=row[SET_CONFLICT],
                                          additional_mv_line_length=row[SET_MIN_GRID_DIST + "{}".format(year)],
                                          elec_loop=row[SET_ELEC_ORDER + "{}".format(year)],
                                          get_investment_cost_mv=True)
            else:
                return 0

        logging.info('Calculate MV investment cost')
        # self.df['InvestmentCostMV' + "{}".format(year)] = self.df.apply(res_investment_cost_mv, axis=1)

        def res_investment_cost_hv(row):
            min_code = row[SET_ELEC_FINAL_CODE + "{}".format(year)]
            if min_code == 1:
                return grid_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                          start_year=year - timestep,
                                          end_year=end_year,
                                          people=row[SET_POP + "{}".format(year)],
                                          new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                          total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                          prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                          num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                          grid_cell_area=row['GridCellArea'],
                                          conf_status=row[SET_CONFLICT],
                                          additional_mv_line_length=row[SET_MIN_GRID_DIST + "{}".format(year)],
                                          elec_loop=row[SET_ELEC_ORDER + "{}".format(year)],
                                          get_investment_cost_hv=True)
            else:
                return 0

        logging.info('Calculate HV investment cost')
        # self.df['InvestmentCostHV' + "{}".format(year)] = self.df.apply(res_investment_cost_hv, axis=1)

        def res_investment_cost_transformer(row):
            min_code = row[SET_ELEC_FINAL_CODE + "{}".format(year)]
            if min_code == 1:
                return grid_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                          start_year=year - timestep,
                                          end_year=end_year,
                                          people=row[SET_POP + "{}".format(year)],
                                          new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                          total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                          prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                          num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                          grid_cell_area=row['GridCellArea'],
                                          conf_status=row[SET_CONFLICT],
                                          additional_mv_line_length=row[SET_MIN_GRID_DIST + "{}".format(year)],
                                          elec_loop=row[SET_ELEC_ORDER + "{}".format(year)],
                                          get_investment_cost_transformer=True)
            else:
                return 0

        logging.info('Calculate transformer investment cost')
        # self.df['InvestmentCostTransformer' + "{}".format(year)] = self.df.apply(res_investment_cost_transformer, axis=1)

        def res_investment_cost_connection(row):
            min_code = row[SET_ELEC_FINAL_CODE + "{}".format(year)]
            if min_code == 1:
                return grid_calc.get_lcoe(energy_per_cell=row[SET_ENERGY_PER_CELL + "{}".format(year)],
                                          start_year=year - timestep,
                                          end_year=end_year,
                                          people=row[SET_POP + "{}".format(year)],
                                          new_connections=row[SET_NEW_CONNECTIONS + "{}".format(year)],
                                          total_energy_per_cell=row[SET_TOTAL_ENERGY_PER_CELL],
                                          prev_code=row[SET_ELEC_FINAL_CODE + "{}".format(year - timestep)],
                                          num_people_per_hh=row[SET_NUM_PEOPLE_PER_HH],
                                          grid_cell_area=row['GridCellArea'],
                                          conf_status=row[SET_CONFLICT],
                                          additional_mv_line_length=row[SET_MIN_GRID_DIST + "{}".format(year)],
                                          elec_loop=row[SET_ELEC_ORDER + "{}".format(year)],
                                          get_investment_cost_connection=True)
            else:
                return 0

        logging.info('Calculate connection investment cost')
       #  self.df['InvestmentCostConnection' + "{}".format(year)] = self.df.apply(res_investment_cost_connection, axis=1)

        def infrastructure_cost(row):
            if row[SET_NEW_CONNECTIONS + "{}".format(year)] > 0 and row[SET_ELEC_FINAL_CODE + "{}".format(year)] == 1:
                return (row['InvestmentCostLV' + "{}".format(year)]
                        + row['InvestmentCostMV' + "{}".format(year)] + row['InvestmentCostHV' + "{}".format(year)]
                        + row['InvestmentCostTransformer' + "{}".format(year)] +
                        row['InvestmentCostConnection' + "{}".format(year)]) / (
                               row[SET_NEW_CONNECTIONS + "{}".format(year)] / row[SET_NUM_PEOPLE_PER_HH])
            else:
                return 0

        logging.info('Calculating average infrastructure cost for grid connection')
        # self.df['InfrastructureCapitaCost' + "{}".format(year)] = self.df.apply(infrastructure_cost, axis=1)

        # TODO this is not correct. It creates problems in certain occasions. I have excluded it from the code. In case it doesn't interfere with any additions you made I suggest deleting
        # Update the actual electrification column with results
        #self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)] = self.df[SET_LIMIT + "{}".format(year)]

    def delete_redundant_columns(self, year):
        self.df.fillna(0)
        self.df['ResultsNoTimestep'] = self.df[SET_ELEC_FINAL_CODE + "{}".format(year)]
        del self.df[SET_ELEC_FINAL_CODE + "{}".format(year)]
        del self.df[SET_LCOE_MG_HYDRO + "{}".format(year)]
        del self.df[SET_LCOE_MG_PV + "{}".format(year)]
        del self.df[SET_LCOE_MG_WIND + "{}".format(year)]
        del self.df[SET_LCOE_MG_DIESEL + "{}".format(year)]
        del self.df[SET_LCOE_SA_DIESEL + "{}".format(year)]
        del self.df[SET_LCOE_SA_PV + "{}".format(year)]
        del self.df[SET_MIN_OFFGRID + "{}".format(year)]
        del self.df[SET_MIN_OFFGRID_LCOE + "{}".format(year)]
        del self.df[SET_MIN_OFFGRID_CODE + "{}".format(year)]
        del self.df[SET_ELEC_FUTURE_GRID + "{}".format(year)]
        del self.df[SET_ELEC_FUTURE_OFFGRID + "{}".format(year)]
        del self.df[SET_ELEC_FUTURE_ACTUAL + "{}".format(year)]
        del self.df[SET_LCOE_GRID + "{}".format(year)]
        del self.df[SET_MIN_GRID_DIST + "{}".format(year)]
        del self.df[SET_ELEC_ORDER + "{}".format(year)]
        del self.df[SET_MIN_OVERALL + "{}".format(year)]
        del self.df[SET_MIN_OVERALL_LCOE + "{}".format(year)]
        del self.df[SET_MIN_OVERALL_CODE + "{}".format(year)]
        del self.df[SET_LIMIT + "{}".format(year)]
        del self.df[SET_ELEC_FINAL_GRID + "{}".format(year)]
        del self.df[SET_ELEC_FINAL_OFFGRID + "{}".format(year)]
        del self.df[SET_NEW_CAPACITY + "{}".format(year)]
        del self.df[SET_INVESTMENT_COST + "{}".format(year)]
        del self.df[SET_NEW_CONNECTIONS + "{}".format(year)]
        del self.df[SET_ENERGY_PER_CELL + "{}".format(year)]

    def calc_summaries(self, df_summary, sumtechs, year):

        """The next section calculates the summaries for technology split, 
        consumption added and total investment cost"""

        logging.info('Calculate summaries')

        # Population Summaries

        df_summary[year][sumtechs[0]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 1) &
                                                        (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                            [SET_POP + "{}".format(year)])

        df_summary[year][sumtechs[1]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 2) &
                                                        (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                            [SET_POP + "{}".format(year)])

        df_summary[year][sumtechs[2]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 3) &
                                                        (self.df[SET_LIMIT + "{}".format(year)] == 1) & (self.df[SET_POP + "{}".format(year)] > 0)]
                                            [SET_POP + "{}".format(year)])

        df_summary[year][sumtechs[3]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 4) &
                                                        (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                            [SET_POP + "{}".format(year)])

        df_summary[year][sumtechs[4]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 5) &
                                                        (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                            [SET_POP + "{}".format(year)])

        df_summary[year][sumtechs[5]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 6) &
                                                        (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                            [SET_POP + "{}".format(year)])

        df_summary[year][sumtechs[6]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 7) &
                                                        (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                            [SET_POP + "{}".format(year)])

        # New_Connection Summaries

        df_summary[year][sumtechs[7]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 1) &
                                                        (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                            [SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[8]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 2) &
                                                        (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                            [SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[9]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 3) &
                                                        (self.df[SET_LIMIT + "{}".format(year)] == 1) & (self.df[SET_POP + "{}".format(year)] > 0)]
                                            [SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[10]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 4) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[11]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 5) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[12]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 6) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_NEW_CONNECTIONS + "{}".format(year)])

        df_summary[year][sumtechs[13]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 7) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_NEW_CONNECTIONS + "{}".format(year)])

        # Capacity Summaries

        df_summary[year][sumtechs[14]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 1) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_NEW_CAPACITY + "{}".format(year)])

        df_summary[year][sumtechs[15]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 2) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_NEW_CAPACITY + "{}".format(year)])

        df_summary[year][sumtechs[16]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 3) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1) & (self.df[SET_POP + "{}".format(year)] > 0)]
                                             [SET_NEW_CAPACITY + "{}".format(year)])

        df_summary[year][sumtechs[17]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 4) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_NEW_CAPACITY + "{}".format(year)])

        df_summary[year][sumtechs[18]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 5) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_NEW_CAPACITY + "{}".format(year)])

        df_summary[year][sumtechs[19]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 6) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_NEW_CAPACITY + "{}".format(year)])

        df_summary[year][sumtechs[20]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 7) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_NEW_CAPACITY + "{}".format(year)])

        # Investment Summaries

        df_summary[year][sumtechs[21]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 1) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[22]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 2) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[23]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 3) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1) & (self.df[SET_POP + "{}".format(year)] > 0)]
                                             [SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[24]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 4) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[25]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 5) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[26]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 6) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[27]] = sum(self.df.loc[(self.df[SET_ELEC_FINAL_CODE + "{}".format(year)] == 7) &
                                                         (self.df[SET_LIMIT + "{}".format(year)] == 1)]
                                             [SET_INVESTMENT_COST + "{}".format(year)])

        df_summary[year][sumtechs[28]] = min(self.df[SET_POP + "{}".format(year)])
        df_summary[year][sumtechs[29]] = max(self.df[SET_POP + "{}".format(year)])
        df_summary[year][sumtechs[30]] = min(self.df['GridCellArea'])
        df_summary[year][sumtechs[31]] = max(self.df['GridCellArea'])
        df_summary[year][sumtechs[32]] = min(self.df['CurrentMVLineDist'])
        df_summary[year][sumtechs[33]] = max(self.df['CurrentMVLineDist'])
        df_summary[year][sumtechs[34]] = min(self.df[SET_ROAD_DIST])
        df_summary[year][sumtechs[35]] = max(self.df[SET_ROAD_DIST])
        df_summary[year][sumtechs[36]] = min((self.df[SET_INVESTMENT_COST + "{}".format(year)]) / (self.df[SET_NEW_CONNECTIONS + "{}".format(year)]))
        df_summary[year][sumtechs[37]] = max((self.df[SET_INVESTMENT_COST + "{}".format(year)]) / (self.df[SET_NEW_CONNECTIONS + "{}".format(year)]))


