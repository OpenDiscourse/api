# Agent Automation Guide

This repository includes comprehensive automation for agents to manage repository operations including wiki pages, GitHub Projects, issues, and security vulnerabilities.

## Quick Start for Agents

### Available Agent Commands

You can control repository operations by commenting on issues with `/agent` commands:

```
/agent wiki-create page_name="PageName" content="Page content here"
/agent wiki-update page_name="ExistingPage" content="Updated content"
/agent project-add project_number=1
/agent issue-label labels="bug,priority:high"
/agent security-scan
```

### Automated Actions

The following actions happen automatically:

1. **New Issues** → Auto-labeled based on keywords, added to project, welcomed
2. **New PRs** → Auto-added to project, linked to issues
3. **Dependabot PRs** → Auto-approved and merged if safe
4. **Security Vulnerabilities** → Auto-scanned weekly, issues created, PRs generated
5. **Stale Issues** → Marked after 60 days, closed after 7 more days
6. **Wiki Updates** → Created/updated via labeled issues

## Detailed Usage

### 1. Managing Wiki Pages

**Via Issue Comment:**
```
/agent wiki-create page_name="API-Guide" content="# API Guide\n\nContent..."
```

**Via Issue Template:**
1. Create a new issue using the "Wiki Update Request" template
2. Fill in the page name and content
3. Add the `wiki-update` label
4. The workflow will automatically process it

**Via Workflow Dispatch:**
```bash
gh workflow run wiki-automation.yml \
  -f action=create \
  -f page_name="NewPage" \
  -f content="# Title\n\nContent"
```

### 2. Managing Issues

**Auto-labeling:**
Just include keywords in your issue:
- "bug" → adds `bug` label
- "feature" or "enhancement" → adds `enhancement` label
- "urgent" or "critical" → adds `priority:high` label
- "security" or "vulnerability" → adds `security` label

**Slash Commands (in comments):**
- `/help` - Show available commands
- `/close` - Close the issue
- `/assign @username` - Assign to user
- `/label label-name` - Add a label
- `/priority high|medium|low` - Set priority

**Programmatic Creation:**
```bash
gh workflow run issue-automation.yml \
  -f action=create \
  -f title="New Issue" \
  -f body="Description" \
  -f labels="bug,priority:high"
```

### 3. Managing Projects

**Automatic:**
- Issues and PRs are automatically added to project #1 when created
- Auto-labeled based on content

**Manual:**
```bash
gh workflow run project-automation.yml \
  -f action=add_issue_to_project \
  -f project_number=1 \
  -f issue_number=123
```

### 4. Security Management

**Automatic Scanning:**
- Runs weekly on Sundays
- Runs on every push to main
- Creates issues for vulnerabilities

**Manual Scan:**
```bash
gh workflow run vulnerability-automation.yml -f action=scan
```

**Auto-fix Vulnerabilities:**
```bash
gh workflow run vulnerability-automation.yml -f action=create_fix_pr
```

**Review Alerts:**
```bash
gh workflow run vulnerability-automation.yml -f action=review_alerts
```

### 5. Dependabot

**Automatic:**
- Weekly checks for dependency updates
- Security updates are prioritized
- Minor/patch updates auto-merge after tests pass
- Major updates require manual review

**Configuration:**
- Python dependencies: Checked weekly
- GitHub Actions: Checked weekly
- Grouped updates for easier review

## For Repository Maintainers

### Initial Setup

1. **Enable Wiki:**
   ```bash
   # Go to repository Settings → Features → Enable Wiki
   # Create the first page manually to initialize
   ```

2. **Create Project:**
   ```bash
   # Go to Projects → New Project
   # Note the project number from URL
   ```

3. **Configure Permissions:**
   ```bash
   # Settings → Actions → General → Workflow permissions
   # Select "Read and write permissions"
   # Check "Allow GitHub Actions to create and approve pull requests"
   ```

4. **Enable Dependabot:**
   ```bash
   # Settings → Security → Code security and analysis
   # Enable Dependabot alerts
   # Enable Dependabot security updates
   ```

### Workflow Files

All workflows are in `.github/workflows/`:

- `wiki-automation.yml` - Wiki management
- `project-automation.yml` - GitHub Projects integration
- `issue-automation.yml` - Issue lifecycle management
- `vulnerability-automation.yml` - Security scanning
- `dependabot-auto-merge.yml` - Auto-merge safe Dependabot PRs
- `agent-dispatcher.yml` - Command routing
- `sync-labels.yml` - Label synchronization

### Customization

**Change Project Number:**
Edit `project-automation.yml` and update the default project number:
```yaml
project_number: ${{ inputs.project_number || 1 }}  # Change 1 to your project number
```

