import json
import subprocess

USER = "ellie-scott"
ORG = "umn-ras"
SINCE = "2026-01-01T00:00:00Z"
UNTIL = "2026-12-31T23:59:59Z"


def run(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True, text=True)


repos = json.loads(run(f"gh repo list {ORG} --limit 200 --json nameWithOwner,primaryLanguage,updatedAt,url"))
rows = []
for repo in repos:
    owner_repo = repo["nameWithOwner"]
    lang = (repo.get("primaryLanguage") or {}).get("name") or "None"
    updated = repo["updatedAt"]
    url = repo["url"]
    path = (
        f"/repos/{owner_repo}/commits?author={USER}"
        f"&since={SINCE}&until={UNTIL}&per_page=100"
    )
    try:
        out = run(f"gh api --paginate '{path}' | jq -s 'map(length) | add'")
        commits = int((out or "0").strip())
    except Exception:
        commits = 0
    rows.append((commits, updated, owner_repo, lang, url))

rows.sort(key=lambda x: (x[0], x[1]), reverse=True)

print("repo\tcommits_2026\tprimary_language\tupdated_at\turl")
for commits, updated, owner_repo, lang, url in rows:
    if commits > 0:
        print(f"{owner_repo}\t{commits}\t{lang}\t{updated}\t{url}")
print("---")
print(f"total_repos\t{len(rows)}")
print(f"repos_with_authored_commits\t{sum(1 for x in rows if x[0] > 0)}")
print(f"total_authored_commits_2026\t{sum(x[0] for x in rows)}")

