# ghstars

A CLI tool to collect and render as a staic website most notable stargazers for your GitHub projects.

Demo: [stars.orsinium.dev](https://stars.orsinium.dev/)

## Usage

1. Install: `python3 -m pip install ghstars`
1. [Generate GitHub API token](https://github.com/settings/tokens)
1. Fetch data: `ghstars fetch --token YOUR_TOKEN --orgs YOUR_ORG`
1. Generate HTML: `ghstars render`
