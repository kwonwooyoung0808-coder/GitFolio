from app.services.github.filter import filter_my_commits


def test_filter_my_commits_matches_login_and_numeric_id():
    commits = [
        {"author": {"login": "alice", "id": 1}, "committer": None},
        {"author": {"login": "bob", "id": 2}, "committer": None},
        {"author": None, "committer": {"login": "alice", "id": 1}},
    ]

    by_login = filter_my_commits(commits, "alice")
    by_id = filter_my_commits(commits, "1")

    assert len(by_login) == 2
    assert len(by_id) == 2
