# Import necessary libraries
import streamlit as st
import yfinance as yf
import pandas as pd

# Streamlit app title
st.title("Simple Stock Data App")

# Input for stock ticker symbol
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT)", "AAPL")

# Button to retrieve data
if st.button("Get Stock Data"):
    # Fetch historical market data from Yahoo Finance
    stock_data = yf.download(ticker, period="1y")  # Fetches data for the last year

    # Check if data is returned
    if not stock_data.empty:
        st.write(f"Displaying Adjusted Close Price for {ticker.upper()}")
        st.line_chart(stock_data["Adj Close"])
    else:
        st.error(f"No data found for ticker '{ticker}'")

