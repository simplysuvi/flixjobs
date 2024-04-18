import requests
from time import sleep
from random import randint
import json

# Function to get all jobs
def get_all_jobs(pages):
    for page in pages:
        response = requests.get(f'https://jobs.netflix.com/api/search?page={page}')
        resp_text = json.loads(response.text)
        
        # Check for successful response and whether search results exist on the page in iteration
        if not resp_text['records']['postings'] or response.status_code != 200:
            print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
        else:
            yield from get_job_infos(response)
        sleep(randint(4,6))

# Function to extract job information
def get_job_infos(response):
    netflix_jobs = json.loads(response.text)
    if not netflix_jobs['records']['postings']:
         print('NO RESULTS!')
    else:
        for website in netflix_jobs['records']['postings']:
            yield {
                'Id': website['external_id'],
                'Title': website['text'],
                'Team': website.get('team','subteam')[0],
                'Location': website['location'],
                'Posting Date Time': website['created_at'],
                'Job URL': f"https://jobs.netflix.com/jobs/{website['external_id']}"
            }


def main():
  response = get('https://jobs.netflix.com/api/search')
  result = json.loads(response.text)
  num_pages = result['info']['postings']['num_pages']
  
  pages = [str(i) for i in range(1,num_pages+1)]
  jobs_data = []

  for job_info in get_all_jobs(pages):
      jobs_data.append(job_info)

  with open('data/netflix_jobs_new.json', 'w') as f:
      json.dump(jobs_data, f)



if __name__ == "__main__":
    main()
