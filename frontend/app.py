API_URL = "https://medicine-alternative-finder.onrender.com"

import requests
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Medicine Alternative Finder",
    page_icon="💊",
    layout="wide"
)

st.title("Medicine Alternative Finder")

st.write(
    "Search a medicine and discover cheaper alternatives."
)

query = st.text_input(
    "Search Medicine"
)

suggestions = []

if query:

    response = requests.get(
        f"{API_URL}/search",
        params={"query": query}
    )

    if response.status_code == 200:
        suggestions = response.json()

selected = None

if suggestions:

    selected = st.selectbox(

        "Select Medicine",

        suggestions

    )

if st.button("Find Alternatives"):

    if selected is None:

        st.warning("Please select a medicine.")

    else:

        with st.spinner("Finding alternatives..."):

            response = requests.post(

                f"{API_URL}/predict",

                json={
                    "medicine_name": selected
                }

            )

        if response.status_code == 200:

            result = response.json()
            searched = result["searched_medicine"]

            st.subheader("Selected Medicine")

            col1, col2 = st.columns(2)

            col1.metric(
                "Actual Price",
                f"₹{searched['actual_price']:.2f}"
            )

            col2.metric(
                "Predicted Price",
                f"₹{searched['predicted_price']:.2f}"
            )

        else:

            st.error("Medicine not found.")

        st.subheader("Alternatives:")

        alternatives = result["alternatives"]            

        if len(alternatives) == 0:

            st.info("No alternatives found.")

        else:

            table = []

            for medicine in alternatives:

                table.append({

                    "Medicine": medicine["medicine"],

                    "Manufacturer": medicine["manufacturer"],

                    "Actual Price (₹)": medicine["actual_price"],

                    "Predicted Price (₹)": medicine["predicted_price"]

                })

            st.dataframe(
                table,
                use_container_width=True
            )

            chart_data = []

            # Add the searched medicine
            chart_data.append({
                "Medicine": searched["name"],
                "Manufacturer": searched["manufacturer"],
                "Price": searched["actual_price"]
            })

            # Add the alternatives
            for medicine in alternatives:
                chart_data.append({
                    "Medicine": medicine["medicine"],
                    "Manufacturer": searched["manufacturer"],
                    "Price": medicine["actual_price"]
                })

            chart_df = pd.DataFrame(chart_data)

            st.subheader("📊 Price Comparison")

            fig = px.bar(
                chart_df,
                x="Medicine",
                y="Price",
                text="Price",
                hover_name="Medicine",
                hover_data={
                    "Manufacturer": True,
                    "Price": ":.2f"
                },
                title="Price Comparison"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )