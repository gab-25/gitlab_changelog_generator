# GitLab Changelog Generator

A Python tool designed to automate the generation of `CHANGELOG.md` files for GitLab projects. It follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format by analyzing merged Merge Requests (MRs).

## Features

- **Automated Versioning**: Extracts version numbers from MR titles (e.g., "Release v1.2.3").
- **Smart Categorization**: Groups changes into standard categories like `Added`, `Fixed`, `Changed`, and `Deprecated` based on GitLab labels.
- **Merge Request Linking**: Automatically adds links to the relevant MRs and mentions the authors.
- **Keep a Changelog Format**: Updates existing changelogs while preserving history.

## Prerequisites

- Python 3.13+
- [Poetry](https://python-poetry.org/) for dependency management.
- A GitLab Private Token with API access.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd gitlab_changelog_generator
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

## Configuration

The tool requires a `.env` file for authentication. You can place it in the project root or at `~/.gitlab_changelog_generator`.

Create a `.env` file with the following content:

```env
GITLAB_URL=https://gitlab.com  # Or your self-hosted instance URL
GITLAB_PRIVATE_TOKEN=your_private_access_token
```