#!/usr/bin/env python3

import argparse, subprocess, requests, shutil, os

script_path = os.path.dirname(os.path.realpath(__file__))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--dest', default=os.path.join(script_path, '.tmp'), help='Where to clone the temporary repository')
	parser.add_argument('-r', dest='replacements', action='append', help='Replacement <find> <replace>. May be given multiple times', nargs=2, required=True)

	subparsers = parser.add_subparsers(dest='service')
	subparsers.required = True

	github_p = subparsers.add_parser('github', help='Gets repositories from GitHub')
	github_p.add_argument('username', help='Your GitHub username')

	bitbucket_p = subparsers.add_parser('bitbucket', help='Gets repositories from BitBucket')
	bitbucket_p.add_argument('username', help='Your BitBucket username')

	args = parser.parse_args()
	replacements = dict(args.replacements)
	dest = args.dest
	username = args.username
	service = args.service

	# These function return a list of dicts with values 'name' and 'ssh_url'
	services = {
		'github': github,
		'bitbucket': bitbucket
	}

	print('Downloading your repos... ', end='')
	repos = services[service](username)
	return process_repos(repos, replacements, dest)
#enddef

def process_repos(repos, replacements, dest):
	print('Found {} repos'.format(len(repos)))

	for repo in repos:
		print('>>> Processing {}'.format(repo['name']))
		try: shutil.rmtree(dest)
		except: pass
		subprocess.check_call(['git', 'clone', repo['ssh_url'], dest])
		clean_git_repo(dest, replacements)
		print()

def github(username):
	r = requests.get('https://api.github.com/users/{0}/repos'.format(username))
	r.raise_for_status()
	repos = r.json()
	return repos


def bitbucket(username):
	r = requests.get('https://api.bitbucket.org/2.0/repositories/{0}'.format(username))
	r.raise_for_status()
	response = r.json()['values']

	repos = []
	for repo in response:
		repo_name = repo['name']
		repo_link = [x['href'] for x in repo['links']['clone'] if x['name'] == 'ssh'][0]
		repos.append({
			'name': repo_name,
			'ssh_url': repo_link
		})
	return repos


def get_env_filter(replacements):
	script = ''
	for find, replace in replacements.items():
		for var in ('AUTHOR_EMAIL', 'AUTHOR_NAME', 'COMMITTER_EMAIL', 'COMMITTER_NAME'):
			script += '''	if test "$GIT_{var}" = '{find}'
	then
		GIT_{var}='{replace}'
	fi
'''.format(find=find, replace=replace, var=var)

	return script
#enddef

def clean_git_repo(repoPath, replacements, remotesToUpdate=None, quiet=False):
	filter = get_env_filter(replacements)

	subprocess.check_call(['git', 'filter-branch', '--env-filter', filter, '--tag-name-filter', 'cat', '--', '--all'], cwd=repoPath)

	remotes = subprocess.check_output(['git', 'remote', 'show'], cwd=repoPath).decode().strip().split(' ')
	if remotesToUpdate is None:
		remotesToUpdate = remotes
	else:
		remotesToUpdate = set(remotesToUpdate).intersection(remotes)

	for remote in remotes:
		if quiet or input('Update remote "{0}"? [y/n] '.format(remote)) == 'y':
			subprocess.check_call(['git', 'push', '-f', '--all', remote], cwd=repoPath)
		else:
			print('Skipping...')
	#endfor
#enddef

if __name__ == '__main__': main()
