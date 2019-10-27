from .CCDefaults import getDefault, getLocality
from .CCConstants import YES, NO, FRACTIONS
from .naturalGas import GasFootprint

MONTHLY_ELEC = "monthly_elec_bill"
ELECTRIC_UTILITY = "electric_utility"
def EvalCommunitySolar(inputs):
    """ 
    Community Solar - allows MA residents to go solar without getting panels of their own
    Homeowners or businesses purchase a subscription to a project, and receive a share of the solar energy supply
    Solar credits are applied to the utility bill to reduce it's cost

    [1] two different CSS models: “public lease” and “participant ownership.” 

    Refs:
    1. https://blog.mass.gov/energy/renewables/community-shared-solar-101/
    2. https://www.solar-estimate.org/news/community-solar-massachusetts
    3. https://www.clearwaycommunitysolar.com/savings-calculator/

    """
    #inputs: community_solar,monthly_elec,electric_utility
    points = cost = savings = 0.
    locality = getLocality(inputs)

    explanation = "Didn't choose to sign up for community solar"
    join_community_solar = inputs.get("community_solar",NO)

    monthly_elec_bill = inputs.get(MONTHLY_ELEC, getDefault(locality,"elec_typical_monthly_bill",150.))

    fractional_savings = getDefault(locality, "elec_community_solar_average_savings",0.07)       # 7% on utility bill from one company ([3])
    if join_community_solar == YES:
        explanation = "You may not be eligible for community solar, which is available to MA customers of Eversource or National Grid"
        electric_utility = inputs.get("electric_utility","").lower()
        if electric_utility == "eversource" or electric_utility == "ever source" or electric_utility == "nationalgrid" or electric_utility == "national grid":
            explanation = "You may be eligible for community solar, which can save 7-10% on your electric bill" # could be eligible.  May depend the community
            points = 0.
            savings = fractional_savings * 12. * monthly_elec_bill
            cost = 0.    # figure out a typical value
    return points, cost, savings, explanation

RENEWABLE_FRACTION = "renewable_elec_fraction"
def EvalRenewableElectricity(inputs):
    """ 
    Renewable Electricity - residents can choose to purchase renewable power

    GECA adds charge of $0.038/kwh for 100% wind power, on top of the $0.22/kwh 
   
    Refs:
    1. https://www.massenergy.org/greenpowered/howswitchingworks#mix
        #choose_renewable,monthly_elec,electric_utility
    
    """
    points = cost = savings = 0.
    locality = getLocality(inputs)

    explanation = "Didn't choose to sign up for renewable electricity"
    choose_renewable = inputs.get("choose_renewable",NO)
    
    monthly_elec_bill = eval(inputs.get(MONTHLY_ELEC, getDefault(locality,"elec_typical_monthly_bill",150.)))

    kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price
    fixed_charge = getDefault(locality,"elec_monthly_fixed_charge",7.00)    # Eversource current charge
    annual_kwh = 12*(monthly_elec_bill - fixed_charge)/kwh_price

    ghg_intensity_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
    annual_ghg = annual_kwh * ghg_intensity_kwh

    additional_kwh_cost = getDefault(locality,"elec_renewable_additional_kwh_cost",0.038)    # GECA price for the 100% renewable
    if choose_renewable == YES:
        explanation = "You may not be eligible for purchasing renewable electricity, which is available to MA customers of Eversource or National Grid"
        electric_utility = inputs.get("electric_utility","").lower()
        if electric_utility == "eversource" or electric_utility == "ever source" or electric_utility == "nationalgrid" or electric_utility == "national grid":
            explanation = "You are eligible for renewable power, which adds a small charge on your electric bill" # could be eligible.  May depend the community
            # assuming 100% renewable GECA plan
            points = annual_ghg
            savings = -1 * additional_kwh_cost * annual_kwh
            cost = 0.    # figure out a typical value
    return points, cost, savings, explanation

