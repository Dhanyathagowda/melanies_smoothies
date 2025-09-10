# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import pandas as pd # Added pandas for dataframe manipulation
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

# Get fruit list from Snowflake
# Renamed from my_dataframe to fruit_options_df for clarity
fruit_options_df = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
    .to_pandas()
)

# Multiselect up to 5 fruits
# Changed to use the DataFrame directly for display in multiselect, similar to the screenshot
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options_df["FRUIT_NAME"].tolist(), # Provide the list of fruit names
    max_selections=5 # Limit selections to 5
)

# Display message if more than 5 items are selected (even though max_selections prevents it,
# the screenshot shows a message about limits, implying this check)
if len(ingredients_list) > 0 and len(ingredients_list) == 5:
    st.info("You can only select up to 5 options.")

# Display selected ingredients string directly below the multiselect, as in the screenshot
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    st.write("You selected:", ingredients_string)

# Only proceed with order submission if ingredients are selected
if ingredients_list:
    # Build insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    
    # Button to submit
    time_to_insert = st.button("Submit Order")
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

    # This section makes an API call for each selected ingredient
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
