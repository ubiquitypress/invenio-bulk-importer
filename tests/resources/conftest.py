import pytest

from flask_security import login_user
from invenio_accounts.testutils import login_user_via_session
from invenio_access.models import ActionRoles
from invenio_accounts.models import Role
from invenio_administration.permissions import administration_access_action


@pytest.fixture()
def headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/json",
    }


@pytest.fixture()
def admin_client(client, user_admin, app, db):
    """Log in a user to the client."""
    user = user_admin.user
    print(type(user))
    # login_user(user)
    login_user_via_session(client, email=user.email)
    return client
