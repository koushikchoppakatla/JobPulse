import requests

def scrape_jobs():

    url = "https://www.arbeitnow.com/api/job-board-api"

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        data = response.json()

        jobs = []

        for job in data.get("data", []):

            job_details = {
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("location"),
                "url": job.get("url")
            }

            jobs.append(job_details)

        return jobs

    except requests.RequestException as e:
        print("Error collecting jobs:", e)
        return []


if __name__ == "__main__":

    jobs = scrape_jobs()

    print("Total jobs collected:", len(jobs))

    for job in jobs[:10]:
        print("-------------------------")
        print("Title:", job["title"])
        print("Company:", job["company"])
        print("Location:", job["location"])
        print("URL:", job["url"])