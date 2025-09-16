# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import pandas as pd   # ✅ added pandas
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Pull fruit options from Snowflake (FRUIT_NAME + SEARCH_ON)
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert Snowflake DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Multiselect up to 5 fruits
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        # ✅ Get the SEARCH_ON value for the chosen fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Show sentence: "The search value for Apples is Apple ."
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        # Show Nutrition Info
        st.subheader(fruit_chosen + " Nutrition Information")

        # Call SmoothieFroot API with SEARCH_ON value
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        # Display nutrition data in a dataframe
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
