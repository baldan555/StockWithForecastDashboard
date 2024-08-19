import streamlit as st


PAGES = {
    "Dashboard": "Dashboard",
    "Forecasting": "Forecasting"
}

st.sidebar.title("Navigasi")
selection = st.sidebar.radio("Pilih Halaman", list(PAGES.keys()))

if selection == "Dashboard":
    from Dashboard import show_dashboard
    show_dashboard()
elif selection == "Forecasting":
    from Forecasting import show_forecasting
    show_forecasting()
