import requests
import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Jobs"

response = requests.get("https://himalayas.app/jobs/api", params={
    "categories": "Software-Engineering",
    "limit": 10,
    "offset": 0,
})

data = response.json()
clean_jobs = []

for job in data["jobs"]:
    min_sal = f"${job['minSalary']}" if job["minSalary"] is not None else "Not Specified"
    max_sal = f"${job['maxSalary']}" if job["maxSalary"] is not None else "Not Specified"

    clean_job = {
        "Title": job["title"],
        "Company": job["companyName"],
        "Salary": f"{min_sal} - {max_sal}",
        "Location": ", ".join(job["locationRestrictions"]) if job["locationRestrictions"] else "Worldwide",
        "Category": ", ".join(job["categories"]),
        "Link": job["applicationLink"]
    }
    clean_jobs.append(clean_job)

# Write header row
headers = ["Title", "Company", "Salary", "Location", "Category", "Link"]
ws.append(headers)

# Write each job as a row
for job in clean_jobs:
    ws.append([
        job["Title"],
        job["Company"],
        job["Salary"],
        job["Location"],
        job["Category"],
        job["Link"]
    ])

wb.save("jobs.xlsx")
print("Saved!")

for job in clean_jobs:
    print(job["Link"])