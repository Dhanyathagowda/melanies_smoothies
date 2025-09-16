# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import pandas as pd  # Added pandas for dataframe manipulation
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

# Get fruit list from Snowflake, now including the SEARCH_ON column
# Convert it to a pandas dataframe right away
fruit_options_df = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
    .to_pandas()
)

# 👇 Show the DataFrame so we can confirm SEARCH_ON values are correct
st.dataframe(data=fruit_options_df, use_container_width=True)

# 👇 Stop execution here for debugging (exactly as in your screenshot)
st.stop()

# Multiselect up to 5 fruits
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options_df["FRUIT_NAME"].tolist(),  # Provide the list of fruit names
    max_selections=5  # Limit selections to 5
)

# Display message if more than 5 items are selected
if len(ingredients_list) > 0 and len(ingredients_list) == 5:
    st.info("You can only select up to 5 options.")

# Display selected ingredients string
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    st.write("You selected:", ingredients_string)

# Only proceed with order submission if ingredients are selected
if ingredients_list:
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

    # Reset ingredients_string for API calls
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        search_on = fruit_options_df.loc[
            fruit_options_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        st.write("The search value for", fruit_chosen, "is", search_on)

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )
        st.subheader(fruit_chosen + " Nutrition Information")
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
