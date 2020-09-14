import pytest


def test_userctl(app):
    # Block normal user
    username = "Test User"
    usermail = "test@example.com"
    userid = "https://example.com/test"
    app.main("-u", app.path, "block-user", userid)
    user1 = app.users().get("1")
    user2 = app.users().get("2")
    assert user1.get("name") == username
    assert user1.get("email") == usermail
    assert user1.get("userid") == userid
    assert user1.get("blocked") is True
    assert user2.get("blocked") is None
    commit = app.get_last_commit()
    assert commit.author == "MSCWG <mscwg@rda-groups.org>".encode('utf8')
    assert commit.message == (f"Block user {userid}\n\nChanged by userctl"
                              .encode('utf8'))

    # Unblock normal user
    app.main("-u", app.path, "unblock-user", userid)
    user1 = app.users().get("1")
    user2 = app.users().get("2")
    assert user1.get("name") == username
    assert user1.get("email") == usermail
    assert user1.get("userid") == userid
    assert user1.get("blocked") is False
    assert user2.get("blocked") is None
    commit = app.get_last_commit()
    assert commit.author == "MSCWG <mscwg@rda-groups.org>".encode('utf8')
    assert commit.message == (f"Unblock user {userid}\n\nChanged by userctl"
                              .encode('utf8'))

    # Normal user not found
    with pytest.raises(SystemExit) as failure:
        app.main("-u", app.path, "block-user", "non-existent")
        assert failure.type == SystemExit
        assert failure.value.code == 1

    # Register API user
    apiusername = "API Tester"
    apiuserid = "apitest"
    apiusermail = "test.app@example.com"
    app.main("-u", app.path, "add-api-user", apiusername, apiuserid, apiusermail)
    apiuser1 = app.apiusers().get("1")
    assert apiuser1.get("name") == apiusername
    assert apiuser1.get("userid") == apiuserid
    assert apiuser1.get("email") == apiusermail
    assert apiuser1.get("password_hash")
    assert apiuser1.get("blocked") is None
    commit = app.get_last_commit()
    assert commit.author == "MSCWG <mscwg@rda-groups.org>".encode('utf8')
    assert commit.message == (f"Add API user {apiusername}\n\nChanged by userctl"
                              .encode('utf8'))

    # Bad username
    with pytest.raises(SystemExit) as failure:
        app.main("-u", app.path, "add-api-user", apiusername, "quäck^", apiusermail)
        assert failure.type == SystemExit
        assert failure.value.code == 1

    # Bad email
    with pytest.raises(SystemExit) as failure:
        app.main("-u", app.path, "add-api-user", apiusername, apiuserid, "boo")
        assert failure.type == SystemExit
        assert failure.value.code == 1

    # Block API user
    app.main("-u", app.path, "block-api-user", apiuserid)
    apiuser1 = app.apiusers().get("1")
    assert apiuser1.get("name") == apiusername
    assert apiuser1.get("userid") == apiuserid
    assert apiuser1.get("email") == apiusermail
    assert apiuser1.get("blocked") is True
    commit = app.get_last_commit()
    assert commit.author == "MSCWG <mscwg@rda-groups.org>".encode('utf8')
    assert commit.message == (f"Block user {apiuserid}\n\nChanged by userctl"
                              .encode('utf8'))

    # Unblock API user
    app.main("-u", app.path, "unblock-api-user", apiuserid)
    apiuser1 = app.apiusers().get("1")
    assert apiuser1.get("name") == apiusername
    assert apiuser1.get("userid") == apiuserid
    assert apiuser1.get("email") == apiusermail
    assert apiuser1.get("blocked") is False
    commit = app.get_last_commit()
    assert commit.author == "MSCWG <mscwg@rda-groups.org>".encode('utf8')
    assert commit.message == (f"Unblock user {apiuserid}\n\nChanged by userctl"
                              .encode('utf8'))

    # API user not found
    with pytest.raises(SystemExit) as failure:
        app.main("-u", app.path, "block-api-user", "non-existent")
        assert failure.type == SystemExit
        assert failure.value.code == 1
