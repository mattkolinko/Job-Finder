# notify.py - Job Finder, step 3: post today's matches as a GitHub issue (GitHub emails you)
import os, datetime, requests
from match import ranked

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
    top = [j for j in ranked() if j["score"] >= 30][:15]
    today = datetime.date.today().strftime("%b %d, %Y")
    r = requests.post(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues",
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
                 "Accept": "application/vnd.github+json"},
        json={"title": f"Job matches for {today}", "body": build_body(top)},
        timeout=20)
    r.raise_for_status()
    print("Posted:", r.json()["html_url"])
