#!/usr/bin/env python3
r'''
works_colombia module
'''
import requests
import json
import pandas as pd
import time

def pagination(base_url,count_levels,results_key,page_key,per_page_key,per_page_value=100,sleep=0.1):
    '''
    Pagination for API with url:

     `f"{base_url}&{page_key}=1&{per_page_value}=100"`

    with the following minimal data scheme:
    ```
     {'level 0 to count key': dict,
         ...
         {'level n to count key': int},
      results_key: list, # with the results
     }

    ```
    OpenAlex example
    ```
     {'meta':
         {'count': 1223,...},
      'results': [...]
     }
    ```
    → count_levels=[{'level':0,'to_count_key':'meta'},{'level':1,'to_count_key':'count'}]
    '''
    per_page_value=per_page_value
    page=1
    r=[]
    j=requests.get(f'{base_url}&{page_key}={page}&{per_page_key}={per_page_value}')
    if j.status_code==200:
        count=j.json()
        for l in set([d.get('level') for d in count_levels]):
            count=count.get( [d.get('to_count_key') for d in count_levels if d.get('level')==l][0]  )

    if isinstance(count,int) and count:
        r = r+j.json().get(results_key) # First page
        npages=count//per_page_value
        if count%per_page_value:
            npages+=1


    for page in range(2,npages+1):
        print(page,end='\r')
        url=f'{base_url}&{page_key}={page}&{per_page_key}={per_page_value}'
        j=requests.get(url)
        time.sleep(sleep) # Avoid overload the API
        if j.status_code==200:
            r = r+j.json().get(results_key) # First page

    return r

def all_works(base_url):
  #base_url= "ttps://api.openalex.org/publishers?filter=country_codes:CO"
  count_levels=[{'level':0,'to_count_key':'meta'},{'level':1,'to_count_key':'count'}] # data scheme for count in JSON
  per_page_key='per-page'
  page_key='page'
  results_key='results' # Must be at the first level in the JSON output
  r=pagination(base_url,count_levels,results_key,page_key,per_page_key,per_page_value=100,sleep=0.1)  
  df = pd.DataFrame(r)  

  df1 = df.loc[:,["id","display_name","works_count","sources_api_url"]]
  publisher =[]
  for index, row in df1.iterrows():
    publisher.append(row["id"])
  pub = [element.rsplit("/",1)[-1] for element in publisher]

  try:
    with open("opnealex_co_publisher.json", "r") as f:
      alls = json.load(f)
  except FileNotFoundError:
      alls = []
  for i in pub[-3:-1]:
    print(i)
   
  ### ADD YOUR EMAIL to use the polite pool
    email = ""

    endpoint = "works"
    filters = ",".join((
      f'primary_location.source.publisher_lineage:{i}',
    ))
    

    cursor = '*'

    select = ",".join((
        'id',
        'display_name',
        'publication_year',
        'publication_date',
        'primary_location',
        'open_access',
        'authorships',
        'cited_by_count',
        'updated_date',
    ))

    works = []
    loop_index = 0
    while cursor:

      # set cursor value and request page from OpenAlex
      url = f'https://api.openalex.org/{endpoint}?filter={filters}&select={select}&cursor={cursor}&mailto={email}'
      page_with_results = requests.get(url).json()

      results = page_with_results['results']
      works.extend(results)

      # update cursor to meta.next_cursor
      cursor = page_with_results['meta']['next_cursor']

    
    
    for work in works:
        revista = work['primary_location']["source"]["display_name"]
        doi = work["primary_location"]["landing_page_url"]
        for authorship in work['authorships']:
            if authorship:
                author = authorship['author']
                author_id = author['id'] if author else None
                author_name = author['display_name'] if author else None
                author_position = authorship['author_position']

                alls.append({
                            'work_id': work['id'],
                            'work_display_name': work['display_name'],
                            'work_publication_year': work['publication_year'],
                            'work_publication_date': work['publication_date'],
                            "doi" : doi,
                            #"host_organization": host_organization,
                            "publisher" : revista,
                            'author_id': author_id,
                            'author_name': author_name,
                            'author_position': author_position,
                        })
      
   
    
  
    df =  pd.DataFrame(alls)
    df.to_json("openalex_co_publisher.json",orient='records')
    time.sleep(0.1)
  return df




if __name__ == '__main__':
    r'''
    Hello main
    '''
    hello()
