# GitHub CLI (gh) Setup for CI Environments

This guide provides instructions for setting up and using the GitHub CLI (`gh`) within a Continuous Integration (CI) environment, such as GitHub Actions.

## Introduction

The GitHub CLI provides a powerful and convenient way to interact with the GitHub API from the command line. In a CI environment, it can be used to automate tasks like creating releases, commenting on pull requests, or inspecting repository data.

## Authentication

The recommended way to authenticate the `gh` CLI in a CI workflow is to use the `GITHUB_TOKEN` that is automatically created for each job.

### Using `GITHUB_TOKEN`

You can authenticate by piping the token to the `gh auth login` command:

```yaml
- name: Authenticate with GitHub CLI
  run: echo "${{ secrets.GITHUB_TOKEN }}" | gh auth login --with-stdin
```

This command reads the token from standard input and configures `gh` to use it for subsequent commands.

## Required Scopes

The default `GITHUB_TOKEN` has a set of default permissions. If your CI job needs to perform actions that require additional permissions (e.g., writing to the repository), you must grant those permissions to the token in your workflow file.

Example of granting `contents: write` permission:

```yaml
permissions:
  contents: write
```

Refer to the [official GitHub documentation](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token) for a complete list of available scopes.

## Runner Permissions

Ensure that the GitHub Actions runner has the necessary permissions to execute the commands in your workflow. For self-hosted runners, this means the user running the runner process must have the appropriate permissions on the host machine. For GitHub-hosted runners, the environment is already configured.

## Troubleshooting

### `Permission denied` errors

If you encounter permission denied errors when running `gh` commands, check the following:

1.  **Token Scopes:** Verify that the `GITHUB_TOKEN` has the required scopes for the operation you are trying to perform. You may need to add a `permissions` block to your workflow file.
2.  **Repository Settings:** Check the repository's settings under **Settings > Actions > General**. Ensure that workflows have the appropriate permissions (e.g., "Read and write permissions").

### `gh: command not found`

This error means the `gh` CLI is not installed on the runner. While most GitHub-hosted runners come with `gh` pre-installed, some environments may not. You can install it using the following step:

```yaml
- name: Install GitHub CLI
  run: |
    sudo apt-get update
    sudo apt-get install gh -y
```

This example is for Debian/Ubuntu-based runners. Adjust the command for other operating systems.
