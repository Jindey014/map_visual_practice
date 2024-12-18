import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')

st.title("Population Dashboard")


# TO get unique year from the dataframe and put them in a list instead of an array like python typically does . Also reverse the ordering of these year list

year_list = list(df_reshaped.year.unique())[::-1] 
state_list =["All"] +list(df_reshaped.states.unique())

with st.sidebar:
    selected_year = st.selectbox('Select a year',year_list,index=0)
    df_selected_year = df_reshaped[df_reshaped["year"] == selected_year]

    selected_state = st.selectbox('Select State', state_list, index=0)
    with st.expander('Add Record'):
        st.header('Insert Record Here')
        detail_form= st.form("Detail Form")
        
        
        
        
selected_color_theme = 'YlGnBu'


# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    if selected_state != 'All':
        input_df = input_df[input_df['states']==selected_state]
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
    choropleth.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

choropleth = make_choropleth(df_selected_year, 'states_code', 'population', selected_color_theme)
st.plotly_chart(choropleth, use_container_width=True)
