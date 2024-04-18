import os
import pandas as pd
import requests
from datetime import datetime, timedelta

def load_data():
    """Loads data from JSON files into pandas DataFrames."""
    master = pd.read_json('data/netflix_jobs_master.json')
    previous = pd.read_json('data/netflix_jobs_last.json')
    current = pd.read_json('data/netflix_jobs_new.json')
    for df in [master, previous, current]:
        df['Posting Date Time'] = pd.to_datetime(df['Posting Date Time'])
    return master, previous, current

def find_jobs(master, previous, current):
    """Identify new, recently removed, and all removed jobs."""
    new_jobs = current[~current['Id'].isin(master['Id'])]
    recently_removed_jobs = previous[~previous['Id'].isin(current['Id'])]
    new_jobs.to_json('data/netflix_jobs_recently_added.json', orient='records', date_format='iso')
    recently_removed_jobs.to_json('data/netflix_jobs_recently_removed.json', orient='records', date_format='iso')
    all_removed_jobs = previous[previous['Id'].isin(master['Id']) & ~previous['Id'].isin(current['Id'])]
    return new_jobs, recently_removed_jobs, all_removed_jobs

def update_job_status(master, removed_jobs):
    """Update days active and job status for each job."""
    current_date = datetime.now()
    master['Days Active'] = master.apply(
        lambda row: (current_date - pd.to_datetime(row['Posting Date Time'])).days if row['Id'] not in removed_jobs['Id'].values else (current_date - timedelta(days=1) - pd.to_datetime(row['Posting Date Time'])).days, 
        axis=1
    )
    master['Job Status'] = master.apply(
        lambda row: 'Closed' if row['Id'] in removed_jobs['Id'].values else 'Open', 
        axis=1
    )
    return master


def main():
    master, previous, current = load_data()
    new_jobs, recently_removed_jobs, all_removed_jobs = find_jobs(master, previous, current)
    
    master = pd.concat([master, new_jobs], ignore_index=True)
    master.to_json('data/netflix_jobs_master.json', orient='records', date_format='iso')
    master = update_job_status(master, all_removed_jobs)
    master.to_json('data/netflix_all_jobs.json', orient='records', date_format='iso')
    current.to_json('data/netflix_jobs_last.json', orient='records', date_format='iso')

if __name__ == '__main__':
    main()
