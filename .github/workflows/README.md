# GitHub Actions Agent Automation

This directory contains automated workflows that enable agents to manage various aspects of the repository, including wiki pages, GitHub Projects, issues, and security vulnerabilities.

## Available Workflows

### 1. Wiki Automation (`wiki-automation.yml`)

Automates the creation, updating, and archiving of wiki pages.

**Triggers:**
- Manual dispatch via workflow_dispatch
- Issue labeling with `wiki-update` label

**Usage:**

```bash
# Via workflow dispatch
gh workflow run wiki-automation.yml \
  -f action=create \
  -f page_name="API-Documentation" \
  -f content="# API Documentation\n\nContent here..."

# Via issue label
# Create an issue with title "Wiki Update: Page-Name"
# Add the label "wiki-update"
```

**Actions:**
- `create`: Create a new wiki page
- `update`: Update an existing wiki page
- `archive`: Archive a wiki page (moves to Archived-PageName.md)

### 2. Project Automation (`project-automation.yml`)

Manages GitHub Projects V2 items, including adding issues and PRs to projects.

**Triggers:**
- Manual dispatch
- New issues opened
- New PRs opened
- Issues/PRs labeled

**Usage:**

```bash
# Via workflow dispatch
gh workflow run project-automation.yml \
  -f action=add_issue_to_project \
  -f project_number=1 \
  -f issue_number=123

# Automatic: Issues and PRs are automatically added to project #1
```

**Features:**
- Auto-adds issues and PRs to projects
- Auto-labels based on content
- Updates project item status
- Comments on successful addition

### 3. Issue Management (`issue-automation.yml`)

Comprehensive issue management including creation, labeling, commenting, and closing.

**Triggers:**
- Manual dispatch
- Issue events (opened, labeled, closed)
- Issue comments
- Schedule (daily for stale issue checks)

**Usage:**

```bash
# Create issue
gh workflow run issue-automation.yml \
  -f action=create \
  -f title="Bug: Something broke" \
  -f body="Description here" \
  -f labels="bug,priority:high"

# Comment on issue
gh workflow run issue-automation.yml \
  -f action=comment \
  -f issue_number=123 \
  -f body="Thank you for reporting this!"

# Close issue
gh workflow run issue-automation.yml \
  -f action=close \
  -f issue_number=123 \
  -f body="Closing as resolved"
```

**Auto-labeling:**
Issues are automatically labeled based on keywords:
- `bug`: title/body contains "bug"
- `enhancement`: title contains "feature" or "enhancement"
- `documentation`: title/body contains "doc" or "documentation"
- `security`: title/body contains "security" or "vulnerability"
- `priority:high`: body contains "urgent" or "critical"

**Comment Commands:**
- `/help`: Show available commands
- `/close`: Close the issue (requires write access)
- `/assign @username`: Assign to user
- `/label label-name`: Add label
- `/priority high|medium|low`: Set priority

**Stale Issue Management:**
- Issues inactive for 60 days are marked as stale
- Stale issues are closed after 7 more days of inactivity
- Issues with labels `pinned`, `security`, or `priority:high` are exempt

### 4. Vulnerability Automation (`vulnerability-automation.yml`)

Scans for security vulnerabilities and can automatically create PRs to fix them.

**Triggers:**
- Manual dispatch
- Schedule (weekly)
- Push to main
- Pull requests

**Usage:**

```bash
# Scan for vulnerabilities
gh workflow run vulnerability-automation.yml \
  -f action=scan

# Create auto-fix PR
gh workflow run vulnerability-automation.yml \
  -f action=create_fix_pr

# Review Dependabot alerts
gh workflow run vulnerability-automation.yml \
  -f action=review_alerts
```

**Features:**
- Scans Python dependencies with `safety` and `pip-audit`
- Creates issues for detected vulnerabilities
- Can automatically create PRs to fix vulnerabilities
- Reviews and summarizes Dependabot alerts

### 5. Dependabot Configuration (`dependabot.yml`)

Configures automatic dependency updates via Dependabot.

**Features:**
- Weekly updates for Python dependencies
- Weekly updates for GitHub Actions
- Auto-groups minor and patch updates
- Prioritizes security updates
- Limits open PRs to prevent spam

### 6. Dependabot Auto-merge (`dependabot-auto-merge.yml`)

