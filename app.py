import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
from datetime import datetime

# Function to get the session state
def get_session_state():
    if 'tickers' not in st.session_state:
        st.session_state.tickers = ['INFY', 'SBIN']

# Setting up the UI elements
st.title('Yahoo Finance Dashboard')
get_session_state()

ticker = st.sidebar.text_input('Enter a Stock')
if ticker:
    st.session_state.tickers.append(ticker.upper())#storing in session state

start_date = st.sidebar.date_input('Start Date', value=datetime(2024, 3, 5))
end_date = st.sidebar.date_input('End Date')
refresh_interval = st.sidebar.number_input('Enter Refresh Rate(seconds)', value=2)
stock_to_remove = st.sidebar.text_input("Enter a stock to remove")

# Remove stock from the list
if stock_to_remove in st.session_state.tickers:
    st.session_state.tickers.remove(stock_to_remove)
placeholder = st.empty()  

while True:
    with placeholder.container():
        for ticker_symbol in st.session_state.tickers:
            url = f'https://www.google.com/finance/quote/{ticker_symbol}:NSE'#url for getting live prices
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                price_elem = soup.find(class_='YMlKec fxKbKc')  # div class for price
                if price_elem is not None:
                    price = float(price_elem.text.strip()[1:].replace(',', ''))#removing uneccesary symbols from the string after scrapping it 
                    st.header(f"Price of {ticker_symbol}: {price}")

                    # Displaying pricing data
                    with st.expander("Pricing Data"):
                        ticker_ns = ticker_symbol + '.NS'
                        data = yf.download(ticker_ns, start=start_date, end=end_date)
                        st.line_chart(data=data)

                    # Displaying Standard Deviation and Risk Adjusted Return
                    with st.expander("Standard Deviation and Risk Adjusted"):
                        data['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
                        annual_return = data['% Change'].mean() * 252 * 100
                        st.write('Annual return is ', annual_return, '%')
                        stdev = np.std(data['% Change']) * np.sqrt(252)
                        st.write('Standard Deviation is ', stdev * 100, '%')
                        st.write('Risk Adj. Return is ', annual_return / (stdev * 100))

                else:
                    st.error(f"Invalid input or unable to retrieve the price for {ticker_symbol}")#error for wrong input
            except ConnectionError:
                st.error("The connection got lost. Please try again.")#error for connection loss

        # Refreshing after each ticker symbol
        time.sleep(refresh_interval)
        st.write("due Alpha Vantage request limit of 25 per day it could not be implemented with the refresh rates")