# Import necessary libraries
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

# Streamlit app title
st.title("Enhanced Stock Dashboard")

# Sidebar inputs
ticker = st.sidebar.text_input('Enter Ticker Symbol (e.g., AAPL)', 'AAPL')
start_date = st.sidebar.date_input('Select Start Date')
end_date = st.sidebar.date_input('Select End Date')

# Fetch historical market data
if ticker and start_date and end_date:
    data = yf.download(ticker, start=start_date, end=end_date)

    # Display line chart for Adjusted Close price
    if not data.empty:
        fig = px.line(data, x=data.index, y="Adj Close", title=f"{ticker} Adjusted Close Price")
        st.plotly_chart(fig)
    else:
        st.error(f"No data found for ticker '{ticker}' between {start_date} and {end_date}")

# Create tabs for different types of data
pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

# Pricing Data Analysis
with pricing_data:
    st.header('Price Movements Analysis')
    if not data.empty:
        # Calculate daily % change
        data['% Change'] = data['Adj Close'].pct_change()
        data.dropna(inplace=True)
        st.write(data)

        # Calculate annual return, standard deviation, and risk-adjusted return
        annual_return = data['% Change'].mean() * 252 * 100  # Assuming 252 trading days
        stdev = np.std(data['% Change']) * np.sqrt(252)
        risk_adjusted_return = annual_return / (stdev * 100)

        st.write(f"Annual Return: {annual_return:.2f}%")
        st.write(f"Standard Deviation (Volatility): {stdev * 100:.2f}%")
        st.write(f"Risk-Adjusted Return (Sharpe Ratio): {risk_adjusted_return:.2f}")
    else:
        st.write("No pricing data available for selected date range.")

# Fundamental Data from Alpha Vantage
with fundamental_data:
    st.header("Fundamental Financial Data")
    if ticker:
        key = 'OW1639L63B5UCYYL'  # Replace with your Alpha Vantage API key
        fd = FundamentalData(key, output_format='pandas')
        
        # Balance Sheet
        try:
            balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
            st.subheader('Balance Sheet')
            st.write(balance_sheet.T[2:])  # Skip metadata rows
        except Exception as e:
            st.write("Error fetching balance sheet data:", e)

        # Income Statement
        try:
            income_statement = fd.get_income_statement_annual(ticker)[0]
            st.subheader('Income Statement')
            st.write(income_statement.T[2:])
        except Exception as e:
            st.write("Error fetching income statement data:", e)

        # Cash Flow Statement
        try:
            cash_flow = fd.get_cash_flow_annual(ticker)[0]
            st.subheader('Cash Flow Statement')
            st.write(cash_flow.T[2:])
        except Exception as e:
            st.write("Error fetching cash flow data:", e)

# Top 10 News with Sentiment Analysis
with news:
    st.header(f"Latest News for {ticker}")
    try:
        sn = StockNews(ticker, save_news=False)
        df_news = sn.read_rss()
        
        for i in range(min(10, len(df_news))):  # Display up to 10 articles
            st.subheader(f"News {i + 1}")
            st.write(df_news['published'][i])
            st.write(df_news['title'][i])
            st.write(df_news['summary'][i])
            st.write(f"Title Sentiment: {df_news['sentiment_title'][i]}")
            st.write(f"News Sentiment: {df_news['sentiment_summary'][i]}")
    except Exception as e:
        st.write("Error fetching news data:", e)
