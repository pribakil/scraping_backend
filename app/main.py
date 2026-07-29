
from math import e

from fastapi import FastAPI, Query
from pydantic import BaseModel
from app.services.general import get_all_links_by_url
from app.services.get_jobs import get_mediacd_jobs_by_search_key
from app.tutorial.tutorial.utils import get_jobs
from typing import Annotated

app = FastAPI()

class FilterType(BaseModel):
    key: str
    value: str
@app.get("/jobs")
async def get_it_jobs(page: int = Query(default=1, gt=0) , page_size: int = Query(default=10, gt=0), search: str | None = None, category: str = "Jobs", filters: list[FilterType] | None = None):
    print("Filters", filters)
    if category == "Jobs":    
        responseData = get_jobs(search, page, page_size)
        return responseData
    elif category == "Tenders":
        #raise NotImplementedError("Tenders not implemented yet")

        return {"data":[]}

    elif category == "Real Estate":
            #raise NotImplementedError("Real Estate not implemented yet")
        return {'data':[]}
    else:
        raise NotImplementedError(f"Category {category} not supported.")

@app.get("/links")
async def get_links(url:str, go_deep:bool=False):
    return get_all_links_by_url(url, go_deep)