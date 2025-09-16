# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(f" :cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom smoothie!
  """)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smooothie will be:", name_on_order)

# Connect to Snowflake
cnx=st.connection("snowflake")
session=cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

# Convert the Snowpark DataFrame to a Pandas DataFrame for easier use
pd_df=my_dataframe.to_pandas()

# Get the list of fruit names for the multiselect widget
fruit_names = pd_df['FRUIT_NAME'].tolist()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,  # CORRECTED: Pass the list of fruit names
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    found_fruits_count = 0  # Initialize a counter for found fruits
    total_fruits_selected = len(ingredients_list)

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        
        # Check if the API call was successful (status code 200)
        if smoothiefroot_response.status_code == 200:
            found_fruits_count += 1
            # Display the nutrition data
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.write(f"Nutrition information for {fruit_chosen} not found.")

    # Logic to determine if the order should be marked as filled
    order_is_filled = False
    if total_fruits_selected > 0:
        if found_fruits_count / total_fruits_selected > 0.75:
            order_is_filled = True

    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        # Use f-string for a cleaner and safer insert statement
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order, order_filled)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}', {order_is_filled})
        """
        
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
