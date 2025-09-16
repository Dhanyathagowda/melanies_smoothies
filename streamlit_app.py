# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col,when_matched
import requests

cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(":cup_with_straw: Customize Youe Smoothie! :cup_with_straw: ")
st.write(
  """Choose the fruit you want in your to custom smoothie.
  """
)

# option = st.selectbox('What is your favourite fruit?',
#                      ('Banana','Strawberries','Peaches'))

# st.write('Your Favourite fruit is:', option)

name_on_order = st.text_input ('Name on Smoothie:')
st.write('The name on your Smoothie will be:',name_on_order)


my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))

pd_df = my_dataframe.to_pandas()
# st.dataframe(data=my_dataframe, use_container_width=True)
ingradients_list = st.multiselect('Choose any 5 items',my_dataframe,max_selections=5)

if ingradients_list:
    # st.write(ingradients_list)
    # st.text(ingradients_list)
    ingradients_string = ''

    for fruit_chosen in ingradients_list:
      
      ingradients_string += fruit_chosen + ' '

      search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
      # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

      st.subheader(fruit_chosen + 'Nutrition Information')
      smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+search_on)
      sf_df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)     
      
        
    # st.write(ingradients_string)
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingradients_string + """','"""+name_on_order+ """')"""

    # st.write(my_insert_stmt)  

    time_to_insert = st.button('Submit Order')

    if time_to_insert :
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
    

    # st.write(my_insert_stmt)

    # if ingradients_string:
    #     session.sql(my_insert_stmt).collect()
    #     st.success('Your Smoothie is ordered!', icon="✅")






    
