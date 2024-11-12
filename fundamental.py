import streamlit as st
import yfinance as yf
import pandas as pd
from sklearn.linear_model import LinearRegression

# Function to retrieve quarterly high and low prices and classify reports
def get_quarterly_report(ticker):
    stock = yf.Ticker(ticker)

    # Get historical data for the last 5 years (changed '4y' to '5y')
    hist = stock.history(period="5y")

    # Resample to quarterly intervals and calculate high and low prices (changed 'Q' to 'QE')
    quarterly_data = hist.resample('QE').agg({'High': 'max', 'Low': 'min'})

    # Use linear regression to predict future prices for the next quarter
    X = pd.DataFrame({'Quarter': range(len(quarterly_data))}).values.reshape(-1, 1)
    y_high = quarterly_data['High'].values
    y_low = quarterly_data['Low'].values

    model_high = LinearRegression().fit(X, y_high)
    model_low = LinearRegression().fit(X, y_low)

    future_quarter = len(quarterly_data)
    next_quarter = future_quarter + 1

    future_price_high = model_high.predict([[next_quarter]])[0]
    future_price_low = model_low.predict([[next_quarter]])[0]

    # Classify the next quarter's report based on the predicted future prices
    decision = 'Hold'
    if (future_price_high >= 1.05 * quarterly_data['High'].iloc[-1]) and (future_price_low >= 1.05 * quarterly_data['Low'].iloc[-1]):
        decision = 'Buy'
    elif (future_price_high <= 0.95 * quarterly_data['High'].iloc[-1]) and (future_price_low <= 0.95 * quarterly_data['Low'].iloc[-1]):
        decision = 'Sell'

    return quarterly_data, future_price_high, future_price_low, decision

# Streamlit app
st.title('Stock Price Prediction for Next Quarter')
ticker = st.text_input('Enter Ticker Symbol (e.g., AAPL for Apple Inc.)')

if st.button('Predict'):
    if not ticker:
        st.error('Please enter a valid ticker symbol.')
    else:
        try:
            quarterly_report, future_price_high, future_price_low, decision = get_quarterly_report(ticker.upper())
            st.header('Quarterly High and Low Prices:')
            st.write(quarterly_report)
            st.header('Predicted Prices for Next Quarter:')
            st.write(f'Predicted High: {future_price_high:.2f}')
            st.write(f'Predicted Low: {future_price_low:.2f}')
            st.success(f'Final Decision for Next Quarter: {decision}')
        except Exception as e:
            st.error(f'An error occurred: {e}')
