import json
from datetime import datetime
import uuid

from attr import filters


SEARCHABLE_FIELDS = (
    "name",
    "organization",
    "location",
    "source_name",
    "source_url",
    "published_date",
)


def get_jobs(search=None, page: int | None = 1, page_size: int | None = 10) -> dict[str, int | list[dict]]:
    page = page or 1
    page_size = page_size or 10
    with open("tutorial/jobs.json", "r", encoding="utf-8") as f:
        jobs = json.load(f)

    # search for jobs that contain the search term in any of the searchable fields
    if search:
        search = search.lower().strip()

        jobs = [
            job
            for job in jobs
            if any(
                search in str(job.get(field, "")).lower()
                for field in SEARCHABLE_FIELDS
            )
        ]

    sorted_jobs = sorted(
        jobs,
        key=lambda job: datetime.strptime(
            job["published_date"],
            "%d.%m.%Y"
        ),
        reverse=True,
    )

    items_count = len(sorted_jobs)
    pages_count = (items_count + page_size - 1) // page_size if page_size else 0

    # Pagination Implementation
    start = (page - 1) * page_size
    end = start + page_size
    paged_jobs = list(sorted_jobs)[start:end]

    has_previous_page = page > 1
    has_next_page = page < pages_count if pages_count else False

    return {
        "data": paged_jobs,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "items_count": items_count,
            "pages_count": pages_count,
            "hasPreviousPage": has_previous_page,
            "hasNextPage": has_next_page,
        },
        "filters":[]
    }

def parse_mediacongo_job_to_dict(htmlJob):
    tds = htmlJob.css("td")
    base_url = "https://www.mediacongo.net"
    return{
        "id": uuid.uuid4().hex,
        "category":"Jobs",
        "title": tds[1].css("strong::text").get(default='').strip(), # Just take the title not the code
        "description":"",
        "source":{
            "id": uuid.uuid4().hex,
            "name": "Media Congo",
            "logo": "",
            "website": base_url,
            "verified": True,
        },
        "image":None,
        "location": tds[3].css("::text").get(default='').strip(),
        "externalUrl": f"{base_url}/{tds[1].css("a::attr(href)").get(default='').strip()}",
        "published_date": tds[4].css("::text").get(default='').strip(),
        "organization": tds[2].css("::text").get(default='').strip(),
    }

def parse_emploicd_job_to_dict(htmlJob):

    card_job_detail = htmlJob.css(".card-job-detail")
    base_url = "https://www.emploi.cd"
    return{
        "id": uuid.uuid4().hex,
        "category":"Jobs",
        "externalUrl": f"{base_url}{card_job_detail.css('h3 a::attr(href)').get(default='').strip()}",
        "title": card_job_detail.css("h3 a::text").get(default='').strip(),
        "description":"",
        "source":{
                    "id": uuid.uuid4().hex,
                    "name": "Emploi CD",
                    "logo": "",
                    "website": base_url,
                    "verified": True,
                },
        "image":None,
        "organization": card_job_detail.css(".company-name::text").get(default='').strip(),
        "location": card_job_detail.xpath(".//ul/li[contains(text(), 'Région de')]/strong/text()").get(default='').strip(),
        "published_date": card_job_detail.css("time::text").get(default='').strip(),
    }

def get_parsed_unique_jobs(parse_function, jobs):
    data = [parse_function(job) for job in jobs]
    # unique_data = {frozenset(item.items()):item for item in data}.values() # Remove duplicates TODO:"fix the unique_data operation"
    return data # unique_data