LED_SWAP_FRACTION = "fraction_led_replacement"
NUM_OLD_BULBS = "number_nonefficient_bulbs"
def EvalLEDLighting(inputs):
    explanation = "Didn't choose to replace bulbs with LEDs"
    locality = getLocality(inputs)

    #bulbs_incandescent,bulbs_replace_leds
    num_old_bulbs = inputs.get(NUM_OLD_BULBS, 10)
    num_old_bulbs = int(num_old_bulbs)
    
    
    replace_fraction = inputs.get("numeric_fraction_led_replacement",0.)
    replace_fraction1 = inputs.get(LED_SWAP_FRACTION,FRACTIONS[0])
    # if they can get energy audit it's free
    bulb_price = 0.
    points = cost = savings = 0
    if replace_fraction == 0. and replace_fraction1 != "None":
        if replace_fraction1 == "All":
            replace_fraction = 1.
        elif replace_fraction1 == "Most":
            replace_fraction = 0.75
        elif replace_fraction1 == "Half":
            replace_fraction = 0.5
        elif replace_fraction1 == "Some":
            replace_fraction = 0.25
    average_watts = getDefault(locality,"elec_bulb_average_wattage",60.)
    average_ontime = getDefault(locality,"elec_bulb_average_ontime_hours",3.)
    average_kwh = average_watts * average_ontime * 365 / 1000
    relative_LED_consumption = getDefault(locality,"elec_bulb_relative_LED_consumption", 0.12)  # 12% of an incandescent

    saved_kwh = (1. - relative_LED_consumption) * replace_fraction * num_old_bulbs * average_kwh
    co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
    kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price
    if num_old_bulbs > 0 and replace_fraction>0.:
        explanation = "Replacing %d bulbs with LEDS would save %.0f kwh" % (replace_fraction * num_old_bulbs, saved_kwh)
        points = saved_kwh * co2_per_kwh
        savings = saved_kwh * kwh_price
        cost = bulb_price * replace_fraction * num_old_bulbs
    return points, cost, savings, explanation

APPLIANCE_AGES = {"0-10 years":"age0-10", "10-15 years":"age10-15","15-20 years":"age15-20",">20 years":"age20+"}
def EvalEnergystarRefrigerator(inputs):
    replace_refrig = inputs.get("replace_refrigerator",NO)          # Yes, No
    refrig_age = inputs.get("refrigerator_age", "")                 # >20, 15-20, 10-15, 0-10
    refrig_energystar = inputs.get("refrigerator_energyztar", NO)   # Yes, No, Not Sure

    explanation = "Didn't choose to replace your refrigerator"
    locality = getLocality(inputs)
    points = 0
    cost = 0
    savings = 0
    if replace_refrig == YES and refrig_age!="":
        co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
        kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price

        #estar_kwh =65/kwh_price     # assumes $65 per year electricity use
        estar_kwh = getDefault(locality,"elec_energystar_refrig_kwh_usage", 404) # Frigidaire FFTR1821TB 18cf top freezer

        variable = "elec_refrig_annual_kwh_"+APPLIANCE_AGES.get(refrig_age,"age10-15")
        old_kwh = getDefault(locality,variable,0.,True) # don't update db constants

        elec_savings = old_kwh - estar_kwh

        explanation = "Replacing a typical refrigerator of that age with EnergyStar saves %.0f kwh electricity" % elec_savings

        points = elec_savings * co2_per_kwh
        savings = elec_savings * kwh_price

        cost = getDefault(locality,"elec_energystar_fridge_cost_low",750.)  # Frigidaire FFTR1821TB 18cf top freezer

    return points, cost, savings, explanation

