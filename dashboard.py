import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime

st.title("Stock Dashboard")

# Sidebar inputs for ticker and dates
ticker = st.sidebar.text_input('Ticker', value='AAPL')  # Default ticker to avoid empty value issues
start_date = st.sidebar.date_input('Start Date', datetime(2020, 1, 1))
end_date = st.sidebar.date_input('End Date', datetime.now())

# Validate date input to prevent issues
if start_date >= end_date:
    st.error("End date must be after the start date.")
else:
    # Fetch stock data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Check if the data is available
    if data.empty:
        st.warning(f"No data found for ticker '{ticker}' within the specified date range.")
    else:
        # Plot adjusted close price
        fig = px.line(data, x=data.index, y="Adj Close", title=f"{ticker} Adjusted Close Price Over Time")
        st.plotly_chart(fig)

        # Tabs for different views
        pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

        # Pricing Data tab
        with pricing_data:
            st.header('Price Movements')
            data['% Change'] = data['Adj Close'].pct_change()
            data.dropna(inplace=True)  # Drop NaN values for the first row where pct_change is NaN
            st.write(data)

            # Calculate annual return and risk metrics
            annual_return = data['% Change'].mean() * 252 * 100
            stdev = np.std(data['% Change']) * np.sqrt(252) * 100
            risk_adjusted_return = annual_return / stdev

            # Display calculated metrics
            st.write('Annual Return: {:.2f}%'.format(annual_return))
            st.write('Standard Deviation: {:.2f}%'.format(stdev))
            st.write('Risk Adjusted Return: {:.2f}'.format(risk_adjusted_return))

        # Fundamental Data tab
        with fundamental_data:
            try:
                from alpha_vantage.fundamentaldata import FundamentalData
                key = 'YOUR_ALPHA_VANTAGE_KEY'
                fd = FundamentalData(key, output_format='pandas')

                st.subheader('Balance Sheet')
                balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
                bs = balance_sheet.T[2:]
                bs.columns = list(balance_sheet.T.iloc[0])
                st.write(bs)

                st.subheader('Income Statement')
                income_statement = fd.get_income_statement_annual(ticker)[0]
                is1 = income_statement.T[2:]
                is1.columns = list(income_statement.T.iloc[0])
                st.write(is1)

                st.subheader('Cash Flow Statement')
                cash_flow = fd.get_cash_flow_annual(ticker)[0]
                cf = cash_flow.T[2:]
                cf.columns = list(cash_flow.T.iloc[0])
                st.write(cf)
            except Exception as e:
                st.error("Failed to fetch fundamental data. Please check API key or try again later.")

        # News tab
        with news:
            try:
                from stocknews import StockNews
                st.header(f'News of {ticker}')
                sn = StockNews(ticker, save_news=False)
                df_news = sn.read_rss()
                for i in range(min(10, len(df_news))):
                    st.subheader(f'News {i+1}')
                    st.write(df_news['published'][i])
                    st.write(df_news['title'][i])
                    st.write(df_news['summary'][i])
                    st.write(f'Title Sentiment: {df_news["sentiment_title"][i]}')
                    st.write(f'News Sentiment: {df_news["sentiment_summary"][i]}')
            except Exception as e:
                st.error("Failed to fetch news data. Please check the API connection or try again later.")

