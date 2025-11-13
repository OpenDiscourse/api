# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities to **[security@opendiscourse.org](mailto:security@opendiscourse.org)**. You will receive a response from us within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within a few days.

## Automated Security Scanning

This repository has automated security scanning enabled:

### Dependabot
- **What it does:** Automatically scans dependencies for known vulnerabilities
- **Frequency:** Continuous monitoring with weekly updates
- **Action:** Creates pull requests to update vulnerable dependencies
- **Auto-merge:** Minor and patch security updates are automatically approved and merged

### Vulnerability Automation Workflow
- **What it does:** 
  - Scans Python dependencies using `safety` and `pip-audit`
  - Creates issues for detected vulnerabilities
  - Can automatically create PRs to fix vulnerabilities
- **Frequency:** Weekly on Sunday, plus on every push to main
- **Manual trigger:** Can be run manually via GitHub Actions

### How Automatic Fixes Work

1. **Detection:** Security vulnerabilities are detected by Dependabot or our scanning tools
2. **PR Creation:** An automated PR is created with the fix
3. **Auto-merge:** If the update is a security patch or minor/patch update:
   - PR is automatically approved
   - All checks must pass
   - PR is automatically merged via squash merge
4. **Manual Review:** Major updates are flagged and require manual review

### Opting Out of Auto-merge

If you want to manually review all security updates:
1. Remove the `dependabot-auto-merge.yml` workflow
2. Dependabot will still create PRs, but they won't auto-merge

## Security Best Practices

When contributing to this repository:

1. **Dependencies:** Only add dependencies from trusted sources
2. **Secrets:** Never commit secrets, API keys, or credentials
3. **Code Review:** All code changes require review before merging
4. **Updates:** Keep dependencies up to date
5. **Scanning:** Run security scans locally before committing

## Security Features

This repository includes:

- ✅ Dependabot security updates
- ✅ Automated dependency scanning
- ✅ Automated vulnerability issue creation
- ✅ Auto-merge of security patches
- ✅ Weekly security scans
- ✅ Security labels on issues and PRs

## Vulnerability Disclosure Timeline

- **0 days:** Security issue reported
- **Within 48 hours:** Initial response and triage
- **Within 7 days:** Fix developed (for confirmed issues)
- **Within 14 days:** Patch released
- **30 days after patch:** Public disclosure (if applicable)

## Contact

For security concerns, contact:
- Email: security@opendiscourse.org
- For general bugs: Use GitHub Issues
- For security vulnerabilities: Use email (above)

## Hall of Fame

We appreciate security researchers who help us keep this project secure. With permission, we'll list contributors here who responsibly disclose vulnerabilities.

---

Last updated: 2025-11-13
