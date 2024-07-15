import math
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import random

VFIAXHistoricalReturnsDaily = []
with open('VFIAXHistoricalReturnsDaily.txt', 'r') as file:
    for line in file:
        VFIAXHistoricalReturnsDaily.append(float(line.strip()))

averageDailyReturn = sum([float(x) for x in VFIAXHistoricalReturnsDaily]) / len(VFIAXHistoricalReturnsDaily)
averageYearlyReturn = (1 + averageDailyReturn) ** 365 - 1

startingValue = st.number_input("Starting Value of Portfolio", value=40000, step=1000)
years = st.number_input("Years until death", value=66)
numSimulations = st.number_input("Number of Simulations", value=100)
initialCostOfLivingPerMonth = st.number_input("Cost of living (monthly)", value=4000, step=1000)
initialCostOfLivingInRetirementPerMonth = st.number_input("Cost of living in retirement (monthly)", value=2000, step=1000)
initialSalary = st.number_input("Salary", value=75000, step=1000)
pension = st.number_input("Yearly pension", value=0, step=500)
yearsUntilPension = st.number_input("Years until pension kicks in", value=0)
plotAll = st.checkbox("Plot all simulations (uncheck to improve performance)")

def monteCarloSimulation(startingValue, years, numSimulations, initialCostOfLivingPerMonth, initialCostOfLivingInRetirementPerMonth, initialSalary):
    simulations = []
    yearsItTookToRetire = []
    for _ in range(numSimulations):
        portfolioValuesOverTime = []
        portfolioValue = startingValue
        costOfLivingInRetirementPerMonth = initialCostOfLivingInRetirementPerMonth
        costOfLivingPerMonth = initialCostOfLivingPerMonth
        salary = initialSalary
        days = years * 365
        retired = False
        for day in range(days):
            portfolioValuesOverTime.append(portfolioValue)
            # Changes portfolio value by choosing a random return value of VFIAX since 2000
            #Vanguard 500 Index Fund Admiral Shares (VFIAX) has a 0.04% expense ratio
            portfolioValue *= (1 + random.choice(VFIAXHistoricalReturnsDaily))
            portfolioValue -= portfolioValue * 0.000001587

            year = day / 365

            if year >= yearsUntilPension and day % 365 == 0:
                portfolioValue += pension

            #inflation is assumed to be 3% annually
            if day % 30 == 0:
                costOfLivingPerMonth *= ((1 + 0.03)**(1/12))
                costOfLivingInRetirementPerMonth *= ((1 + 0.03)**(1/12))
            #salary increases by 3% annually
            if day % 365 == 0:
                salary *= 1.03

            if not retired:
            #this is a conservative estimate
                if costOfLivingInRetirementPerMonth * 1.03 * 12 / portfolioValue <= 0.03:
                    retired = True
                    yearsItTookToRetire.append(year)
                    

            if not retired:
                # monthly
                if day % 30 == 0:
                    portfolioValue -= costOfLivingPerMonth
                    portfolioValue += salary / 12
            elif day % 30 == 0 and retired:
                portfolioValue -= costOfLivingInRetirementPerMonth

        simulations.append(portfolioValuesOverTime)
    st.write(f"Average years until retirement: {sum(yearsItTookToRetire) / len(yearsItTookToRetire)}")
    st.write(f"Fastest retirement: {min(yearsItTookToRetire)}")
    st.write(f"Slowest retirement: {max(yearsItTookToRetire)}")
    return simulations

def nonMonteCarloSimulation(startingValue, years, initialCostOfLivingPerMonth, initialCostOfLivingInRetirementPerMonth, initialSalary):
    portfolioValuesOverTime = []
    portfolioValue = startingValue
    costOfLivingInRetirementPerMonth = initialCostOfLivingInRetirementPerMonth
    costOfLivingPerMonth = initialCostOfLivingPerMonth
    salary = initialSalary
    retired = False
    days = years * 365
    for day in range(days):
        portfolioValuesOverTime.append(portfolioValue)

        #inflation is assumed to be 3% annually
        #Add a yearly increase option for myself later
        if day % 30 == 0:
            costOfLivingPerMonth *= ((1 + 0.03)**(1/12))
            costOfLivingInRetirementPerMonth *= ((1 + 0.03)**(1/12))
        #salary increases by 3% annually
        if day % 365 == 0:
            salary *= 1.03
        
        #double check vangaurd fees
        portfolioValue *= (1 + averageDailyReturn)
        portfolioValue -= portfolioValue * 0.000001587

        year = day / 365
        
        if year >= yearsUntilPension and day % 365 == 0:
            portfolioValue += pension

        if not retired:
            #this is a conservative estimate
            if costOfLivingInRetirementPerMonth * 1.03 * 12 / portfolioValue <= 0.03:
                retired = True

        if not retired:
            # monthly
            if day % 30 == 0:
                portfolioValue -= costOfLivingPerMonth
                portfolioValue += salary / 12
        elif retired and day % 30 == 0:
            portfolioValue -= costOfLivingInRetirementPerMonth
    return portfolioValuesOverTime

def containsZeroOrLess(portfolioValuesOverTime):
    for value in portfolioValuesOverTime:
        if value <= 0:
            return True
    return False

def calculateChanceOfSuccess(simulations):
    successful = 0
    for portfolioValuesOverTime in simulations:
        if containsZeroOrLess(portfolioValuesOverTime) == False:
            successful += 1
    return successful / len(simulations) * 100

if st.button("Run Simulation"):
    simulations = monteCarloSimulation(startingValue, years, numSimulations, initialCostOfLivingPerMonth, initialCostOfLivingInRetirementPerMonth, initialSalary)
    st.write(f"Chance of Success: {calculateChanceOfSuccess(simulations)}%")

    # Change y-axis to display full numbers instead of scientific notation
    formatter = ticker.FuncFormatter(lambda x, p: '$' + format(int(x), ','))
    plt.gca().yaxis.set_major_formatter(formatter)

    plt.ylim(0, 1500000 * 1.1)  # Add some padding
    plt.xlim(0, years)

    # Generate x-axis values for years
    yearsForXAxis = [day/365 for day in range(0, len(simulations[0]))]

    # Plot the portfolio value over time
    if plotAll:
        for portfolioValuesOverTime in simulations:
            plt.plot(yearsForXAxis, portfolioValuesOverTime)
    plt.plot(yearsForXAxis, nonMonteCarloSimulation(startingValue, years, initialCostOfLivingPerMonth, initialCostOfLivingInRetirementPerMonth, initialSalary), color='black')
    plt.xlabel('Years')
    plt.ylabel('Portfolio Value')
    plt.title('Portfolio Value Over Time')
    plt.grid(True)

    # Display the plot on the website
    st.pyplot(plt.gcf())

st.write(f"Average Return for VFIAX: {averageYearlyReturn * 100}%")