**Adjust Stale Timing:**
Edit `issue-automation.yml`:
```yaml
days-before-stale: 60  # Change to your preference
days-before-close: 7   # Change to your preference
```

**Add/Remove Labels:**
Edit `.github/labels.yml` and push to main to sync.

**Customize Auto-labeling:**
Edit `issue-automation.yml` under `auto-label-issue` job.

### Monitoring

**View Workflow Runs:**
```bash
gh run list --workflow=issue-automation.yml
gh run view <run-id>
```

**Check Security Alerts:**
```bash
# Issues with 'security' label
gh issue list --label security

# Dependabot alerts
gh api /repos/:owner/:repo/dependabot/alerts
```

**Review Auto-merged PRs:**
```bash
gh pr list --label automated --state closed
```

## Examples

### Example 1: Create API Documentation

**Option A - Via Issue:**
1. Create issue with title: "Wiki Update: API-Documentation"
2. Add content in the body
3. Add label: `wiki-update`
4. Workflow creates the wiki page

**Option B - Via Command:**
```
/agent wiki-create page_name="API-Documentation" content="# API Docs\n\n## Endpoints\n\n..."
```

### Example 2: Bulk Issue Creation

```bash
for i in {1..5}; do
  gh workflow run issue-automation.yml \
    -f action=create \
    -f title="Task $i" \
    -f body="Description for task $i" \
    -f labels="enhancement"
done
```

### Example 3: Weekly Security Review

```bash
# Run security scan
gh workflow run vulnerability-automation.yml -f action=scan

# Review results
gh issue list --label security --state open

# Review Dependabot alerts summary
gh workflow run vulnerability-automation.yml -f action=review_alerts
```

### Example 4: Archive Old Wiki Pages

```bash
gh workflow run wiki-automation.yml \
  -f action=archive \
  -f page_name="Old-Documentation"
```

## Troubleshooting

### Wiki Automation Not Working

**Problem:** "Could not checkout wiki"
**Solution:** Initialize wiki by creating at least one page manually

### Project Automation Failing

**Problem:** "Project not found"
**Solution:** 
1. Verify project number in URL
2. Ensure it's a Projects V2 (not classic)
3. Check organization vs repository project

### Dependabot PRs Not Auto-merging

**Problem:** PRs stay open despite approval
**Solution:**
1. Settings → General → Pull Requests
2. Enable "Allow auto-merge"
3. Ensure branch protection doesn't prevent auto-merge

### Permission Errors

**Problem:** "Resource not accessible by integration"
**Solution:**
1. Settings → Actions → General
2. Workflow permissions → "Read and write"
3. Check "Allow GitHub Actions to create and approve pull requests"

### Labels Not Syncing

**Problem:** Labels not updating after changing `labels.yml`
**Solution:**
1. Ensure changes are pushed to main branch
2. Manually trigger: `gh workflow run sync-labels.yml`
3. Check workflow logs for errors

## Security Considerations

1. **Review Auto-merged PRs:** Periodically review automatically merged PRs
2. **Monitor Security Issues:** Check security-labeled issues weekly
3. **Update Dependencies:** Keep workflows up to date
4. **Access Control:** Limit who can trigger workflows manually
5. **Audit Logs:** Review Actions audit logs regularly

## Best Practices

### For Agents

1. **Use descriptive titles** - Helps with auto-labeling
2. **Include keywords** - Triggers appropriate workflows
3. **Check workflow status** - Verify commands executed successfully
4. **Use issue templates** - Ensures required information is provided
5. **Report issues** - If automation fails, create an issue

### For Maintainers

1. **Monitor workflow runs** - Check for failures
2. **Review security alerts** - Respond to vulnerabilities quickly
3. **Keep workflows updated** - Update GitHub Actions versions
4. **Test major changes** - Test workflow changes in a branch first
5. **Document customizations** - Note any custom configurations

## Getting Help

- **Workflow Documentation:** See `.github/workflows/README.md`
- **Issue Templates:** Use provided templates for common tasks
- **Security Policy:** See `.github/SECURITY.md`
- **Command Help:** Comment `/help` on any issue
- **GitHub Issues:** Create an issue for workflow problems

## Contributing

To contribute new automation:

1. Create workflow in `.github/workflows/`
2. Add documentation to workflow README
3. Test with workflow_dispatch first
4. Add to agent dispatcher if command-based
5. Update this guide with usage examples

## Changelog

### 2025-11-13 - Initial Release
- Wiki automation
- Project automation
- Issue management
- Security scanning
- Dependabot auto-merge
- Agent command dispatcher
- Label syncing
- Issue templates
