def filter_my_commits(commits: list, github_identity: str) -> list:
    """Filter commits by GitHub login or numeric GitHub user id."""
    my_commits = []
    identity = str(github_identity).strip().lower()

    for commit in commits:
        author = commit.get("author") or {}
        committer = commit.get("committer") or {}
        login = str(author.get("login") or committer.get("login") or "").lower()
        author_id = str(author.get("id") or committer.get("id") or "").lower()
        if identity and identity in {login, author_id}:
            my_commits.append(commit)

    return my_commits
