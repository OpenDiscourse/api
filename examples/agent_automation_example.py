#!/usr/bin/env python3
"""
Example script demonstrating programmatic interaction with GitHub Actions automation.

This script shows how to trigger various automation workflows using the GitHub API.

Requirements:
    pip install PyGithub python-dotenv

Usage:
    export GITHUB_TOKEN=your_token_here
    python examples/agent_automation_example.py
"""

import os
import sys
from typing import Optional
from github import Github
from github.Repository import Repository
from github.Issue import Issue


def get_repo(token: str, repo_name: str = "OpenDiscourse/api") -> Repository:
    """Get a GitHub repository object."""
    g = Github(token)
    return g.get_repo(repo_name)


def create_wiki_page_via_issue(repo: Repository, page_name: str, content: str) -> Issue:
    """
    Create a wiki page by creating an issue with the wiki-update label.
    
    Args:
        repo: GitHub repository object
        page_name: Name of the wiki page to create
        content: Markdown content for the page
    
    Returns:
        Created issue object
    """
    issue = repo.create_issue(
        title=f"Wiki Update: {page_name}",
        body=content,
        labels=["wiki-update", "documentation"]
    )
    print(f"✓ Created issue #{issue.number} to create wiki page '{page_name}'")
    return issue


def trigger_security_scan(repo: Repository) -> bool:
    """
    Trigger a security scan workflow.
    
    Args:
        repo: GitHub repository object
    
    Returns:
        True if workflow was triggered successfully
    """
    # Get the workflow
    workflow = repo.get_workflow("vulnerability-automation.yml")
    
    # Trigger with scan action
    success = workflow.create_dispatch(
        ref="main",
        inputs={"action": "scan"}
    )
    
    print(f"✓ Security scan workflow triggered")
    return success


def create_issue_with_auto_labels(repo: Repository, title: str, body: str) -> Issue:
    """
    Create an issue that will be automatically labeled based on keywords.
    
    Args:
        repo: GitHub repository object
        title: Issue title
        body: Issue body
    
    Returns:
        Created issue object
    """
    issue = repo.create_issue(
        title=title,
        body=body
    )
    print(f"✓ Created issue #{issue.number}: {title}")
    print(f"  Issue will be auto-labeled based on keywords")
    return issue


def use_agent_command(repo: Repository, issue_number: int, command: str) -> None:
    """
    Post an agent command as a comment on an issue.
    
    Args:
        repo: GitHub repository object
        issue_number: Issue number to comment on
        command: Agent command to execute
    """
    issue = repo.get_issue(issue_number)
    comment = issue.create_comment(command)
    print(f"✓ Posted agent command to issue #{issue_number}")
    print(f"  Command: {command}")


def main():
    """Main function demonstrating various automation examples."""
    
    # Get token from environment
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        print("Set it with: export GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    
    # Get repository
    try:
        repo = get_repo(token)
        print(f"Connected to repository: {repo.full_name}\n")
    except Exception as e:
        print(f"Error connecting to repository: {e}")
        sys.exit(1)
    
    # Example 1: Create a wiki page via issue
    print("Example 1: Create Wiki Page")
    print("-" * 50)
    wiki_issue = create_wiki_page_via_issue(
        repo,
        page_name="Example-Documentation",
        content="# Example Documentation\n\nThis is an example wiki page created programmatically."
    )
    print()
    
    # Example 2: Create an issue with auto-labeling
    print("Example 2: Create Issue with Auto-labeling")
    print("-" * 50)
    bug_issue = create_issue_with_auto_labels(
        repo,
        title="Bug: Example issue for testing",
        body="This is an urgent bug that needs to be fixed. It affects the API component."
    )
    print()
    
    # Example 3: Use agent command
    print("Example 3: Use Agent Command")
    print("-" * 50)
    print(f"Using issue #{bug_issue.number} for command demo")
    use_agent_command(
        repo,
        bug_issue.number,
        "/agent issue-label labels=priority:high,needs-review"
    )
    print()
    
    # Example 4: Trigger security scan
    print("Example 4: Trigger Security Scan")
    print("-" * 50)
    try:
        trigger_security_scan(repo)
    except Exception as e:
        print(f"Note: Security scan trigger requires workflow_dispatch permission")
        print(f"Error: {e}")
    print()
    
    print("=" * 50)
    print("All examples completed!")
    print("Check the repository for created issues and triggered workflows.")
    print("\nUseful commands:")
    print(f"  View issues: gh issue list --repo {repo.full_name}")
    print(f"  View wiki issue: gh issue view {wiki_issue.number} --repo {repo.full_name}")
    print(f"  View workflows: gh run list --repo {repo.full_name}")


if __name__ == "__main__":
    main()
