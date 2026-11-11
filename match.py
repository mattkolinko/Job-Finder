# match.py - Job Finder, step 2: score jobs against Matt's resume
from jobs import search

# Skills and keywords from Matt's resume and career inventory, with weights
KEYWORDS = {
    "ts/sci": 5, "top secret": 4, "clearance": 3, "pmp": 4,
    "program management": 4, "project management": 3, "technical program": 4,
    "systems engineering": 4, "test and evaluation": 4, "t&e": 3,
    "verification": 3, "validation": 3, "integration": 3, "requirements": 3,
    "stakeholder": 2, "risk management": 2, "agile": 2, "scrum": 2,
    "jira": 1, "doors": 2, "kpi": 2, "data analysis": 2, "aerospace": 3,
    "missile defense": 4, "space": 2, "radar": 3, "navy": 2, "air force": 1,
    "space force": 3, "consulting": 2, "cross-functional": 2,
}
ALREADY_APPLIED = ["anduril", "apogee", "aria", "blue origin", "boeing", "coinbase",
    "deepmind", "deloitte", "firefly", "google", "lockheed", "microsoft", "northrop",
    "raytheon", "relativity", "rocket lab", "shield", "true anomaly", "trueanomaly",
    "vantor", "varda", "vast", "scale"]

def score(job):
    text = (job["title"] + " " + job["text"]).lower()
    hits = [k for k in KEYWORDS if k in text]
    points = sum(KEYWORDS[k] for k in hits)
    if any(t in job["title"].lower() for t in ["program manager", "systems engineer", "technical program"]):
        points += 5   # bonus for a core title match
    job["score"] = min(100, points * 3)
    job["matched"] = hits
    job["applied_before"] = any(c in job["company"].lower() for c in ALREADY_APPLIED)
    return job

def ranked():
    jobs = [score(j) for j in search()]
    return sorted(jobs, key=lambda j: j["score"], reverse=True)

if __name__ == "__main__":
    for j in ranked():
        flag = " (applied to this company before)" if j["applied_before"] else ""
        print(f"{j['score']:>3}/100 [{j['track']}] {j['company']}: {j['title']}{flag}")
        print(f"   matched: {', '.join(j['matched'][:8])}\n   {j['url']}")
