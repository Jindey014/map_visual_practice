import streamlit as st
import pandas as pd
import plotly.express as px

# Load data from CSV into session state
if 'df_reshaped' not in st.session_state:
    st.session_state.df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')

df_reshaped = st.session_state.df_reshaped
# Drop unwanted unnamed columns if they appear
df_reshaped = df_reshaped.loc[:, ~df_reshaped.columns.str.contains('^Unnamed')]

st.title("Population Dashboard")

# Get unique years and states
year_list = sorted(df_reshaped['year'].dropna().unique().tolist(), reverse=True)  # Remove NaN and sort
state_list = ["All"] + sorted(df_reshaped['states'].dropna().unique().tolist())   # Remove NaN and sort

# Sidebar selectors
with st.sidebar:
    selected_year = st.selectbox('Select a year', year_list, index=0)
    df_selected_year = df_reshaped[df_reshaped["year"] == selected_year]

    selected_state = st.selectbox('Select State', state_list, index=0)

# Choropleth map
selected_color_theme = 'YlGnBu'

def make_choropleth(input_df, input_id, input_column, input_color_theme):
    if selected_state != 'All':
        input_df = input_df[input_df['states'] == selected_state]
    choropleth = px.choropleth(
        input_df,
        locations=input_id,
        color=input_column,
        locationmode="USA-states",
        color_continuous_scale=input_color_theme,
        range_color=(0, max(df_selected_year.population)),
        scope="usa",
        labels={'population': 'Population'}
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

# Add Record Form
with st.expander('Add Record'):
    st.header('Insert Record Here')
    detail_form = st.form(key="add_record_form")  # Added unique key
    state_name = detail_form.text_input("State Name")
    state_code = detail_form.text_input("State Code")
    year = detail_form.selectbox("Installation Year", year_list)
    population = detail_form.number_input("Population", min_value=0)
    add_record = detail_form.form_submit_button(label="Add new record")

    # Add record logic
    if add_record:
        if state_name:
            # Generate a new ID
            if 'id' in df_reshaped.columns:
                new_id = df_reshaped['id'].max() + 1
            else:
                new_id = 1

            # Create a new record
            new_record = pd.DataFrame.from_records([{
                'states': state_name,
                'states_code': state_code,
                'id': new_id,
                'year': year,
                'population': population
            }])

            # Update session state DataFrame
            st.session_state.df_reshaped = pd.concat([df_reshaped, new_record], ignore_index=True)

            # Debug: Show updated DataFrame
            st.write("Updated DataFrame:", st.session_state.df_reshaped.tail())

            # Save to CSV
            try:
                st.session_state.df_reshaped.to_csv('data/us-population-2010-2019-reshaped.csv', index=False)
                st.success(f"Record for {state_name} added successfully!")

                # Reload the page immediately
                st.rerun()  

            except Exception as e:
                st.error(f"Error saving file: {e}")
        else:
            st.error('State Name is required')


# Update Record Form
with st.expander('Update Record'):
    st.header('Update Existing Record')
    update_form = st.form("Update Form")
    
    # Select existing record for updating
    selected_record = None
    if selected_state != "All" and selected_year:
        selected_record = df_reshaped[
            (df_reshaped['states'] == selected_state) & 
            (df_reshaped['year'] == selected_year)
        ]

    if selected_record is not None and len(selected_record) > 0:
        # Populate the form fields
        state_name = selected_record.iloc[0]['states']
        state_code = selected_record.iloc[0]['states_code']
        population = int(selected_record.iloc[0]['population']) if selected_record.iloc[0]['population'] is not None else 0
        
        # Display the fields in the form
        state_name = update_form.text_input("State Name", value=state_name, disabled=True) 
        state_code = update_form.text_input("State Code", value=state_code, disabled=True)
        year = update_form.selectbox("Installation Year", year_list, index=year_list.index(selected_year) if selected_year in year_list else 0)
        new_population = update_form.number_input("Population", min_value=0, value=population)

        update_record = update_form.form_submit_button(label="Update Record")

        # Update logic
        if update_record:
            # Update the population in the session state DataFrame
            st.session_state.df_reshaped.loc[
                (st.session_state.df_reshaped['states'] == selected_state) & 
                (st.session_state.df_reshaped['year'] == selected_year), 
                'population'
            ] = new_population

            # Save updated DataFrame to the CSV
            try:
                st.session_state.df_reshaped.to_csv('data/us-population-2010-2019-reshaped.csv', index=False)
                st.success(f"Record for {selected_state} updated successfully!")
                
                # Trigger app refresh
                st.rerun()

            except Exception as e:
                st.error(f"Error saving file: {e}")
    else:
        st.warning("No record found for the selected state and year.")


