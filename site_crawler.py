import requests
from bs4 import BeautifulSoup
import csv
import time
import argparse

  # Replace with your target URL
def page_crawler(url):
    print(f'Processing {url}')
    response = requests.get(url)

    #print(response.text)
    # print(response.status_code)
    # print(response.headers.get('Content-Type'))

    soup = BeautifulSoup(response.text, 'html.parser')
    content_type = response.headers.get('Content-Type')
    status_code = response.status_code
    title = soup.title.string
    #print(title)
    # Find all <a> tags with an href attribute
    links = [a['href'] for a in soup.find_all('a', href=True)]
    filtered_links = [link for link in links if link.startswith('/')]
    extra_filtered_links = list(dict.fromkeys(filtered_links))
    num_outgoing_links = len(extra_filtered_links)
   #print(num_outgoing_links)
    return {
        "status_code": status_code,
        "title": title,
        "content_type": content_type,
        "list_of_links": extra_filtered_links
        }
    
    # for link in extra_filtered_links:
    #     print(link)

def main():
    parser = argparse.ArgumentParser(description="Crawl a webpage")
    parser.add_argument('--seeds')
    parser.add_argument('--max-pages', type = int, default = 1000)
    parser.add_argument('--max-depth', type = int, default = 4)
    parser.add_argument('--rate', type = float, default = 1)
    args = parser.parse_args()
    max_pages = args.max_pages
    rate = args.rate
    seed_url = args.seeds
    max_depth = args.max_depth
    list_of_pages = {}
        
    page_info = page_crawler(seed_url)
    list_of_pages[seed_url] = page_info


    ## Visited dict/map with results (url, sode, title ...)
    ## To Visit List of urls
    # to_visit = page_info["list_of_links"]
    to_visit = [(1, path) for path in page_info["list_of_links"]]
    #print(page_info)

    # for link in links:
    #     print(link)
    while to_visit and len(list_of_pages) < max_pages:
        depth, new_path = to_visit.pop()
        new_url = seed_url + new_path
        if new_url not in list_of_pages:
            page_info = page_crawler(new_url)
            list_of_pages[new_url] = page_info
            time.sleep(rate)
            #if depth+1<=max_depth:
            to_visit.extend([(depth+1, path) for path in page_info["list_of_links"]])


    fieldnames = ['url', 'status_code', 'title', 'content_type', 'num_links']

    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, row in list_of_pages.items():
            row_with_id = {'url': key}
            row_with_id['status_code'] = row['status_code']
            row_with_id['title'] = row['title']
            row_with_id['content_type'] = row['content_type']
            row_with_id['num_links'] = len(row['list_of_links'])
            writer.writerow(row_with_id)


if __name__ == '__main__':
    main()