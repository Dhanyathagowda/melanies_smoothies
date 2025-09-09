# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import pandas as pd # Added pandas for dataframe manipulation

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake session
cnx=st.connection("snowflake")
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
if len(ingredients_list) > 0 and len(ingredients_list) == 5: # This condition might need adjustment based on desired exact behavior
    st.info("You can only select up to 5 options.") # Adjusted message

# Display selected ingredients string directly below the multiselect, as in the screenshot
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    st.write("You selected:", ingredients_string) # Added this line for visual confirmation

# Only proceed with order submission if ingredients are selected
if ingredients_list:
    # Build insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Debug first (optional)
    # st.write(my_insert_stmt)
    # st.stop()

    # Button to submit
    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
