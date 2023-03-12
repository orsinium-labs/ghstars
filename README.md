# ghstars

A CLI tool to collect and render as a staic website most notable stargazers for your GitHub projects.

Demo: [stars.orsinium.dev](https://stars.orsinium.dev/)

## Usage

1. Install: `python3 -m pip install ghstars`
1. [Generate GitHub API token](https://github.com/settings/tokens)
1. Fetch data: `ghstars fetch --token YOUR_TOKEN`. Requires one (or several) of the following flags:
    1. `--orgs life4`: space-separated list of organizations.
    1. `--repos life4/textdistance`: space-separated list of repositories.
1. Generate HTML: `ghstars render`

## Other commands

There are a few more commands to analyze the fetched data:

1. `ghstars top-authors`: show most popular projects authored by your stargazers.
1. `ghstars top-followed`: show stargazers with the most followers.
