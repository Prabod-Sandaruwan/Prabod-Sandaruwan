import json
import os
import pathlib
import urllib.request


def get_json(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def gql(query, headers, variables=None):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={**headers, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
        if "errors" in data:
            raise RuntimeError(data["errors"])
        return data["data"]


def svg_escape(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main():
    token = os.environ["GITHUB_TOKEN"]
    user = os.environ["GH_USER"]
    headers = {
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Accept": "application/vnd.github+json",
        "User-Agent": "codex-readme-cards",
    }

    u = get_json(f"https://api.github.com/users/{user}", headers)
    q = gql(
        """
        query($login:String!) {
          user(login:$login) {
            repositories {
              totalCount
            }
            followers {
              totalCount
            }
            contributionsCollection {
              totalCommitContributions
              totalPullRequestContributions
              totalIssueContributions
              totalPullRequestReviewContributions
              contributionCalendar {
                totalContributions
              }
            }
          }
        }
        """,
        headers,
        {"login": user},
    )["user"]

    profile = pathlib.Path("profile")
    profile.mkdir(exist_ok=True)
    display_name = svg_escape(u.get("name") or user)
    login = svg_escape(user)

    stats_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="165" viewBox="0 0 495 165" role="img" aria-labelledby="title desc">
  <title id="title">{display_name}'s GitHub stats</title>
  <desc id="desc">Live GitHub statistics generated from the GitHub API.</desc>
  <rect width="495" height="165" rx="12" fill="#0D1117"/>
  <text x="24" y="38" fill="#E6EDF3" font-family="Arial, sans-serif" font-size="22" font-weight="700">{display_name}'s GitHub stats</text>
  <text x="24" y="62" fill="#8B949E" font-family="Arial, sans-serif" font-size="12">{login}</text>
  <g fill="#00F5D4" font-family="Arial, sans-serif" font-size="14">
    <text x="24" y="100">Repos: {q['repositories']['totalCount']}</text>
    <text x="24" y="122">Commits: {q['contributionsCollection']['totalCommitContributions']}</text>
    <text x="24" y="144">PRs: {q['contributionsCollection']['totalPullRequestContributions']}</text>
  </g>
  <g fill="#E6EDF3" font-family="Arial, sans-serif" font-size="14">
    <text x="260" y="100">Issues: {q['contributionsCollection']['totalIssueContributions']}</text>
    <text x="260" y="122">Reviews: {q['contributionsCollection']['totalPullRequestReviewContributions']}</text>
    <text x="260" y="144">Followers: {q['followers']['totalCount']}</text>
  </g>
</svg>"""

    streak_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="165" viewBox="0 0 495 165" role="img" aria-labelledby="title desc">
  <title id="title">{display_name}'s contribution streak</title>
  <desc id="desc">Live GitHub contributions summary generated from the GitHub API.</desc>
  <rect width="495" height="165" rx="12" fill="#0D1117"/>
  <text x="24" y="38" fill="#E6EDF3" font-family="Arial, sans-serif" font-size="22" font-weight="700">{display_name}'s contribution streak</text>
  <text x="24" y="62" fill="#8B949E" font-family="Arial, sans-serif" font-size="12">{login}</text>
  <rect x="24" y="88" width="447" height="54" rx="10" fill="#161B22"/>
  <text x="40" y="112" fill="#00F5D4" font-family="Arial, sans-serif" font-size="15">Total contributions this year</text>
  <text x="40" y="134" fill="#E6EDF3" font-family="Arial, sans-serif" font-size="26" font-weight="700">{q['contributionsCollection']['contributionCalendar']['totalContributions']}</text>
</svg>"""

    (profile / "stats.svg").write_text(stats_svg, encoding="utf-8")
    (profile / "streak.svg").write_text(streak_svg, encoding="utf-8")


if __name__ == "__main__":
    main()
