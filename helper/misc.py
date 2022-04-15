from git import Repo

git = Repo(".")
commits_from_repo = list(git.iter_commits())
result = len(commits_from_repo)
top = int(result // 1000)
ver = int((result % 1000) // 100)
bottom = int((result % 1000) % 100)
__version__ = f"{top}.{ver}.{bottom}"
