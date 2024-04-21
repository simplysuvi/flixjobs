import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import calplot
import os
import json
import pytz
from datetime import datetime, timedelta
from plot_functions import plot_timeline, plot_dayoftheweek, plot_months, plot_timeoftheday, plot_jobs_by_location, plot_jobs_by_team, plot_jobs_by_subteam, plot_daysActive

st.set_page_config(page_title='Netflix Jobs Dashboard', layout="wide", page_icon='assets/favicon.ico')


def clear_multi():
    st.session_state.multiselect1 = []
    st.session_state.multiselect2 = []
    st.session_state.multiselect3 = []
    st.session_state.multiselect4 = []
    return


st.title(":red[N]etflix Jobs Dashboard :globe_with_meridians:")

# LOAD DATA
jobs_df = pd.read_json('data/netflix_jobs_master.json')
recent_removed_jobs = pd.read_json('data/netflix_jobs_recently_removed.json')
recent_added_jobs = pd.read_json('data/netflix_jobs_recently_added.json')


# PREPROCESS DATA
jobs_df['Posting Date'] = pd.to_datetime(jobs_df['Posting Date'])
jobs_df['Posting Date Time'] = pd.to_datetime(jobs_df['Posting Date Time'])

jobs_df['Posting Date Time'] = jobs_df['Posting Date Time'].dt.tz_convert('America/New_York')
jobs_df['Posting Date'] = jobs_df['Posting Date'].dt.strftime('%B %d, %Y')

# Extract day of the week and posting time
jobs_df['Day of Week'] = jobs_df['Posting Date Time'].dt.day_name()
jobs_df['Posting Time'] = jobs_df['Posting Date Time'].dt.time
jobs_df['Hour'] = jobs_df['Posting Date Time'].dt.hour
jobs_df['Month'] = (pd.to_datetime(jobs_df['Posting Date'])).dt.to_period('M').dt.strftime('%B')
# Sort the DataFrame by 'Posting Date Time' in descending order
jobs_df = jobs_df.sort_values(by='Posting Date Time', ascending=False)



# IDENTIFY RECENTLY ADDED AND REMOVED JOBS
added_jobs = pd.DataFrame()
removed_jobs = pd.DataFrame()
if not recent_added_jobs.empty:
    recent_added_ids = recent_added_jobs['Id'].tolist()
    added_jobs = jobs_df[jobs_df['Id'].isin(recent_added_ids)]

if not recent_removed_jobs.empty:
    recent_removed_ids = recent_removed_jobs['Id'].tolist()
    removed_jobs = jobs_df[jobs_df['Id'].isin(recent_removed_ids)]


# SIDEBAR FOR FILTERS
with st.sidebar:
    st.title('Job Filters')

    # SelectBox for Team
    selected_teams = st.multiselect(
        'Select Teams',
        options=jobs_df['Team'].unique().tolist(),
        default=None,
        placeholder='Choose Teams',
        key="multiselect1"
    )

    # SelectBox for Locations
    selected_locations = st.multiselect(
        'Select Locations',
        options=jobs_df['Location'].unique().tolist(),
        default=None,
        placeholder='Choose Locations',
        key="multiselect2"
    )

    # SelectBox for Posting Date
    selected_dates = st.multiselect(
        'Select Posting Dates',
        options=jobs_df['Posting Date'].unique().tolist(),
        default=None,
        placeholder='Choose Job Posting Dates',
        key="multiselect3"
    )

  
    # SelectBox for Job Status
    selected_job_status = st.multiselect(
        'Select Job Status',
        options=jobs_df['Job Status'].unique().tolist(),
        default=None,
        placeholder='Choose Job Status',
        key="multiselect4"
    )


    # Button to reset filters
    st.button('Reset Filters',on_click=clear_multi, type="primary")

    # Filter based on selection
    if selected_teams:
        jobs_df = jobs_df[jobs_df['Team'].isin(selected_teams)]
    if selected_locations:
        jobs_df = jobs_df[jobs_df['Location'].isin(selected_locations)]
    if selected_dates:
        jobs_df = jobs_df[jobs_df['Posting Date'].isin(selected_dates)]
    if selected_job_status:
        jobs_df = jobs_df[jobs_df['Job Status'].isin(selected_job_status)]


