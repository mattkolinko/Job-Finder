# jobs.py - Job Finder, step 1: search and filter (expanded company list)
import re, requests

TITLES = ["program manager", "project manager", "engagement manager", "technical program",
          "systems engineer", "test engineer", "integration engineer", "requirements engineer",
          "aerospace engineer", "verification", "project engineer", "pmo", "manager"]
LOCATIONS = ["colorado springs", "denver", "colorado", "remote", "united states", "us"]
DEFENSE_WORDS = ["ts/sci", "top secret", "clearance", "dod", "department of war", "defense", "public sector"]
MIN_SALARY = 150_000

# Defense, space and AI companies on Greenhouse (bad names are skipped automatically)
GREENHOUSE = ["anduril", "scaleai", "spacex", "trueanomaly", "relativity", "vast", "varda",
    "deepmind", "astranis", "axiomspace", "sierraspace", "planetlabs", "capellaspace",
    "umbra", "hawkeye360", "epirus", "castelion", "hadrian", "stokespace", "impulsespace",
    "firefly", "rocketlab", "skydio", "appliedintuition", "vannevarlabs", "rebelliondefense",
    "govini", "istari", "muonspace", "albedo", "turionspace", "redwire", "intuitivemachines",
    "anthropic", "openai", "databricks", "stripe", "coinbase", "cloudflare", "figma",
    "joby", "archer", "boomsupersonic", "hermeus", "ursamajor", "voyagerspace", "blacksky"]
# Companies on Lever
LEVER = ["shieldai", "palantir", "saronic", "neros", "chaosindustries", "machindustries",
    "zoox", "primer", "firestormlabs"]

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
    return pay is None or pay >= MIN_SALARY

def search():
    results, found, skipped = [], [], []
    for source, names in ((greenhouse, GREENHOUSE), (lever, LEVER)):
        for c in names:
            try:
                jobs = list(source(c))
                found.append(f"{c} ({len(jobs)} jobs)")
                results += [j for j in jobs if keep(j)]
            except Exception:
                skipped.append(c)
    print("Checked:", ", ".join(found))
    print("Skipped (board not found):", ", ".join(skipped))
    return results

if __name__ == "__main__":
    for j in search():
        pay = f"${j['salary']:,}" if j["salary"] else "pay not listed"
        print(f"[{j['track']}] {j['company']}: {j['title']} | {j['location']} | {pay}\n  {j['url']}")
