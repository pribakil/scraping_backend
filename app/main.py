
from fastapi import FastAPI, Query
from app.services.general import get_all_links_by_url
from app.services.get_jobs import get_mediacd_jobs_by_search_key
from app.tutorial.tutorial.utils import get_jobs
from typing import Annotated

app = FastAPI()

@app.get("/jobs")
async def get_it_jobs(page: int = Query(default=1, gt=0) , page_size: int = Query(default=10, gt=0), search: str | None = None):
    """   search_keys = ["developpeur", "programmeur", "webmaster", "IT", "logiciel", "programmation", "informatique"]
    jobs = []
    for key in search_keys:
        jobs.extend(get_mediacd_jobs_by_search_key(key)) """

    jobs = get_jobs(search, page, page_size)
    return jobs

@app.get("/links")
async def get_links(url:str, go_deep:bool=False):
    return get_all_links_by_url(url, go_deep)