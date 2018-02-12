# trans-git
Silly little utility for purging deadnames from your public GitHub repos

## Requirements
- Python3
- requests

## Running
Right now only your public Github repositories are supported:

`python3 transGit.py -r 'Dead Name' 'New Name' -r 'Dead@email.com' 'new@email.com' github YourUsername`

The script will clone all your public repositories and clean them. It'll give you the option to force-push your changes back up. It's recommended to inspect the cleaned repo at this point (stored in `./.tmp` by default):

- If everything looks good, you can answer `y` and the script will push for you.
- If you'd like to skip this remote, enter `n`.
- If you'd like to do something custom, now's the time. When you're done, enter `y` to push or `n` to skip pushing.

Note that once the repo has been pushed (or not), the local copy **will be deleted**. Make sure you've saved it before answering y/n if you want to preserve it.

**WARNING**: This script uses `git filter-branch` and force pushing. This *WILL* mess up any collaborators the same as if you did a rebase. See the git docs on filter-branch for more details.
