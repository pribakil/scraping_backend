import json
from datetime import datetime


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

    return {
        "data": paged_jobs,
        "pages_count": pages_count,
        "items_count": items_count,
    }

def parse_mediacongo_job_to_dict(htmlJob):
    tds = htmlJob.css("td")
    base_url = "https://www.mediacongo.net"
    return{
        "link": f"{base_url}/{tds[1].css("a::attr(href)").get(default='').strip()}",
        "name": tds[1].css("strong::text").get(default='').strip(), # Just take the title not the code
        "organization": tds[2].css("::text").get(default='').strip(),
        "location": tds[3].css("::text").get(default='').strip(),
        "source_url": base_url,
        "source_name": "Media Congo",
        "published_date": tds[4].css("::text").get(default='').strip(),
    }

def parse_emploicd_job_to_dict(htmlJob):

    card_job_detail = htmlJob.css(".card-job-detail")
    base_url = "https://www.emploi.cd"
    return{
        "link": f"{base_url}{card_job_detail.css('h3 a::attr(href)').get(default='').strip()}",
        "name": card_job_detail.css("h3 a::text").get(default='').strip(),
        "organization": card_job_detail.css(".company-name::text").get(default='').strip(),
        "location": card_job_detail.xpath(".//ul/li[contains(text(), 'Région de')]/strong/text()").get(default='').strip(),
        "source_url": base_url,
        "source_name": "Emploi CD",
        "published_date": card_job_detail.css("time::text").get(default='').strip(),
    }

def get_parsed_unique_jobs(parse_function, jobs):
    data = [parse_function(job) for job in jobs]
    unique_data = {frozenset(item.items()):item for item in data}.values() # Remove duplicates
    return unique_data