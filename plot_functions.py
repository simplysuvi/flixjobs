import plotly.express as px


# Function to plot the timeline of job postings
def plot_timeline(df):
    # Create a new dataframe for plotting, counting the number of jobs per date
    timeline_df = df.resample('ME', on='Posting Date Time').count().reset_index()
    
    fig = px.line(timeline_df, x='Posting Date Time', y='Title',
                  title='Timeline of Netflix Job Postings', markers=True,
                 labels={'Title': 'Number of Jobs', 'Posting Date Time': 'Date'})
    fig.update_traces(marker=dict(color='black',size=8),
                      line=dict(color='red',width=3),
                      hovertemplate='<b>Date: %{x}</b><br><b>Jobs Posted: %{y}</b>')

    # Update layout
    fig.update_layout(xaxis_title='Date', yaxis_title='Number of Job Postings', xaxis_tickangle=-45)
    
    return fig

# Function to plot the distribution of job postings by day of the week
def plot_dayoftheweek(df):
    # Calculate counts of each day
    day_counts = df['Day of Week'].value_counts()

    # Create Plotly pie chart
    fig = px.pie(
        names=day_counts.index,
        values=day_counts.values,
        title="Distribution of Job Postings by Day of the Week"
    )
    
    fig.update_traces(
        hoverinfo='label+percent',
        text=day_counts.index,
        textinfo='text+percent'
    )

    return fig

def plot_months(df):
    # Count occurrences of each month
    monthly_counts = df['Month'].value_counts().sort_index()
    
    fig = px.line(
        x=monthly_counts.index,
        y=monthly_counts.values,
        markers=True,
        title="Distribution of Job Postings by Month",
        labels={"x": "Month", "y": "Number of Job Postings"}
    )
    fig.update_traces(marker=dict(color='black',size=6),
                      line=dict(color='red',width=3),
                      hovertemplate='<b>Month: %{x}</b><br><b>Jobs Posted: %{y}</b>')
    fig.update_xaxes(range=[1,12], dtick=1)
    return fig

def plot_timeoftheday(df):
    # Count occurrences of each hour
    hour_counts = df['Hour'].value_counts().sort_index()

    # Create Plotly line chart
    fig = px.line(
        x=hour_counts.index,
        y=hour_counts.values,
        markers=True,
        title="Distribution of Job Postings by Hour of the Day",
        labels={"x": "Hour of the Day", "y": "Number of Job Postings"}
    )
    fig.update_traces(marker=dict(color='black',size=6),
                      line=dict(color='red',width=3),
                      hovertemplate='<b>Hour of the Day: %{x}</b><br><b>Jobs Posted: %{y}</b>')

    # Set x-axis range from 0 to 23 (for 24-hour format)
    fig.update_xaxes(range=[0, 23], dtick=1)
    fig.update_xaxes(tickvals=list(range(24)), ticktext=["12 AM" if hour == 0 else f"{hour} AM" if hour < 12 else "12 PM" if hour == 12 else f"{hour-12} PM" for hour in range(24)])

    return fig

# Function to plot the number of roles in each country
def plot_jobs_by_location(df):
    country_counts = df['Location'].value_counts()
    country_counts = country_counts.sort_values(ascending=True)

    # Convert to DataFrame for Plotly
    country_counts_df = country_counts.reset_index()
    country_counts_df.columns = ['Location', 'Number of Roles']

    # Create Plotly bar chart using the DataFrame
    fig = px.bar(country_counts_df, y='Location', x='Number of Roles',
                 text='Number of Roles',
                 title='Number of Netflix Job Roles by Country',
                 labels={'Number of Roles': 'Number of Roles', 'Location': 'Location'},
                 color='Number of Roles',
                 color_continuous_scale='Reds')
    fig.update_layout(showlegend=False)
    fig.update(layout_coloraxis_showscale=False)

    fig_height = len(country_counts_df) * 50
    fig.update_layout(height=fig_height)

    return fig


# Function to plot the number of roles in each team
def plot_jobs_by_team(df):
    team_counts = df['Team'].value_counts()
    team_counts = team_counts.sort_values(ascending=True)

    # Convert to DataFrame for Plotly
    team_counts_df = team_counts.reset_index()
    team_counts_df.columns = ['Team', 'Number of Roles']

    # Create Plotly bar chart using the DataFrame
    fig = px.bar(team_counts_df, y='Team', x='Number of Roles',
                 text='Number of Roles',
                 title='Number of Netflix Job Roles by Team',
                 labels={'Number of Roles': 'Number of Roles', 'Team': 'Team'},
                 color='Number of Roles',
                 color_continuous_scale='Reds')
    fig.update_layout(showlegend=False)
    fig.update(layout_coloraxis_showscale=False)

    fig_height = len(team_counts_df) * 50
    fig.update_layout(height=fig_height)

    return fig


def plot_daysActive(df):
    # Create a histogram to show the distribution of 'Days Active'
    fig = px.histogram(df, x='Days Active',
                    title='Distribution of Days Jobs Have Been Active',
                    labels={'Days Active': 'Days Active'},
                    nbins=40,
                    color_discrete_sequence=['#2CA02C'])

    fig.update_layout(
        xaxis_title='Days Active',
        yaxis_title='Number of Jobs',
        bargap=0.2,  # Adjust the gap between bars
    )

    return fig