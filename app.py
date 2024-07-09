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

startingValue = st.number_input("Starting Value of Portfolio", value=38000, step=1000)
years = st.number_input("Years until death", value=66)
numSimulations = st.number_input("Number of Simulations", value=100)
yearsUntilRetirement = st.number_input("Years until retirement", value=10)
initialCostOfLivingPerMonth = st.number_input("Cost of living (monthly)", value=3000, step=1000)
initialCostOfLivingInRetirementPerMonth = st.number_input("Cost of living in retirement (monthly)", value=600, step=1000)
initialSalary = st.number_input("Salary", value=75000, step=1000)

def monteCarloSimulation(startingValue, years, numSimulations, yearsUntilRetirement, initialCostOfLivingPerMonth, initialCostOfLivingInRetirementPerMonth, initialSalary):
    days = years * 365
    simulations = []
    for _ in range(numSimulations):
        portfolioValuesOverTime = []
        portfolioValue = startingValue
        costOfLivingInRetirementPerMonth = initialCostOfLivingInRetirementPerMonth
        costOfLivingPerMonth = initialCostOfLivingPerMonth
        salary = initialSalary
        for day in range(days):
            portfolioValuesOverTime.append(portfolioValue)
            # Changes portfolio value by choosing a random return value of VFIAX since 2000
            #Vanguard 500 Index Fund Admiral Shares (VFIAX) has a 0.04% expense ratio
            portfolioValue *= (1 + random.choice(VFIAXHistoricalReturnsDaily)) * (1 - 0.0004)

            year = day // 365

            #inflation is assumed to be 3% annually
            if day % 30 == 0:
                costOfLivingPerMonth *= ((1 + 0.03)**(1/12))
                costOfLivingInRetirementPerMonth *= ((1 + 0.03)**(1/12))
            #salary increases by 3% annually
            if day % 365 == 0:
                salary *= 1.03

            if year <= yearsUntilRetirement:
                # monthly
                if day % 30 == 0:
                    portfolioValue -= costOfLivingPerMonth
                # bi-monthly
                if day % 15 == 0:
                    portfolioValue += salary / 24
            elif day % 30 == 0 and year > yearsUntilRetirement:
                portfolioValue -= costOfLivingInRetirementPerMonth

        simulations.append(portfolioValuesOverTime)
    return simulations

def nonMonteCarloSimulation(startingValue, years, yearsUntilRetirement, initialCostOfLivingPerMonth, initialCostOfLivingInRetirementPerMonth, initialSalary):
    days = years * 365
    portfolioValuesOverTime = []
    portfolioValue = startingValue
    costOfLivingInRetirementPerMonth = initialCostOfLivingInRetirementPerMonth
    costOfLivingPerMonth = initialCostOfLivingPerMonth
    salary = initialSalary
    for day in range(days):
        portfolioValuesOverTime.append(portfolioValue)
        # Changes portfolio value by increaseing by the average daily return of VFIAX since 2000
        portfolioValue *= (1 + averageDailyReturn) * (1 - 0.0004)

        year = day // 365

        #inflation is assumed to be 3% annually
        if day % 30 == 0:
            costOfLivingPerMonth *= ((1 + 0.03)**(1/12))
        if day % 365 == 0:
            costOfLivingInRetirementPerMonth *= 1.03
        #salary increases by 3% annually
        if day % 365 == 0:
            salary *= 1.03

        if year <= yearsUntilRetirement:
            # monthly
            if day % 30 == 0:
                portfolioValue -= costOfLivingPerMonth
            # bi-monthly
            if day % 15 == 0:
                portfolioValue += salary / 24
        elif day % 30 == 0 and year > yearsUntilRetirement:
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
    simulations = monteCarloSimulation(startingValue, years, numSimulations, yearsUntilRetirement, initialCostOfLivingPerMonth, initialCostOfLivingInRetirementPerMonth, initialSalary)
    st.write(f"Chance of Success: {calculateChanceOfSuccess(simulations)}%")

    # Change y-axis to display full numbers instead of scientific notation
    formatter = ticker.FuncFormatter(lambda x, p: '$' + format(int(x), ','))
    plt.gca().yaxis.set_major_formatter(formatter)

    # Generate x-axis values for years
    yearsForXAxis = [day/365 for day in range(0, len(simulations[0]))]

    # Plot the portfolio value over time
    for portfolioValuesOverTime in simulations:
        plt.plot(yearsForXAxis, portfolioValuesOverTime)
    plt.plot(yearsForXAxis, nonMonteCarloSimulation(startingValue, years, yearsUntilRetirement, initialCostOfLivingPerMonth, initialCostOfLivingInRetirementPerMonth, initialSalary), color='black')
    plt.xlabel('Years')
    plt.ylabel('Portfolio Value')
    plt.title('Portfolio Value Over Time')
    plt.grid(True)

    # Display the plot on the website
    st.pyplot(plt.gcf())

st.write(f"Average Return for VFIAX: {averageYearlyReturn * 100}%")