open_jobs = (jobs_df['Job Status'].value_counts()).reset_index()
with st.container(border=False):
    cols = st.columns(3)
    with cols[0]:
        st.metric(label="**TOTAL JOBS**", value=f"{len(jobs_df)}")
    for i, row in open_jobs.iterrows():
        job_status = row['Job Status']
        count = row['count']
        if job_status == 'Open':
            label = f"**:green[{job_status.upper()}]**"
            delta = len(added_jobs) if (not added_jobs.empty) else 0
        if job_status == 'Closed':
            label = f"**:red[{job_status.upper()}]**"
            delta = -(len(removed_jobs)) if (not removed_jobs.empty) else -1
        with cols[i+1]:
            st.metric(label=label, value=count, delta=delta)


columns_to_display = [col for col in jobs_df.columns if col not in ['Id', 'Posting Date Time','Day of Week','Posting Time','Hour', 'Month', 'Team']]
st.dataframe(jobs_df[columns_to_display],use_container_width=True,hide_index=True)

# Read timestamp from file
with open("last_updated.txt", "r") as file:
    last_updated = file.read()
    last_updated_dt = pd.to_datetime(last_updated)
    last_updated_dt_ny = last_updated_dt.tz_localize('UTC').tz_convert('America/New_York')

# Display last updated time
st.caption(f"Last updated: {last_updated_dt_ny.strftime('%B %d, %Y %H:%M')}")
st.caption("All times in Eastern Daylight Time (EDT).")
st.caption("Source: [Netflix Jobs](%s)" % "https://jobs.netflix.com/")


with st.expander('**Recently :green[Added] Jobs**'):
    if not added_jobs.empty:
        st.dataframe(added_jobs[['Title', 'Subteam', 'Posting Date', 'Location', 'Job URL']], use_container_width=True, hide_index=True)
    else:
        st.error("No new jobs added recently.")


with st.expander('**Recently :red[Closed] Jobs**'):
    if not removed_jobs.empty:
        st.dataframe(removed_jobs[['Title', 'Team', 'Location', 'Days Active']], use_container_width=True, hide_index=True)
    else:
        st.error("No jobs have been closed recently.")


if not jobs_df.empty:

    # Plotting the number of roles in each team
    fig_jobsByTeam = plot_jobs_by_team(jobs_df)
    st.plotly_chart(fig_jobsByTeam, use_container_width=True)

    # Plotting the number of roles in each subteam
    fig_jobsBySubteam = plot_jobs_by_subteam(jobs_df)
    st.plotly_chart(fig_jobsBySubteam, use_container_width=True)
    
    # Plotting the number of roles in each location
    fig_jobsByLocation = plot_jobs_by_location(jobs_df)
    st.plotly_chart(fig_jobsByLocation, use_container_width=True)
    
    # Plotting the timeline of job postings
    fig_timeline = plot_timeline(jobs_df)
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Plotting the distribution of days active for the job postings
    fig_daysActive = plot_daysActive(jobs_df)
    st.plotly_chart(fig_daysActive, use_container_width=True)

    # Plotting the distribution of job postings by month
    fig_months = plot_months(jobs_df)
    st.plotly_chart(fig_months, use_container_width=True)
    
    # Plotting the distribution of job postings by day of the week
    fig_dayoftheWeek = plot_dayoftheweek(jobs_df)
    st.plotly_chart(fig_dayoftheWeek, use_container_width=True)
    
    # Plotting the distribution of job postings by time of the day
    fig_timeoftheDay = plot_timeoftheday(jobs_df)
    st.plotly_chart(fig_timeoftheDay, use_container_width=True)
    
else:
    st.error('No data to show')


# Add a copyright notice at the bottom of the app
current_year = datetime.now().year
st.markdown(f"---\n**©** {current_year} Made and Managed with :heart: by **Suvrat Jain**. This app is not affiliated with Netflix Inc. in any way.", unsafe_allow_html=True)
