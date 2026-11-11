# notify.py - Job Finder, step 3: post NEW matches as a GitHub issue (GitHub emails you)
import os, re, datetime, requests
from match import ranked

DAILY_MAX = 25      # jobs per day
PER_COMPANY = 2     # max jobs from any one company

REPO = os.environ["GITHUB_REPOSITORY"]
OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", REPO.split("/")[0])
API = f"https://api.github.com/repos/{REPO}/issues"
HEADERS = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
           "Accept": "application/vnd.github+json"}

def already_sent():
    """Memory: collect every job link from earlier daily notes."""
    seen = set()
    for page in (1, 2, 3):
        r = requests.get(API, headers=HEADERS, timeout=20,
                         params={"state": "all", "per_page": 100, "page": page})
        r.raise_for_status()
        issues = r.json()
        for i in issues:
            if i.get("title", "").startswith("Job matches"):
                seen.update(re.findall(r"\]\((https?://[^)\s]+)\)", i.get("body") or ""))
        if len(issues) < 100: break
    return seen

def build_body(jobs):
    if not jobs:
        return "No new matches today."
    lines = []
    for j in jobs:
        pay = f"${j['salary']:,}" if j["salary"] else "pay not listed"
        flag = " _(applied here before)_" if j["applied_before"] else ""
        lines.append(f"**{j['score']}/100** [{j['track']}] {j['company']}: "
                     f"[{j['title']}]({j['url']})  \n{j['location']} | {pay}{flag}\n")
    return "\n".join(lines)

def pick(jobs, seen):
    chosen, per_co = [], {}
    for j in jobs:
        if j["score"] < 30 or j["url"] in seen:
            continue
        c = j["company"].lower()
        if per_co.get(c, 0) >= PER_COMPANY:
            continue
        per_co[c] = per_co.get(c, 0) + 1
        chosen.append(j)
        if len(chosen) >= DAILY_MAX:
            break
    return chosen

if __name__ == "__main__":
    seen = already_sent()
    new = pick(ranked(), seen)
    print(f"Skipping {len(seen)} jobs already sent; {len(new)} new today.")
    today = datetime.date.today().strftime("%b %d, %Y")
    r = requests.post(API, headers=HEADERS, timeout=20,
        json={"title": f"Job matches for {today}", "body": build_body(new),
              "assignees": [OWNER]})
    r.raise_for_status()
    print("Posted:", r.json()["html_url"])
