import requests
url ='https://dummyjson.com/products'

all_products =[]

skip = 0
limit =30
total = None
while total is None or skip < total:
    params = {
        'skip': skip,
        'limit': limit
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print("API failed :",e)
        break

    total = data['total']

    all_products.extend(data['products'])
    skip+=limit
print(len(all_products))


