from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

def get_mediacd_jobs_by_search_key(search_key):
    mediacg_url = f"http://mediacongo.net/emplois-search-{search_key}-tri-offres_recentes-page-1.html"
    html = urlopen(mediacg_url)
    soup = BeautifulSoup(html.read(), 'html.parser')
    jobs = soup.find("table",class_="table_datas").tr.find_next_siblings()
    data = [to_dict(job) for job in jobs]
    unique_data = {frozenset(item.items()):item for item in data}.values() # Remove duplicates
    return list(unique_data)



def to_dict(htmlJob):
    tds = htmlJob.find_all("td")

    function = tds[1].find("strong").get_text(strip=True) # Just take the title not the code

    return{
        "function": function,
        "organization": tds[2].get_text(strip=True),
        "location": tds[3].get_text(strip=True),
        "published_date": tds[4].get_text(strip=True),
    }