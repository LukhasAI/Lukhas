---
status: wip
type: documentation
---
# Workflow Secret Management

This directory contains GitHub Actions workflows that may require access to API keys and tokens.

## Setting Up Secrets

Two options are available:

### Option 1: GitHub Repository Secrets (Recommended)
Set up your secrets in GitHub repository settings:
- Go to your repository on GitHub
- Click on Settings > Secrets and variables > Actions
- Add the necessary secrets with the same names used in workflows

### Option 2: Local Secrets File
For local testing, a `.env.secrets` file is provided with the necessary keys.
⚠️ **IMPORTANT**: This file contains sensitive information and should not be committed to the repository.

## Required Secrets

The following secrets are typically required:
- `GITHUB_TOKEN` - GitHub API token
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions for repository operations and ΛBot automation
- `OPENAI_API_KEY` - OpenAI API key
- `AZURE_OPENAI_API` - Azure OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `GOOGLE_API_KEY` - Google API key
- `PERPLEXITY_API_KEY` - Perplexity API key
- `NOTION_API_TOKEN` - Notion API token
- `ELEVENLABS_API_KEY` - ElevenLabs API key

## Accessing Secrets in Workflows

In your workflow YAML files, use secrets like this:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

For composite actions or reusable workflows that need secrets, pass them explicitly:

```yaml
jobs:
  my_job:
    runs-on: ubuntu-latest
    steps:
      - name: Use external action
        uses: external/action@v1
        with:
          api-key: ${{ secrets.OPENAI_API_KEY }}
```
