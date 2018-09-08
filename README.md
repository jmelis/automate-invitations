# automate-invitations.py

## Description

[automate-invitations.py](automate-invitations.py) accepts Github repository
invitations if the target repositories are listed in a whitelist file.

This whitelist file should be yaml file with a top-level array as follows:

```yaml
---
- org1/repo1
- org1/repo2
- ...
```

## Authentication

Requires the env variable `GH_TOKEN` to be defined with a personal token or an OAuth token.

Generate the personal auth token with permissions `repo:invite`.

## Usage

```
usage: automate-invitations.py [-h] -l LIST

Accept whitelisted invitations

optional arguments:
  -h, --help            show this help message and exit
  -l LIST, --list LIST  Yaml file with the whitelisted repos
```
