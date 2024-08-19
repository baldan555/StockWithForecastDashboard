import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from PIL import Image
import io
import requests

def show_dashboard():
 
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

    #
    def get_company_logo(ticker):
        return logo_urls.get(ticker, 'https://via.placeholder.com/150')  

    st.markdown("<h1 style='text-align: center;'>Dashboard Harga Saham</h1>", unsafe_allow_html=True)
    st.sidebar.header("Pengaturan")

    tickers_input = st.sidebar.text_area("Masukkan Ticker Saham (pisahkan dengan koma)", value="GOOGL, AAPL, MSFT, NVDA, TSLA, INTC")
    tickers = [ticker.strip().upper() for ticker in tickers_input.split(',') if ticker.strip()]

    if tickers:
        st.write(f"Menampilkan data untuk {', '.join(tickers)}")
        data = get_stock_data(tickers)

        st.subheader("Informasi Saham")

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

                performance_color = 'green' if current_value > previous_value else 'red'
                performance_text = 'Naik' if current_value > previous_value else 'Turun'

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
                    <p>Nilai Terkini: ${current_value:,.2f}</p>
                    <p style="color:{performance_color}; font-weight:bold;">{performance_text}</p>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        for i in range(0, len(tickers), 2):
            cols = st.columns(2) 
            for j in range(2):  
                if i + j < len(tickers):
                    ticker = tickers[i + j]
                    df = data[ticker]
                    cols[j].subheader(f"Grafik Harga Saham {ticker}")

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
                            title=f'Candlestick dan Volume Saham {ticker}',
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

                    cols[j].plotly_chart(fig, use_container_width=True) 
