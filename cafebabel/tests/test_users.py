from http import HTTPStatus

from ..users.models import Role, UserRoles


def test_user_has_no_default_roles(user):
    assert not user.has_role('editor')
    assert not user.has_role('admin')
    assert not user.has_role('whatever')


def test_user_add_custom_role(user):
    editor = Role.get(name='editor')
    UserRoles.create(user=user, role=editor)
    assert user.has_role('editor')
    assert not user.has_role('admin')
    assert not user.has_role('whatever')


def test_admin_has_all_roles(admin):
    assert admin.has_role('editor')
    assert admin.has_role('admin')
    assert admin.has_role('whatever')


def test_unauthenticated_user_cannot_access_login_required_page(client):
    response = client.get('/profile/')
    assert response.status_code == HTTPStatus.FOUND
