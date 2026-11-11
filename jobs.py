# jobs.py - Job Finder, step 1: search and filter (company boards + Adzuna)
import os, re, requests

TITLES = ["program manager", "project manager", "engagement manager", "technical program",
          "systems engineer", "test engineer", "integration engineer", "requirements engineer",
          "aerospace engineer", "verification", "project engineer", "pmo", "manager", "consultant"]
LOCATIONS = ["colorado springs", "denver", "colorado", "remote"]
DEFENSE_WORDS = ["ts/sci", "top secret", "clearance", "dod", "department of war", "defense", "public sector"]
MIN_SALARY = 150_000

GREENHOUSE = ["anduril", "scaleai", "spacex", "trueanomaly", "relativity", "vast", "varda",
    "deepmind", "astranis", "axiomspace", "sierraspace", "planetlabs", "capellaspace",
    "umbra", "hawkeye360", "epirus", "castelion", "hadrian", "stokespace", "impulsespace",
    "firefly", "rocketlab", "skydio", "appliedintuition", "vannevarlabs", "rebelliondefense",
    "govini", "istari", "muonspace", "albedo", "turionspace", "redwire", "intuitivemachines",
    "anthropic", "openai", "databricks", "stripe", "coinbase", "cloudflare", "figma",
    "joby", "archer", "boomsupersonic", "hermeus", "ursamajor", "voyagerspace", "blacksky"]
LEVER = ["shieldai", "palantir", "saronic", "neros", "chaosindustries", "machindustries",
    "zoox", "primer", "firestormlabs"]

# Adzuna searches (each one uses 1 of your daily API calls - keep this list short)
ADZUNA_SEARCHES = [
    ("program manager", "Colorado"),
    ("systems engineer", "Colorado"),
    ("engagement manager consulting", "Colorado"),
    ("remote technical program manager", ""),
    ("aerospace engineer", "Colorado"),
]

def greenhouse(company):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
    r = requests.get(url, timeout=20); r.raise_for_status()
    for j in r.json().get("jobs", []):
        yield {"company": company, "title": j["title"], "location": j["location"]["name"],
               "url": j["absolute_url"], "text": j.get("content", "")}

def lever(company):
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    r = requests.get(url, timeout=20); r.raise_for_status()
    for j in r.json():
        yield {"company": company, "title": j["text"],
               "location": j.get("categories", {}).get("location", "") or "",
               "url": j["hostedUrl"], "text": j.get("descriptionPlain", "") or ""}

def adzuna(what, where):
    params = {"app_id": os.environ["ADZUNA_APP_ID"], "app_key": os.environ["ADZUNA_APP_KEY"],
              "what": what, "salary_min": MIN_SALARY, "results_per_page": 50}
    if where: params["where"] = where
    r = requests.get("https://api.adzuna.com/v1/api/jobs/us/search/1", params=params, timeout=20)
    r.raise_for_status()
    for j in r.json().get("results", []):
        text = j.get("description", "")
        loc = j.get("location", {}).get("display_name", "")
        if "remote" in (j.get("title", "") + text).lower(): loc += " remote"
        yield {"company": j.get("company", {}).get("display_name", "Unknown"),
               "title": j.get("title", ""), "location": loc,
               "url": j.get("redirect_url", ""), "text": text,
               "pay": int(j["salary_max"]) if j.get("salary_max") else None}

def top_salary(text):
    nums = [int(n.replace(",", "")) for n in re.findall(r"\$(\d{2,3},\d{3})", text)]
    return max(nums) if nums else None

def keep(job):
    title, loc = job["title"].lower(), job["location"].lower()
    if not any(t in title for t in TITLES): return False
    if not any(l in loc for l in LOCATIONS): return False
    pay = job.get("pay") or top_salary(job["text"])
    job["salary"] = pay
    job["track"] = "Defense" if any(w in job["text"].lower() for w in DEFENSE_WORDS) else "Tech/Other"
    return pay is None or pay >= MIN_SALARY

def search():
    results, found, skipped, seen = [], [], [], set()
    for source, names in ((greenhouse, GREENHOUSE), (lever, LEVER)):
        for c in names:
            try:
                jobs = list(source(c))
                found.append(f"{c} ({len(jobs)})")
                results += [j for j in jobs if keep(j)]
            except Exception:
                skipped.append(c)
    if os.environ.get("ADZUNA_APP_ID"):
        for what, where in ADZUNA_SEARCHES:
            try:
                jobs = list(adzuna(what, where))
                found.append(f"Adzuna '{what}' ({len(jobs)})")
                results += [j for j in jobs if keep(j)]
            except Exception as e:
                skipped.append(f"Adzuna '{what}': {e}")
    print("Checked:", ", ".join(found))
    print("Skipped:", ", ".join(skipped))
    unique = []
    for j in results:   # drop duplicates
        key = (j["company"].lower(), j["title"].lower())
        if key not in seen:
            seen.add(key); unique.append(j)
    return unique

if __name__ == "__main__":
    for j in search():
        pay = f"${j['salary']:,}" if j["salary"] else "pay not listed"
        print(f"[{j['track']}] {j['company']}: {j['title']} | {j['location']} | {pay}\n  {j['url']}")
