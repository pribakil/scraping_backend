
from fastapi import FastAPI
from services.general import get_all_links_by_url
from services.get_jobs import get_mediacd_jobs_by_search_key

app = FastAPI()

@app.get("/jobs")
async def get_it_jobs():
    search_keys = ["developpeur", "programmeur", "webmaster", "IT", "logiciel", "programmation", "informatique"]
    jobs = []

    for key in search_keys:
        jobs.extend(get_mediacd_jobs_by_search_key(key))

    return { "data": jobs, "count": len(jobs) }

@app.get("/links")
async def get_links(url:str, go_deep:bool=False):
    return get_all_links_by_url(url, go_deep)