#!/usr/bin/env python3
import time
import requests
import pandas as pd


class Chaac:
    def __init__(
            self,
        country_codes):
        """
        Constructor to obtain the published works by publishers
         from the OpenAlex database.
         The filtering URL is
         https://api.openalex.org/publishers?filter=country_codes:CO
         By default, it fetches publisher from Colombia

        Parameters:
        -----------
         country_codes: str
        ISO 3166-1 alfa-2 country code(2- letter code) of the country
        """
        self.country_codes = country_codes
        self.base_url = f"https://api.openalex.org/publishers?filter=country_codes:{country_codes}"
        self.count_levels = [{'level': 0, 'to_count_key': 'meta'},
                             {'level': 1, 'to_count_key': 'count'}]
        self.results_key = 'results'
        self.page_key = "page"
        self.per_page_key = "per_page"
        self.sleep = 0.1

    def pagination(self):
        """
        Method to obtain the complete information of count from the
            URL of the OpenAlex API.
            By default, OpenAlex display 25 results per pages.
            For Example, in OpenAlex API for Colombia is:
            {'meta':
                {'count': 104,
                  'db_response_time_ms':12,
                  'page': 1,
                  'per_page': 25
                  }
               }
            {'results':[...]}

        Parameters:
        -------
        None

        Return:
        --------
         List of all publishers with all the information provided in OpenAlex.
        """

        response = requests.get(self.base_url)
        if response.status_code == 200:
            data = response.json()
        try:
            if data["meta"]["count"] != 0:
                print("There is information for the entered country code.")
                page = 1
                r = []
                j = requests.get(
                    f'{self.base_url}&{self.page_key}={page}&{self.per_page_key}=100')
                if j.status_code == 200:
                    count = j.json()
                    for m in set([d.get('level') for d in self.count_levels]):
                        count = count.get([d.get('to_count_key')
                                           for d in self.count_levels if d.get('level') == m][0])
            if isinstance(count, int) and count:
                r = r + j.json().get(self.results_key)
                npages = count // 100
                if count % 100:
                    npages += 1
                for page in range(2, npages + 1):
                    print(page, end='\r')
                    url = f'{self.base_url}&{self.page_key}={page}&{self.per_page_key}=100'
                    j = requests.get(url)
                    time.sleep(self.sleep)
                    if j.status_code == 200:
                        r = r + j.json().get(self.results_key)
            return r
        except Exception:
            return None

    def get_publisher_ids(self):
        """
        Obtain the IDs of all the publisher
        For example, for Colombia, the ID of the National University
            in OpenAlex is: P4310318911
        The identifiers for publishers in the OpenAlex database
        will always start with the letter P
        Parameters:
        ----------
        None
        """
        try:
            df = pd.DataFrame(self.pagination())
            df = df.loc[:, ["id", "display_name",
                            "works_count", "sources_api_url"]]
            publisher = []
            for index, row in df.iterrows():
                publisher.append(row["id"])
            pub = [element.rsplit("/", 1)[-1] for element in publisher]
            return pub
        except Exception:
            return None

    def Works(self, email: str = " ", output: str = 'opnealexCO_publisher'):
        """
        Method to obtain all the published works for each publisher.
        The identifiers of each publisher are printed as the requests are made.

        Parameters:
        ---------
        email: str
            Enter your email address in the 'email' variable.
            This will provide you with faster and more consistent
            response times when using the API.
        output : str
            Name of the output file in JSON format for all the works.
            By default = opnealexCO_publisher.json

        Return:
        ---------
        A JSON file of all jobs with:
            work_id
            work_display_name
            work_publication_year
            work_publication_date
            DOI
            publisher
            author_id
            author_name
            author_position
        """

        alls = []
        try:
            get_publisher_id = self.get_publisher_ids()
            for i in get_publisher_id:
                print(i)
                endpoint = "works"
                filters = ",".join((
                    f'primary_location.source.publisher_lineage:{i}',))
                cursor = '*'

                select = ",".join(('id',
                                    'display_name',
                                    'publication_year',
                                    'publication_date',
                                    'primary_location',
                                    'open_access',
                                    'authorships',
                                    'cited_by_count',
                                    'updated_date',))

                works = []
                while cursor:
                    url = f'https://api.openalex.org/{endpoint}?filter={filters}&select={select}&cursor={cursor}&mailto={email}'
                    page_with_results = requests.get(url).json()
                    results = page_with_results['results']
                    works.extend(results)
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
                            alls.append({'work_id': work['id'],
                                        'work_display_name': work['display_name'],
                                        'work_publication_year': work['publication_year'],
                                        'work_publication_date': work['publication_date'],
                                        "doi": doi,
                                        "publisher": revista,
                                        'author_id': author_id,
                                        'author_name': author_name,
                                        'author_position': author_position,
                                            })

                data = pd.DataFrame(alls)
                time.sleep(0.1)
            data.to_json(f"./{output}.json", orient='records')
        except Exception:
            print("""There are no jobs in the OpenAlex database for this country code. 
            Please try another ISO 3166-1 alpha-2 code.""")
