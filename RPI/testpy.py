from google.cloud import bigquery

q=bigquery.Client()
print(type(q))