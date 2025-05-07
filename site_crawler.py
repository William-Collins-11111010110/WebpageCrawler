import requests
from bs4 import BeautifulSoup
import csv
import time
import argparse
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser


ALL_USER_AGENTS = '*'


def page_crawler(url, debugLog = False):
    # if not robots_manager.can_fetch(url):
    #     print(f'Skipping {url} - not allowed by robots.txt')
    #     return None
        
    if debugLog: print(f'Processing {url}') 

    try:
        response = requests.get(url)
        response.raise_for_status()

        # Get source domain and protocol from url
        parse_source = urlparse(url)
        source_domain_protocol = f"{parse_source.scheme}://{parse_source.netloc}"

        soup = BeautifulSoup(response.text, 'html.parser')
        content_type = response.headers.get('Content-Type')
        status_code = response.status_code
        title = soup.title.string if soup.title else "No title"

        # Initialize lists for storing urls
        list_of_external_sites = []
        list_of_local_pages = []
        
        # Find all <a> tags with an href attribute
        links = [a['href'] for a in soup.find_all('a', href=True)]
        
        # Extract domains from external links and add to list
        for link in links:
            if link.startswith(("http://", "https://")):
                try:
                    parsed = urlparse(link)
                    domain_with_protocol = f"{parsed.scheme}://{parsed.netloc}"

                    if domain_with_protocol == source_domain_protocol:
                        list_of_local_pages.append(link)
                    elif domain_with_protocol and domain_with_protocol not in list_of_external_sites:
                        list_of_external_sites.append(domain_with_protocol)
                except:
                    continue

        # Local domain links
        filtered_links = [urljoin(source_domain_protocol, link) for link in links if link.startswith('/')]
        list_of_local_pages.extend(filtered_links)
        extra_filtered_links = list(dict.fromkeys(list_of_local_pages))  # Removes duplicate urls

        return {
            "status_code": status_code,
            "title": title,
            "content_type": content_type,
            "list_of_links": extra_filtered_links,
            "list_of_external_sites": list_of_external_sites,
            "num_internal_links": len(extra_filtered_links),
            "num_external_links": len(list_of_external_sites)
        }
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None


def write_links(list_of_pages, includeExternal = False): #Prints to csv file
    fieldnames = ['url', 'status_code', 'content_type', 'title', 'num_outgoing_links']

    with open('crawl.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, row in list_of_pages.items():
            row_with_id = {'url': key}
            row_with_id['status_code'] = row['status_code']
            row_with_id['title'] = row['title']
            row_with_id['content_type'] = row['content_type']
            if includeExternal:
                row_with_id['num_outgoing_links'] = row["num_internal_links"] + row["num_external_links"]
            else:
                row_with_id['num_outgoing_links'] = row["num_internal_links"]
            writer.writerow(row_with_id)


def can_fetch(rp, url):
    return rp.can_fetch(ALL_USER_AGENTS, url)

def get_crawl_delay(rp):
    delay = rp.crawl_delay(ALL_USER_AGENTS)
    return 0 if delay is None else delay


def main():
    parser = argparse.ArgumentParser(description="Crawl a set of websites")
    parser.add_argument('--seeds', nargs='+', help='List of seed URLs to start crawling from')
    parser.add_argument('--max-pages', type=int, default=1000, help='Limit of pages to crawl')
    parser.add_argument('--max-depth', type=int, default=4, help= 'Limit of depth to crawl')
    parser.add_argument('--rate', type=float, default=1,help='How many requests/sec')
    parser.add_argument('--allow-external', action='store_true', help='Allowing urls outside seeds domain')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    
    max_pages = args.max_pages
    rate = args.rate
    seed_urls = args.seeds
    max_depth = args.max_depth
    allow_external = args.allow_external
    debug = args.debug
    list_of_pages = {}
    list_of_sites = seed_urls # Start with all seed URLs

    if debug: print(f'Processing {list_of_sites}')

    rp = RobotFileParser()
    
    while list_of_sites: 
        site_url = list_of_sites.pop()
        if site_url in list_of_pages:
            continue

        rp.set_url(site_url)

        try:
            rp.read()
        except Exception as e:
            print(f"Warning: Could not read robots.txt for {site_url}: {e}")
            rp = RobotFileParser()   # Optionally, reset or re-initialize rp if needed
        
        page_info = page_crawler(site_url, debug)
        if page_info is None: continue

        list_of_pages[site_url] = page_info

        to_visit = page_info["list_of_links"]
        if allow_external:
            list_of_sites.extend(page_info["list_of_external_sites"])
        delay_time = max(rate, get_crawl_delay(rp)) # Respect the crawl delay

        while to_visit and len(list_of_pages) < max_pages:
            new_url = to_visit.pop()
            
            if new_url not in list_of_pages and can_fetch(rp, new_url):
                time.sleep(delay_time)  
                
                page_info = page_crawler(new_url, debug)
                if page_info is not None:
                    list_of_pages[new_url] = page_info
                    to_visit.extend(page_info["list_of_links"])
                    if allow_external:
                        list_of_sites.extend(page_info["list_of_external_sites"])

    write_links(list_of_pages, allow_external)

if __name__ == '__main__':
    main()