import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

VFIAXHistoricalReturnsDaily = []
with open('VFIAXHistoricalReturnsDaily.txt', 'r') as file:
    for line in file:
        VFIAXHistoricalReturnsDaily.append(line.strip())

averageDailyReturn = sum([float(x) for x in VFIAXHistoricalReturnsDaily]) / len(VFIAXHistoricalReturnsDaily)
averageYearlyReturn = (1 + averageDailyReturn) ** 365 - 1

st.title("Monte Carlo Simulation")

st.write("Dont use this yet, still in development")
st.write(f"Average Return for VFIAX: {averageYearlyReturn}")

startingValue = st.number_input("Starting Value", value=35000)
years = st.number_input("Years", value=66)
numSimulations = 1

days = years * 365

def monteCarloSimulation(startingValue, years, numSimulations):
    portfolioValuesOverTime = []
    simulations = []
    for i in range(numSimulations):
        portfolioValue = startingValue
        portfolioValuesOverTime.append(portfolioValue)
        for j in range(years * 365):
            portfolioValue *= (1 + averageDailyReturn)
            portfolioValuesOverTime.append(portfolioValue)
        simulations.append(portfolioValuesOverTime)
    return simulations

if st.button("Run Simulation"):
    results = monteCarloSimulation(startingValue, years, numSimulations)

    # Plot
    fig, ax = plt.subplots()
    for sim in results:
        ax.plot(range(days + 1), sim)
    ax.set_xlabel("Years")
    ax.set_ylabel("Portfolio Value")

    # Format x-axis to display years
    ax.get_xaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x / 365), ',')))

    # Add $ before the numbers on the y-axis
    ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: '${:,.0f}'.format(int(x), ',')))
    
    st.pyplot(fig)