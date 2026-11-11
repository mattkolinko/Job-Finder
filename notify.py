# notify.py - Job Finder, step 3: post NEW matches as a GitHub issue (GitHub emails you)
import os, re, datetime, requests
from match import ranked

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

if __name__ == "__main__":
    seen = already_sent()
    new = [j for j in ranked() if j["score"] >= 30 and j["url"] not in seen][:15]
    print(f"Skipping {len(seen)} jobs already sent; {len(new)} new today.")
    today = datetime.date.today().strftime("%b %d, %Y")
    r = requests.post(API, headers=HEADERS, timeout=20,
        json={"title": f"Job matches for {today}", "body": build_body(new),
              "assignees": [OWNER]})   # assigning you makes GitHub send the email
    r.raise_for_status()
    print("Posted:", r.json()["html_url"])
