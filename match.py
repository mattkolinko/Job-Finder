# match.py - Job Finder, step 2: score jobs against Matt's qualifications
import re
from jobs import search

KEYWORDS = {
    "ts/sci": 6, "top secret": 5, "clearance": 3, "pmp": 5,
    "program management": 4, "project management": 3, "technical program": 4,
    "systems engineering": 4, "test and evaluation": 4, "t&e": 3,
    "verification": 3, "validation": 3, "integration": 3, "requirements": 3,
    "stakeholder": 2, "risk management": 2, "agile": 2, "scrum": 2,
    "jira": 1, "doors": 2, "kpi": 2, "data analysis": 2, "aerospace": 3,
    "missile defense": 4, "space": 2, "radar": 3, "navy": 2, "space force": 3,
    "veteran": 2, "consulting": 2, "cross-functional": 2,
}
ALREADY_APPLIED = ["anduril", "apogee", "aria", "blue origin", "boeing", "coinbase",
    "deepmind", "deloitte", "firefly", "google", "lockheed", "microsoft", "northrop",
    "raytheon", "relativity", "rocket lab", "shield", "true anomaly", "trueanomaly",
    "vantor", "varda", "vast", "scale"]

# Titles that are too junior for 10+ years of experience
TOO_JUNIOR = ["intern", "junior", "entry level", "entry-level", "new grad", "apprentice",
              "associate engineer", "engineer i ", "technician"]
# Things Matt doesn't have - these lower the score
GAPS = {"phd": 25, "ph.d": 25, "doctorate": 25, "polygraph": 8}
MY_YEARS = 10

def years_required(text):
    nums = [int(n) for n in re.findall(r"(\d{1,2})\+?\s*(?:or more\s*)?years", text)]
    nums = [n for n in nums if 1 <= n <= 30]
    return min(nums) if nums else None

def score(job):
    title = job["title"].lower()
    text = (job["title"] + " " + job["text"]).lower()
    hits = [k for k in KEYWORDS if k in text]
    points = sum(KEYWORDS[k] for k in hits)
    if any(t in title for t in ["program manager", "systems engineer", "technical program",
                                "engagement manager", "project manager"]):
        points += 6
    if any(t in title for t in ["senior", "sr.", "lead", "principal", "staff", "manager"]):
        points += 4

    pct = min(100, points * 3)
    notes = []
    if any(t in f"{title} " for t in TOO_JUNIOR):
        pct = 0; notes.append("too junior")
    yrs = years_required(text)
    if yrs is not None:
        if yrs > MY_YEARS + 5:
            pct -= 30; notes.append(f"wants {yrs}+ yrs")
        elif yrs < 4:
            pct -= 15; notes.append(f"only {yrs} yrs")
    for gap, penalty in GAPS.items():
        if gap in text:
            pct -= penalty; notes.append(gap)

    job["score"] = max(0, pct)
    job["matched"] = hits
    job["notes"] = notes
    job["applied_before"] = any(c in job["company"].lower() for c in ALREADY_APPLIED)
    return job

def ranked():
    jobs = [score(j) for j in search()]
    return sorted(jobs, key=lambda j: j["score"], reverse=True)

if __name__ == "__main__":
    for j in ranked():
        print(f"{j['score']:>3}/100 {j['company']}: {j['title']}  {j['notes']}")
