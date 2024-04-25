import os
import pandas as pd
from datetime import datetime, timedelta

def load_data():
    """Loads data from JSON files into pandas DataFrames."""
    master = pd.read_json('data/netflix_jobs_master.json')
    new = pd.read_json('data/netflix_jobs_new.json')  # Load new daily data

    for df in [master, new]:
        df['Posting Date Time'] = pd.to_datetime(df['Posting Date Time'])
        df['Posting Date'] = pd.to_datetime(df['Posting Date Time'].dt.date)
    return master, new

def update_master(master, new):
    """Update the master data with new jobs and mark closed jobs."""
    current_date = datetime.now()
    
    # Identify new jobs not previously in master
    new_jobs = new[~new['Id'].isin(master['Id'])]
    new_jobs['Job Status'] = 'Open'
    new_jobs['Days Active'] = 0  # Initialize days active for new jobs
    new_jobs.to_json('data/netflix_jobs_recently_added.json', orient='records', date_format='iso')

    # Append new jobs to the master DataFrame
    updated_master = pd.concat([master, new_jobs], ignore_index=True)

    # Determine recently closed jobs:
    # These are the jobs that are present in master, marked as 'Open', but not present in new data
    recently_closed_ids = master[(master['Id'].isin(updated_master['Id'])) & (master['Job Status'] == 'Open') & (~master['Id'].isin(new['Id']))]['Id']
    recently_closed_jobs = master[(master['Id'].isin(updated_master['Id'])) & (master['Job Status'] == 'Open') & (~master['Id'].isin(new['Id']))]
    recently_closed_jobs.to_json('data/netflix_jobs_recently_removed.json', orient='records', date_format='iso')
    
    updated_master['Job Status'] = updated_master.apply(
        lambda row: 'Closed' if row['Id'] in recently_closed_ids.values else row['Job Status'], axis=1
    )

    # Update Days Active for all jobs
    # Recalculate for open jobs and retain for closed jobs
    updated_master['Days Active'] = updated_master.apply(
        lambda row: (current_date - row['Posting Date']).days if row['Job Status'] == 'Open' else row['Days Active'],
        axis=1
    )

    return updated_master

def save_data(master):
    """Save the updated master data to JSON."""
    master.to_json('data/netflix_jobs_master.json', orient='records', date_format='iso')

def main():
    master, new = load_data()
    master = update_master(master, new)
    save_data(master)

if __name__ == '__main__':
    main()
