#!/usr/bin/env python3
"""
Script to automatically extract and update repository information from GitHub.
This script fetches README content and metadata from all repositories.
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

# GitHub API configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', 'VIRUSGAMING64')
API_BASE = 'https://api.github.com'

def get_headers() -> Dict[str, str]:
    """Get headers for GitHub API requests."""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    return headers

def get_user_repos() -> List[Dict]:
    """Fetch all repositories for the user."""
    repos = []
    page = 1
    
    print(f"Fetching repos for user: {GITHUB_USERNAME}")
    
    while True:
        url = f'{API_BASE}/users/{GITHUB_USERNAME}/repos'
        params = {
            'per_page': 100,
            'page': page,
            'sort': 'updated',
            'direction': 'desc'
        }
        
        try:
            response = requests.get(url, headers=get_headers(), params=params, timeout=30)
        except (requests.RequestException, requests.ConnectionError) as e:
            print(f"Error making request: {e}")
            break
        
        if response.status_code != 200:
            print(f"Error fetching repos: {response.status_code}")
            print(response.text)
            # Try without authentication if we got auth error
            if response.status_code == 403 or response.status_code == 401:
                print("Trying without authentication...")
                response = requests.get(url, params=params, timeout=30)
                if response.status_code != 200:
                    break
            else:
                break
            
        data = response.json()
        if not data:
            break
            
        repos.extend(data)
        page += 1
        
        # Limit to avoid rate limiting during testing
        if page > 10:
            break
        
    return repos

def get_repo_readme(owner: str, repo: str) -> Optional[str]:
    """Fetch README content for a repository."""
    url = f'{API_BASE}/repos/{owner}/{repo}/readme'
    
    response = requests.get(url, headers=get_headers())
    
    if response.status_code == 200:
        data = response.json()
        # README is base64 encoded
        import base64
        content = base64.b64decode(data['content']).decode('utf-8')
        return content
    
    return None

def extract_description_from_readme(readme_content: Optional[str]) -> str:
    """Extract a meaningful description from README content."""
    if not readme_content:
        return "No description available"
    
    lines = readme_content.split('\n')
    description_lines = []
    
    # Skip headers and find first paragraph
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line and not line.startswith('[') and not line.startswith('!'):
            description_lines.append(line)
            if len(description_lines) >= 2:
                break
    
    return ' '.join(description_lines) if description_lines else "No description available"

def get_repo_emoji(name: str) -> str:
    """Get appropriate emoji icon for repository based on name."""
    name_lower = name.lower()
    
    if 'shell' in name_lower:
        return '🐚'
    elif 'bot' in name_lower or 'telegram' in name_lower:
        return '📱'
    elif 'event' in name_lower:
        return '⚡'
    elif 'zip' in name_lower or '7z' in name_lower:
        return '📦'
    elif 'web' in name_lower or '.io' in name:
        return '🌐'
    elif 'stat' in name_lower or 'monitor' in name_lower:
        return '📊'
    elif 'final' in name_lower or 'c-' in name_lower:
        return '🎓'
    else:
        return '🔧'

def format_date(date_str: str) -> str:
    """Format ISO date to readable format."""
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date.strftime('%B %d, %Y')
    except (ValueError, TypeError) as e:
        return date_str

def generate_repositories_md(repos: List[Dict]) -> str:
    """Generate the REPOSITORIES.md content."""
    output = ["# 📚 Complete Repository List\n"]
    output.append("This document provides detailed information about all repositories in the VIRUSGAMING64 organization.\n")
    output.append("---\n")
    output.append("\n## 🌟 Active Projects\n")
    
    # Filter out forks if needed
    repos = [r for r in repos if not r.get('fork', False)]
    
    # Sort by stars and then by update date
    repos_sorted = sorted(repos, key=lambda x: (x.get('stargazers_count', 0), x.get('updated_at', '')), reverse=True)
    
    for idx, repo in enumerate(repos_sorted, 1):
        name = repo['name']
        html_url = repo['html_url']
        stars = repo.get('stargazers_count', 0)
        language = repo.get('language', 'Not specified')
        created = format_date(repo['created_at'])
        updated = format_date(repo['updated_at'])
        description = repo.get('description', '')
        
        # Fetch README for more details
        readme = get_repo_readme(GITHUB_USERNAME, name)
        if not description and readme:
            description = extract_description_from_readme(readme)
        
        output.append(f"\n### {idx}. {name}\n")
        output.append(f"**Repository:** [{GITHUB_USERNAME}/{name}]({html_url})\n")
        if language != 'Not specified':
            output.append(f"- **Language:** {language}\n")
        if stars > 0:
            output.append(f"- **Stars:** ⭐ {stars}\n")
        output.append(f"- **Status:** Active\n")
        output.append(f"- **Created:** {created}\n")
        output.append(f"- **Last Updated:** {updated}\n")
        if description:
            output.append(f"- **Description:** {description}\n")
        
        output.append("\n---\n")
    
    # Add statistics
    total_repos = len(repos_sorted)
    total_stars = sum(r.get('stargazers_count', 0) for r in repos_sorted)
    languages = set(r.get('language') for r in repos_sorted if r.get('language'))
    most_starred = max(repos_sorted, key=lambda x: x.get('stargazers_count', 0)) if repos_sorted else None
    
    output.append("\n## 📊 Statistics Summary\n")
    output.append(f"\n- **Total Repositories:** {total_repos}\n")
    output.append(f"- **Total Stars:** {total_stars}\n")
    output.append(f"- **Primary Languages:** {', '.join(sorted(languages))}\n")
    if most_starred:
        output.append(f"- **Most Starred:** {most_starred['name']} ({most_starred.get('stargazers_count', 0)} stars)\n")
    
    output.append("\n---\n")
    output.append(f"\n*Last updated: {datetime.now().strftime('%B %d, %Y')}*\n")
    
    return ''.join(output)

def update_main_readme(repos: List[Dict]):
    """Update the main README.md with repository information."""
    readme_path = 'README.md'
    
    if not os.path.exists(readme_path):
        print(f"README.md not found at {readme_path}")
        return
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the featured repositories section
    start_marker = "## 🚀 My Projects"
    end_marker = "---\n\n## 📫 Connect With Me"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("Could not find repository section markers in README.md")
        return
    
    # Generate new repositories section
    repos_section = ["\n## 🚀 My Projects\n"]
    repos_section.append("\n### Featured Repositories\n")
    
    # Sort by stars
    repos_sorted = sorted(repos, key=lambda x: x.get('stargazers_count', 0), reverse=True)[:10]
    
    for repo in repos_sorted:
        name = repo['name']
        html_url = repo['html_url']
        stars = repo.get('stargazers_count', 0)
        language = repo.get('language', '')
        description = repo.get('description', '')
        
        stars_str = f" ⭐ {stars}" if stars > 0 else ""
        
        repos_section.append(f"\n#### {get_repo_emoji(name)} [{name}]({html_url}){stars_str}\n")
        if language:
            repos_section.append(f"**{language}** | ")
        repos_section.append(f"{description or 'No description available'}\n")
    
    # Replace the section
    new_content = content[:start_idx] + ''.join(repos_section) + "\n" + content[end_idx:]
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("README.md updated successfully")

def main():
    """Main function."""
    print("Fetching repositories...")
    repos = get_user_repos()
    
    if not repos:
        print("No repositories found")
        sys.exit(1)
    
    print(f"Found {len(repos)} repositories")
    
    # Generate REPOSITORIES.md
    print("Generating REPOSITORIES.md...")
    repo_md_content = generate_repositories_md(repos)
    
    os.makedirs('docs', exist_ok=True)
    with open('docs/REPOSITORIES.md', 'w', encoding='utf-8') as f:
        f.write(repo_md_content)
    
    print("REPOSITORIES.md updated successfully")
    
    # Update main README.md
    print("Updating README.md...")
    update_main_readme(repos)
    
    print("All updates complete!")

if __name__ == '__main__':
    main()
