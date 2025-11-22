# Scripts Directory

This directory contains automation scripts for the repository.

## update_repo_info.py

Automatically extracts and updates repository information from GitHub.

### What it does:
- Fetches all public repositories for the user
- Extracts README content from each repository
- Updates `docs/REPOSITORIES.md` with complete repository details
- Updates the main `README.md` with featured repositories
- Generates statistics (total repos, stars, languages, etc.)

### Requirements:
- Python 3.x
- requests library (install via `pip install -r requirements.txt`)

### Environment Variables:
- `GITHUB_TOKEN` (optional but recommended): GitHub personal access token for higher API rate limits
- `GITHUB_USERNAME` (optional): GitHub username, defaults to 'VIRUSGAMING64'

### Usage:

Manual run:
```bash
export GITHUB_TOKEN="your_token_here"
python scripts/update_repo_info.py
```

The script is also integrated into the GitHub Actions workflow and runs automatically:
- Daily at midnight UTC
- On manual workflow dispatch
- On pushes to main/master branch

### Output Files:
- `docs/REPOSITORIES.md`: Detailed list of all repositories
- `README.md`: Updated featured repositories section
