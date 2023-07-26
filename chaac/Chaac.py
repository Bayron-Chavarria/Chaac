#!/usr/bin/env python3
import time
import requests
import pandas as pd

class Chaac:
   def __init__(
         self,
         per_page_value=100,
         sleep=0.1,
         country_codes: str = "CO"):
      """
      Constructor para obtener los trabajos publicados por publishers 
         de la base de datos de OpenAlex.
         La url del filtrado es https://api.openalex.org/publishers?filter=country_codes:CO
         Por defecto se toma los publisher de Colombia.

         Parámetros:
         -----------
         country_codes: str="CO"
            Codigo del país ISO 3166-1 alfa-2 (código de 2 letras)
      """
      self.base_url = f"https://api.openalex.org/publishers?filter=country_codes:{country_codes}"
      self.count_levels = [{'level': 0, 'to_count_key': 'meta'}, {
         'level': 1, 'to_count_key': 'count'}]
      self.results_key = f'results'
      self.page_key = f"page"
      self.per_page_key = f"per_page"
      self.per_page_value = per_page_value
      self.sleep = sleep

   def pagination(self):
      """ 
      Método para recorrer todos los resultados de la url de la API de OpenAlex.
         OpenAlex por defecto muestra 25 resultados por página.
         Ejemplo en OpenAlex para Colombia:
         {'meta':
                  {'count': 104,
                  'db_response_time_ms':12,
                  'page': 1,
                  'per_page': 25
                  }
               }
         {'results':[...]}

      Parámetros:
      -------
      Ninguno

      Retorna:
      --------
      Lista de todas las publisher con toda la información dada en OpenAlex.
      """

      response = requests.get(self.base_url)
      if response.status_code == 200:
         data = response.json()
         if data["meta"]["count"] != 0:
            print("Hay información para el el codigo de país recibido.")
         else:
            print("No hay información dada para el endpoint dado. Ingresa otro codigo ISO3166-2")
      page = 1
      r = []
      j = requests.get(
         f'{self.base_url}&{self.page_key}={page}&{self.per_page_key}=100')
      if j.status_code == 200:
         count = j.json()
         for l in set([d.get('level') for d in self.count_levels]):
               count = count.get(
                  [d.get('to_count_key')for d in self.count_levels if d.get('level') == l][0]
               )
      if isinstance(count, int) and count:
         r = r + j.json().get(self.results_key)  # Primera pagina
         npages = count // 100
         if count % 100:
               npages += 1
         for page in range(2, npages + 1):
               print(page, end='\r')
               url = f'{self.base_url}&{self.page_key}={page}&{self.per_page_key}=100'
               j = requests.get(url)
               time.sleep(self.sleep)  # Para evitar sobrecargar la API
               if j.status_code == 200:
                  r = r + j.json().get(self.results_key)  # Primera pagina
      return r
         

   def get_publisher_ids(self):
      """
      Obtiene los ID de todas las publisher
      Parámetros:
      ----------
      Ninguno
      """
      df = pd.DataFrame(self.pagination())
      df = df.loc[:, ["id", "display_name",
                        "works_count", "sources_api_url"]]
      publisher = []
      for index, row in df.iterrows():
         publisher.append(row["id"])
      pub = [element.rsplit("/", 1)[-1] for element in publisher]
      return pub

   def Works(self, email: str = " ", name: str = 'opnealexCO_publisher'):
      """
      Método para obtener todos los trabajos publicados 
         por cada publisher.
      Se imprime los identificadores de cada publisher a
         medida que se hace el requests.

      Parámetros:
      ---------
      email: str
         Poner su dirección de correo electrónico 
            en la variable email.
         Así le conseguirá tiempos de respuesta más rápidos 
            y consistentes al utilizar la API.
      name : str = 'opnealexCO_publisher'
         Nombre del archivo de salida en formato Json de todos los trabajos.
         
      Retorna:
      ---------
      DataFrame y un archivo json de todos los trabajos con:
      ID del trabajo en la API de OpenAlex ()
      Título del trabajo
      Año de publicación
      Día de publicación
      DOI
      Editorial
      ID del autor
      Nombre del autor
      Posición del autor en el trabajo

      """

      alls = []
      get_publisher_id = self.get_publisher_ids()
      for i in get_publisher_id:
         print(i)
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
         while cursor:

               # establece el valor del cursor y hace requests en OpenAlex
               url = f'https://api.openalex.org/{endpoint}?filter={filters}&select={select}&cursor={cursor}&mailto={email}'
               page_with_results = requests.get(url).json()

               results = page_with_results['results']
               works.extend(results)

               # actualiza cursos a meta.next_cursor
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
                                 "doi": doi,
                                 "publisher": revista,
                                 'author_id': author_id,
                                 'author_name': author_name,
                                 'author_position': author_position,
                                 })

         data = pd.DataFrame(alls)
         time.sleep(0.1)
      data.to_json(f"{name}.json", orient='records')
