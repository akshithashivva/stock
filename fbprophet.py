import streamlit as st
from datetime import date
import numpy as np
import pandas as pd
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
from sklearn.metrics import mean_absolute_error, mean_squared_error

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.title('Stock Forecast App')

# Input for ticker symbol and prediction years
ticker_symbol = st.text_input('Enter ticker symbol (e.g., AAPL, MSFT)', 'AAPL')
n_years = st.slider('Years of prediction:', 1, 4)
period = n_years * 365

# Function to load data
@st.cache_data
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data

# Load data
data_load_state = st.text('Loading data...')
try:
    data = load_data(ticker_symbol)
    data_load_state.text('Loading data... done!')
except Exception as e:
    st.error(f"Error loading data: {e}")

# Show raw data
st.subheader('Raw data')
st.write(data.tail())

# Plot raw data
def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
    fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_raw_data()

# Prepare data for Prophet model
try:
    # Ensure 'Close' column is numeric and drop NaN rows
    data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
    data.dropna(subset=['Close'], inplace=True)

    df_train = data[['Date', 'Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

    # Initialize and fit the Prophet model
    m = Prophet()
    m.fit(df_train)
    
    # Make future predictions
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)
    
    # Show and plot forecast
    st.subheader('Forecast data')
    st.write(forecast.tail())
    
    st.write(f'Forecast plot for {n_years} years')
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1)
    
    st.write("Forecast components")
    fig2 = m.plot_components(forecast)
    st.write(fig2)
    
    # Evaluation metrics
    actual_values = data['Close'].values[-len(forecast['yhat'].values):]
    predicted_values = forecast['yhat'].values[-len(actual_values):]
    
    mae = mean_absolute_error(actual_values, predicted_values)
    mse = mean_squared_error(actual_values, predicted_values)
    rmse = np.sqrt(mse)
    
    st.write("Evaluation metrics")
    st.write(f"Mean Absolute Error (MAE): {mae}")
    st.write(f"Mean Squared Error (MSE): {mse}")
    st.write(f"Root Mean Squared Error (RMSE): {rmse}")
    
except Exception as e:
    st.error(f"Error during forecasting: {e}")