GALS_PER_SCF = 7.48052
def EvalEnergystarWasher(inputs):
    replace_washer = inputs.get("replace_washer",NO)          # Yes, No
    washer_age = inputs.get("washer_age", "")                 # >20, 15-20, 10-15, 0-10
    washer_energystar = inputs.get("washer_energystar", NO)   # Yes, No, Not Sure
    washer_loads = inputs.get("washer_loads", 0.)
    #replace_washer,washer_age,wash_loads
    explanation = "Didn't choose to replace your washer"
    locality = getLocality(inputs)
    points = 0
    cost = 0
    savings = 0
    if replace_washer == YES:
        if washer_age == "0-10 years" and washer_energystar == YES:
            explanation = "You have a pretty new energystar washer already, no point in replacing it."
        else:
            co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
            kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price

            water_price = getDefault(locality,"water_price_per_scf", 0.0564) / GALS_PER_SCF
            # specific heat kj/(L deg C) * gal/L * degC/degF * degreesF
            # assume hot water wash, cold water rince, 50% each
            water_heating_energy = 4.1796 * 3.785 * 5/9 * (120-50) * 0.5
            # assume electric water heater, 1 kwh = 3600 kj
            water_heating_kwh = water_heating_energy / 3600
            water_heating_price = kwh_price * water_heating_kwh
            water_heating_co2 = co2_per_kwh * water_heating_kwh

            if washer_weekly_loads > 0.:
                annual_loads = 52 * washer_weekly_loads
            else:
                annual_loads = getDefaults(locality,"elec_washer_average_annual_loads", 300)

            estar_water_use = getDefaults(locality,"elec_energystar_washer_water_use", 14)
            cost_estar_water = (water_price + water_heating_price) * estar_water_use

            water_embodied_kwh = 1e-6 * getDefaults(locality,"water_kwh_per_MG", 2000)
            water_embodied_co2 = water_embodied_kwh * co2_per_kwh
            co2_estar_water = (water_embodied_co2 + water_heating_co2) * estar_water_use 

            estar_load_kwh = getDefaults(locality,"elec_energystar_elec_per_load", 1.053)
            estar_elec_use = estar_load_kwh

            cost_estar_elec =  estar_elec_use * kwh_price
            co2_estar_elec = estar_elec_use * co2_per_kwh

            cost_energystar = (cost_estar_elec + cost_estar_water) * annual_loads
            co2_energystar = (co2_estar_elec + co2_estar_water) * annual_loads

            # water savings 45%, elec savings 25%
            estar_water_faction_savings = getDefault(locality,"elec_energystar_washer_water_saved_frac")
            estar_elec_faction_savings = getDefault(locality,"elec_energystar_washer_elec_saved_frac")
            old_water_use = estar_water_use / (1. - estar_water_fraction_savings)
            old_elec_use = estar_elec_use / (1. - estar_elec_fraction_savings)

            if washer_age != "0-10 years":      # old washers, double it
                old_water_use = 2. * old_water_use
                old_elec_use = 2. * old_elec_use
                
            cost_old_elec = old_elec_use * kwh_price
            cost_old_water = old_water_use * (water_price + water_heating_price)

            co2_old_elec = old_elec_use * co2_per_kwh
            co2_old_water = old_water_use * (water_embodied_co2 + water_heating_co2)

            cost_old = (cost_old_elec + cost_old_water) * annual_loads
            co2_old = (co2_old_elec + co2_old_water) * annual_loads
            
            water_savings = (old_water_use - estar_water_use) * annual_loads
            elec_savings = (old_elec_use - estar_elec_use) * annual_loads

            explanation = "Replacing your current washer with EnergyStar would save %.0f Gal of water and %.0f kwh" % (water_savings, elec_savings)
            points = (co2_old-co2_energystar)
            savings = (cost_old-cost_energystar)
            cost = getDefault(locality,"elec_energystar_washer_cost_low",700.)

    return points, cost, savings, explanation

def EvalInductionStove(inputs):
    #induction_stove,stove_type
    # efficiency: 90% induction, 65% electric, 45% gas
    # how much gas used in cooking

    explanation = "Didn't choose to switch to an induction stove w convection oven"
    locality = getLocality(inputs)

    if inputs.get("induction_stove",NO) == YES:    
        old_stove = inputs.get("stove_type","")
        if old_stove == "Induction":
            explanation = "You already have an induction stove, so you can't switch to one"
        else:
            co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
            kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price

            kwh_induction = getDefault(locality, "elec_cooking_kwh_induction", 801)
            cost_induction = kwh_induction * kwh_price
            co2_induction = kwh_induction * co2_per_kwh

            if old_stove == "Gas":
                therm_gas = getDefault(locality,"elec_cooking_therm_gas", 110)
                therm_price = getDefault(locality,"natgas_price_per_therm", 1.25)
                co2_per_therm = GasFootprint(locality)
                co2_cooking = therm_gas * co2_per_therm
                cooking_cost = therm_gas * therm_price
                explanation = "Replacing your gas range with induction would save energy and emissions, but probably cost more"
            else:
                cooking_kwh = getDefault(locality, "elec_cooking_kwh_conventional", 1144)
                cooking_cost = cooking_kwh * kwh_price
                co2_cooking = cooking_kwh * co2_per_kwh
                explanation = "Replacing your electric range with induction would save %.0f kwh" % cooking_kwh - kwh_induction
            points = co2_cooking - co2_induction
            savings = cooking_cost - cost_induction

        cost = getDefault(locality,"elec_cost_induction_stove_low", 1550)
    return points, cost, savings, explanation


