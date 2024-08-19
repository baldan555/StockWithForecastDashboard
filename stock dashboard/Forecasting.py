import streamlit as st
import yfinance as yf
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import plotly.graph_objects as go

def show_forecasting():
    st.set_page_config(
        page_title="Forecasting Harga Saham",
        layout="wide"
    )

    st.title("Halaman Forecasting Harga Saham")

    ticker = st.text_input("Masukkan Ticker Saham untuk Forecasting", value="GOOGL").upper()

    if ticker:
  
        stock = yf.Ticker(ticker)
        df = stock.history(period="2y") 
        df['Return'] = df['Close'].pct_change()
        df['Lag_1'] = df['Close'].shift(1)
        df.dropna(inplace=True)

        X = df[['Lag_1']]
        y = df['Close']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)


        model = RandomForestRegressor(n_estimators=100, max_depth=None, min_samples_split=2)
        model.fit(X_train, y_train)

        forecast = model.predict(X_test)
        forecast_df = pd.DataFrame({'Date': X_test.index, 'Actual': y_test, 'Forecast': forecast})
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Actual'], mode='lines', name='Actual'))
        fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Forecast'], mode='lines', name='Forecast'))

        fig.update_layout(
            title=f'Forecasting Harga Saham {ticker}',
            xaxis_title='Tanggal',
            yaxis_title='Harga'
        )

        st.plotly_chart(fig, use_container_width=True)
