# jobs.py - Job Finder, step 1: search and filter
import re, requests

TITLES = ["program manager", "project manager", "engagement manager", "technical program",
          "systems engineer", "test engineer", "integration engineer", "requirements engineer",
          "aerospace engineer", "verification", "project engineer", "pmo", "manager"]
LOCATIONS = ["colorado springs", "denver", "remote"]
DEFENSE_WORDS = ["ts/sci", "top secret", "clearance", "dod", "department of war", "defense"]
MIN_SALARY = 150_000

# Company job boards (edit freely). Greenhouse and Lever have free public APIs.
GREENHOUSE = ["anduril", "scaleai", "trueanomaly", "relativity", "vast", "varda", "deepmind"]
LEVER = ["shieldai"]

def greenhouse(company):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
    for j in requests.get(url, timeout=20).json().get("jobs", []):
        yield {"company": company, "title": j["title"], "location": j["location"]["name"],
               "url": j["absolute_url"], "text": j.get("content", "")}

def lever(company):
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    for j in requests.get(url, timeout=20).json():
        yield {"company": company, "title": j["text"],
               "location": j.get("categories", {}).get("location", ""),
               "url": j["hostedUrl"], "text": j.get("descriptionPlain", "")}

def top_salary(text):
    nums = [int(n.replace(",", "")) for n in re.findall(r"\$(\d{2,3},\d{3})", text)]
    return max(nums) if nums else None

def keep(job):
    title, loc = job["title"].lower(), job["location"].lower()
    if not any(t in title for t in TITLES): return False
    if not any(l in loc for l in LOCATIONS): return False
    pay = top_salary(job["text"])
    job["salary"] = pay
    job["track"] = "Defense" if any(w in job["text"].lower() for w in DEFENSE_WORDS) else "Tech/Other"
    return pay is None or pay >= MIN_SALARY   # keep unlisted pay, flag it

def search():
    results = []
    for c in GREENHOUSE:
        try: results += [j for j in greenhouse(c) if keep(j)]
        except Exception as e: print("skip", c, e)
    for c in LEVER:
        try: results += [j for j in lever(c) if keep(j)]
        except Exception as e: print("skip", c, e)
    return results

if __name__ == "__main__":
    for j in search():
        pay = f"${j['salary']:,}" if j["salary"] else "pay not listed"
        print(f"[{j['track']}] {j['company']}: {j['title']} | {j['location']} | {pay}\n  {j['url']}")
