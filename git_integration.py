
# filepath: git_integration.py
"""GitHub integration for document organization."""
import os
import sys
import subprocess
import json
from pathlib import Path
import datetime

def is_git_installed():
    """Check if Git is installed."""
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        return True
    except:
        return False

def setup_github_repo():
    """Interactive setup for GitHub repository."""
    if not is_git_installed():
        print("❌ Git is not installed. Please install Git first.")
        return False
    
    print("\n" + "="*60)
    print("GITHUB REPOSITORY SETUP")
    print("="*60)
    
    # Ask for user input
    username = input("GitHub username: ")
    repo_name = input("Repository name [document-organization-system]: ").strip() or "document-organization-system"
    token = input("GitHub Personal Access Token: ")
    is_private = input("Make repository private? (y/N): ").lower().startswith('y')
    
    if not username or not token:
        print("❌ Username and token are required.")
        return False
    
    # Create repo on GitHub using GitHub API
    try:
        import json
        auth = f"{username}:{token}"
        data = {
            "name": repo_name,
            "private": is_private,
            "description": "Document Organization System - Automated file management"
        }
        
        curl_cmd = [
            'curl', '-X', 'POST',
            '-u', auth,
            'https://api.github.com/user/repos',
            '-d', json.dumps(data),
            '-H', 'Accept: application/vnd.github.v3+json'
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        # Initialize Git repo and push
        subprocess.run(['git', 'init'], check=True)
        with open('.gitignore', 'w') as f:
            f.write("# Organization system gitignore\n*.log\nlogs/\n*.tmp\n")
        
        # Set up remote
        repo_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
        subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True)
        
        # Stage and commit files
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', "Initial setup of document organization system"], check=True)
        
        # Push to GitHub
        subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)
        
        print(f"\n✅ GitHub repository created and initial files pushed!")
        print(f"Repository URL: https://github.com/{username}/{repo_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up GitHub repository: {str(e)}")
        return False

if __name__ == "__main__":
    if not is_git_installed():
        print("Git is not installed. Please install Git to use GitHub integration.")
        sys.exit(1)
        
    setup_github_repo()
