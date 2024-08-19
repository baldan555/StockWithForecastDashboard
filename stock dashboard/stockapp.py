import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from PIL import Image
import io
import requests
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from streamlit_option_menu import option_menu


st.set_page_config(
    page_title="Stock Price Dash",
    
    layout="wide"  
)

logo_urls = {
    'GOOGL': 'https://logo.clearbit.com/google.com',
    'AAPL': 'https://logo.clearbit.com/apple.com',
    'MSFT': 'https://logo.clearbit.com/microsoft.com',
    'NVDA': 'https://logo.clearbit.com/nvidia.com',
    'TSLA': 'https://logo.clearbit.com/tesla.com',
    'INTC': 'https://logo.clearbit.com/intel.com'
}

def get_stock_data(tickers):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")  
        data[ticker] = hist
    return data

def get_company_logo(ticker):
    return logo_urls.get(ticker, 'https://via.placeholder.com/150')  

def forecast_stock_data(df):
    model = ExponentialSmoothing(df['Close'], trend='add', seasonal='add', seasonal_periods=252)
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=30)  
    return forecast

with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Forecasting"],
        icons=["bar-chart", "calendar"],
        menu_icon="cast",
        default_index=0
    )

if selected == "Dashboard":
   
    st.markdown("<h1 style='text-align: center;'>Stock Price Dash</h1>", unsafe_allow_html=True)


    tickers_input = st.sidebar.text_area("Masukkan Ticker Saham (pisahkan dengan koma)", value="GOOGL, AAPL, MSFT, NVDA, TSLA, INTC")
    tickers = [ticker.strip().upper() for ticker in tickers_input.split(',') if ticker.strip()]

    if tickers:
     
        data = get_stock_data(tickers)
        num_columns = len(tickers)
        cols = st.columns(num_columns)

        chart_types = {}
        for ticker in tickers:
            chart_types[ticker] = st.sidebar.selectbox(
                f"Pilih jenis grafik untuk {ticker}",
                ('Candlestick dengan Volume', 'Line Plot'),
                index=0  
            )

        for idx, ticker in enumerate(tickers):
            with cols[idx]:
                logo_url = get_company_logo(ticker)
                response = requests.get(logo_url)
                logo = Image.open(io.BytesIO(response.content))

                df = data[ticker]
                current_value = df['Close'].iloc[-1]
                previous_value = df['Close'].iloc[-2]
                last_date = df.index[-1].strftime('%Y-%m-%d')

                performance_color = 'green' if current_value > previous_value else 'red'
                performance_text = 'Up' if current_value > previous_value else 'Down'

                st.markdown(f"""
                <div style="
                    border: 2px solid #ccc;
                    border-radius: 8px;
                    padding: 10px;
                    text-align: center;
                    box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
                    margin: 10px;
                ">
                    <h3>{ticker}</h3>
                    <img src="{logo_url}" width="100" style="border-radius: 8px;" />
                    <p>Current Price: ${current_value:,.2f}</p>
                    <p style="color:{performance_color}; font-weight:bold;">{performance_text}</p>
                </div>
                """, unsafe_allow_html=True)

            st.divider()

     
            open_price = df['Open'][0]
            close_price = df['Close'][0]
            percentage_change = ((close_price - open_price) / open_price) * 100
            if percentage_change >= 0:
                change_color = "#4CAF50"  
                change_text = f"+{percentage_change:.2f}%"
            else:
                change_color = "#F44336"  
                change_text = f"{percentage_change:.2f}%"
            col1, col2 = st.columns([3, 1])

            with col1:
                with st.container():
                    st.subheader(f"{ticker} Stock")

                    fig = go.Figure()

                    if chart_types[ticker] == 'Candlestick dengan Volume':
                      
                        fig.add_trace(go.Candlestick(
                            x=df.index,
                            open=df['Open'],
                            high=df['High'],
                            low=df['Low'],
                            close=df['Close'],
                            name='Candlestick'
                        ))

                        fig.add_trace(go.Bar(
                            x=df.index,
                            y=df['Volume'],
                            name='Volume',
                            yaxis='y2',
                            marker=dict(color='rgba(0, 100, 250, 0.5)')
                        ))

                        fig.update_layout(
                            xaxis_title='Tanggal',
                            yaxis_title='Harga',
                            yaxis2=dict(
                                title='Volume',
                                overlaying='y',
                                side='right'
                            ),
                            xaxis_rangeslider_visible=False
                        )
                    else:
                       
                        fig.add_trace(go.Scatter(
                            x=df.index,
                            y=df['Open'],
                            mode='lines',
                            name='Harga Pembuka',
                            line=dict(color='royalblue')
                        ))

                        fig.add_trace(go.Scatter(
                            x=df.index,
                            y=df['Close'],
                            mode='lines',
                            name='Harga Penutup',
                            line=dict(color='firebrick')
                        ))

                        fig.update_layout(
                            title=f'Line Plot Harga Saham {ticker}',
                            xaxis_title='Tanggal',
                            yaxis_title='Harga',
                        )

                    with st.container():
                        st.markdown("""
                            <style>
                            .plot-container {
                                border: 2px solid #ffffff;
                                border-radius: 12px;
                                padding: 20px;
                                box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
                                background-color: #ffffff;
                                margin-top: 20px;
                            }
                         
                            """, unsafe_allow_html=True)
                        
                        st.plotly_chart(fig, use_container_width=True)

            with col2:
                
                 st.markdown(f"""
                    <div style="
                        border: 2px solid #ffffff;
                        border-radius: 12px;
                        background-color: #ffffff;
                        padding: 20px;
                        text-align: center;
                        box-shadow: 0px 8px 16px rgba(0,0,0,0.2);
                        margin-top: 63px;  /* Menurunkan posisi card dengan margin atas yang lebih besar */
                        font-family: Arial, sans-serif;
                    ">
                        <h2 style="color: #4CAF50;">📈 Market Summary</h2>
                        <p style="font-size: 1.2em; color: #333333;">Date: <strong>{last_date}</strong></p>
                        <div style="
                            background-color: {change_color};
                            color: #ffffff;
                            border-radius: 10px;
                            padding: 15px;
                            box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
                            border: 1px solid #d3d3d3;
                            margin-bottom: 20px;
                        ">
                            <p style="font-size: 1.2em; margin: 0;"><strong>Change:</strong> {change_text}</p>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: center;">
                            <div style="
                                background-color: #f0f8ff;
                                border-radius: 10px;
                                padding: 15px;
                                box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
                                border: 1px solid #d3d3d3;
                            ">
                                <p style="font-size: 1.1em; color: #ff9800;"><strong>Open:</strong> ${df['Open'][0]:,.2f}</p>
                                <p style="font-size: 1.1em; color: #ff5722;"><strong>Close:</strong> ${df['Close'][0]:,.2f}</p>
                            </div>
                            <div style="
                                background-color: #f0f8ff;
                                border-radius: 10px;
                                padding: 15px;
                                box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
                                border: 1px solid #d3d3d3;
                            ">
                                <p style="font-size: 1.1em; color: #2196F3;"><strong>High:</strong> ${df['High'][0]:,.2f}</p>
                                <p style="font-size: 1.1em; color: #009688;"><strong>Low:</strong> ${df['Low'][0]:,.2f}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

elif selected == "Forecasting":
   
    def get_stock_data(tickers):
        data = {}
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")  
            hist = hist[['Open', 'High', 'Low', 'Close']]
            data[ticker] = hist
        return data

    def forecast_exponential_smoothing(series, steps=40):
        model = ExponentialSmoothing(series, trend='add', seasonal='add', seasonal_periods=20)
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=steps)
        conf_int = 0.02 * forecast  
        return forecast, conf_int

  
    def plot_data_and_forecast(df, feature, forecast, conf_int, forecast_steps):
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=df.index, y=df[feature], mode='lines', name='Historical Data', line=dict(color='royalblue')))

        last_date = df.index[-1]
        forecast_index = pd.date_range(start=last_date, periods=forecast_steps + 1, freq='B')[1:]
        
        lower_bound = forecast - conf_int
        upper_bound = forecast + conf_int

        fig.add_trace(go.Scatter(
            x=forecast_index.tolist() + forecast_index.tolist()[::-1],
            y=lower_bound.tolist() + upper_bound.tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0, 100, 250, 0.2)', 
            line=dict(color='rgba(255, 255, 255, 0)'), 
            name='Forecast Interval'
        ))

        fig.add_trace(go.Scatter(
            x=forecast_index,
            y=forecast,
            mode='lines',
            name='Forecast',
            line=dict(color='red')
        ))

        fig.update_layout(
            xaxis_title='Date',
            yaxis_title=feature,
            legend_title='Legend',
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(240,240,240,0.8)'
        )
        return fig


    def forecast_page():
        st.markdown("""
            <style>
            .title {
                text-align: center;
                font-size: 2em;
                color: #333;
                margin-bottom: 20px;
            }
            .card {
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                background-color: #ffffff;
                padding: 20px;
                box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
                margin-top: 20px;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="title">Stock Price Forecasting</div>', unsafe_allow_html=True)

        st.sidebar.header("Pengaturan")
        tickers = st.sidebar.text_input("Masukkan Ticker Saham (pisahkan dengan koma)", "GOOGL").split(',')
        tickers = [ticker.strip() for ticker in tickers]
        
        if tickers:
            data = get_stock_data(tickers)

            ticker = tickers[0]
            df = data[ticker]
            forecast_steps = 40  
            features = ['Open', 'High', 'Low', 'Close']

            for feature in features:
                series = df[feature].dropna()
                if len(series) > 10: 
                    forecast, conf_int = forecast_exponential_smoothing(series, steps=forecast_steps)
                    fig = plot_data_and_forecast(df, feature, forecast, conf_int, forecast_steps)
                    st.write(f"<div class='card'><strong>{feature} Price - Forecast of {ticker} Stock</strong></div>", unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write(f"<div class='card'><strong>{feature}:</strong> Not enough data to forecast.</div>", unsafe_allow_html=True)

    forecast_page()