def EvalHeatPumpDryer(inputs):
    #replace_dryer,dryer_type
    # GreenBuildingAdvisor: save 29c per load compared with electric

    # EPA 133 kWh/year  Heat Pump, saves 60% in energy compared with electric
    # average dryer 3.3 kwh energy per load, gas 0.24 therms/load


    explanation = "Didn't choose to switch to a heat pump dryer"
    locality = getLocality(inputs)

    if inputs.get("replace_dryer",NO) == YES:
        old_dryer = inputs.get("dryer_type","")
        dryer_loads = inputs.get("dryer_loads", 8.)
        if old_dryer == "Heat pump":
            explanation = "You already have a heat pump dryer, so you can't switch to one"
        else:
            co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
            kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price

            kwh_electric_dryer = getDefault(locality,"elec_dryer_load_kwh", 3.3)
            kwh_heatpump = getDefault(locality, "elec_heatpump_dryer_energy_reduction", (1-.6)) * kwh_electric_dryer
            cost_heatpump = kwh_heatpump * kwh_price
            co2_heatpump = kwh_heatpump * co2_per_kwh

            if old_dryer == "Gas":
                therm_gas = getDefault(locality,"elec_dryerload_therm_gas", 0.24) * 52 * dryer_loads
                therm_price = getDefault(locality,"natgas_price_per_therm", 1.25)
                co2_per_therm = GasFootprint(locality)
                co2_drying = therm_gas * co2_per_therm
                drying_cost = therm_gas * therm_price
                explanation = "Replacing your gas dryer with heatpump would save energy and emissions, but probably cost more"
            else:
                drying_cost = kwh_electric_dryer * kwh_price
                co2_drying = kwh_electric_dryer * co2_per_kwh
                explanation = "Replacing your electric dryer with heatpump would save %.0f kwh" % drying_kwh - kwh_heatpump

            points = co2_drying - co2_heatpump
            savings = drying_cost - cost_heatpump

        cost = getDefault(locality,"elec_cost_heatpump_dryer_low", 1250)
    return points, cost, savings, explanation

def EvalColdWaterWash(inputs):
    #cold_water_wash,wash_loads
    explanation = "Didn't choose to ..."
    locality = getLocality(inputs)
    points = 666
    cost = 666.
    savings = 666.
    return points, cost, savings, explanation

def EvalLineDry(inputs):
    #line_or_rack_dry_loads,wash_loads
    explanation = "Didn't choose to ..."
    locality = getLocality(inputs)
    points = 666
    cost = 666.
    savings = 666.
    return points, cost, savings, explanation

def EvalRefrigeratorPickup(inputs):
    #extra_refrigerator,extra_refrigerator_age,extra_refrigerator_pickup,unplug_refrigerator
    explanation = "Didn't choose to have an extra refrigerator pickup"
    locality = getLocality(inputs)

    refrig_pickup = inputs.get("extra_refrigerator_pickup",NO)
    extra_refrig = inputs.get("extra_refrigerator",NO)              # Yes, No
    extra_refrig_age = inputs.get("extra_refrigerator_age", "")                 # >20, 15-20, 10-15, 0-10

    points = 0
    cost = 0
    savings = 0
    if extra_refrig == YES and refrig_pickup == YES:
        co2_per_kwh = getDefault(locality,"elec_lbs_co2_per_kwh",0.75)    # lbs CO2 per kwh
        kwh_price = getDefault(locality,"elec_price_per_kwh",0.2209)            # Eversource current price

        variable = "elec_refrig_annual_kwh_"+APPLIANCE_AGES.get(extra_refrig_age,"age10-15")
        old_kwh = getDefault(locality,variable,0.,True) # don't update db constants
        explanation = "Eliminating a typical refrigerator of that age saves %.0f kwh electricity" % old_kwh

        elec_savings = old_kwh

        points = elec_savings * co2_per_kwh
        savings = elec_savings * kwh_price

        cost = getDefault(locality,"elec_energystar_fridge_cost_low",750.)  # Frigidaire FFTR1821TB 18cf top freezer
    return points, cost, savings, explanation

def EvalSmartPowerStrip(inputs):
    #smart_power_strips
    explanation = "Didn't choose to ..."
    locality = getLocality(inputs)
    points = 666
    cost = 666.
    savings = 666.
    return points, cost, savings, explanation

def EvalElectricityMonitor(inputs):
    #install_electricity_monitor
    explanation = "Didn't choose to ..."
    locality = getLocality(inputs)
    points = 666
    cost = 666.
    savings = 666.
    return points, cost, savings, explanation