Automatically approves and merges safe Dependabot PRs.

**Triggers:**
- Pull request events from Dependabot

**Auto-merge conditions:**
- Security updates: Always auto-approved and merged
- Minor/patch updates: Auto-approved and merged
- Major updates: Flagged for manual review

**Features:**
- Auto-approves security updates
- Auto-approves minor/patch updates
- Flags major updates for manual review
- Adds appropriate labels and comments

### 7. Agent Command Dispatcher (`agent-dispatcher.yml`)

Central dispatcher for agent commands via issue comments or workflow dispatch.

**Triggers:**
- Issue comments starting with `/agent`
- Manual dispatch

**Usage in Issues:**

```
/agent wiki-create page_name="NewPage" content="Page content"
/agent wiki-update page_name="ExistingPage" content="Updated content"
/agent project-add project_number=1
/agent issue-label labels="bug,priority:high"
/agent security-scan
```

**Usage via Workflow Dispatch:**

```bash
gh workflow run agent-dispatcher.yml \
  -f command=wiki-create \
  -f parameters='{"page_name":"NewPage","content":"Content here"}'
```

**Supported Commands:**
- `wiki-create`: Create wiki page
- `wiki-update`: Update wiki page
- `project-add`: Add to project
- `issue-create`: Create issue
- `issue-label`: Label issue
- `security-scan`: Run security scan

## Setup Requirements

### 1. Repository Settings

Ensure the following repository settings are configured:

- **Actions > General > Workflow permissions:**
  - ✅ Read and write permissions
  - ✅ Allow GitHub Actions to create and approve pull requests

### 2. Required Secrets

No additional secrets are required beyond the default `GITHUB_TOKEN`.

### 3. Wiki Initialization

To use wiki automation, the repository wiki must be initialized:

1. Go to the repository's Wiki tab
2. Create the first page (e.g., "Home")
3. The wiki will now be available for automation

### 4. Project Setup

For project automation:

1. Create a GitHub Project (Projects V2)
2. Note the project number from the URL
3. Use this number in workflow inputs

## Best Practices

### For Agents

1. **Use descriptive titles and labels** for automatic categorization
2. **Include relevant keywords** to trigger auto-labeling
3. **Comment with `/help`** to see available commands
4. **Use workflow dispatch** for programmatic execution

### For Maintainers

1. **Review major updates** flagged by Dependabot
2. **Monitor security scan results** via generated issues
3. **Configure project numbers** in workflow files if needed
4. **Adjust stale issue timing** in `issue-automation.yml` as needed

### Security Considerations

1. **Review auto-generated PRs** before merging
2. **Don't disable security scanning** workflows
3. **Keep Dependabot enabled** for automatic updates
4. **Monitor security issues** created by automation

## Troubleshooting

### Wiki Automation Fails

**Error:** "Could not checkout wiki"
- **Solution:** Initialize the wiki by creating at least one page manually

### Project Automation Fails

**Error:** "Project not found"
- **Solution:** Verify the project number and ensure it's a V2 project

### Dependabot PRs Not Auto-merging

**Error:** PRs remain open despite approval
- **Solution:** Ensure "Allow auto-merge" is enabled in repository settings

### Permission Errors

**Error:** "Resource not accessible by integration"
- **Solution:** Check workflow permissions in repository settings

## Examples

### Example 1: Create Documentation via Agent

```
/agent wiki-create page_name="API-v2-Guide" content="# API v2 Guide\n\nNew features in v2..."
```

### Example 2: Bulk Label Issues

Create a workflow file that runs the issue automation:

```bash
for issue in 123 124 125; do
  gh workflow run issue-automation.yml \
    -f action=label \
    -f issue_number=$issue \
    -f labels="needs-review"
done
```

### Example 3: Monthly Security Scan

The security scan runs weekly by default, but you can run it manually:

```bash
gh workflow run vulnerability-automation.yml -f action=scan
```

## Contributing

To add new automation workflows:

1. Create workflow file in `.github/workflows/`
2. Add appropriate permissions
3. Document usage in this README
4. Test with manual dispatch first
5. Add to agent dispatcher if needed

## Support

For issues with workflows:
1. Check workflow logs in Actions tab
2. Verify permissions are correct
3. Ensure repository settings allow required operations
4. Create an issue with the `workflow` label
