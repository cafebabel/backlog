from http import HTTPStatus
from pathlib import Path

from flask.helpers import get_flashed_messages

from ..articles.models import Article
from .utils import login


def test_proposal_sends_email_to_editor(app, client):
    response = client.get('/article/proposal/')
    assert response.status_code == 200
    assert 'action=/article/proposal/' in response.get_data().decode()


def test_create_draft_should_generate_article(client, editor):
    login(client, editor.email, 'secret')
    response = client.post('/article/draft/', data={
        'title': 'Test article',
        'language': 'en',
        'body': 'Article body',
    }, follow_redirects=True)
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert '<h1>Test article</h1>' in body
    assert '<p>Article body</p>' in body


def test_draft_editing_should_update_content(client, editor):
    login(client, editor.email, 'secret')
    data = {'title': 'My article', 'language': 'en', 'body': 'Article body'}
    draft = Article.objects.create(**data)
    updated_data = data.copy()
    updated_data['language'] = 'fr'
    response = client.post(f'/article/draft/{draft.uid}/edit/',
                           data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    updated_draft = Article.objects.get(uid=draft.uid)
    assert updated_draft.id == draft.id
    assert updated_draft.language == 'fr'
    assert updated_draft.title == 'My article'


def test_draft_image_should_save_and_render(client, editor):
    login(client, editor.email, 'secret')
    image = open(Path(__file__).parent / 'dummy-image.jpg')
    data = {
        'title': 'My article',
        'language': 'en',
        'body': 'Article body',
        'image': image,
    }
    response = client.post('/article/draft/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    image.close()
    article = Article.objects.first()
    assert Path(app.config.get('ARTICLES_IMAGES_PATH') / article.id).exists()


def test_access_published_article_should_return_200(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.OK


def test_access_article_with_large_slug_should_return_200(client, article):
    article.status = 'published'
    article.slug = 'quite-large-slug-with-dashes'
    article.save()
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.OK


def test_access_draft_article_should_return_404(client, article):
    response = client.get(f'/article/{article.slug}-{article.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_no_article_should_return_404(client):
    response = client.get(f'/article/foo-bar/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_no_id_should_return_404(client):
    response = client.get(f'/article/foobar/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_old_slug_article_should_return_301(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/article/wrong-slug-{article.id}/')
    assert response.status_code == HTTPStatus.MOVED_PERMANENTLY


def test_access_article_form_regular_user_should_return_403(client, user,
                                                            article):
    login(client, user.email, 'secret')
    response = client.get(f'/article/{article.id}/form/')
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_access_published_article_form_should_return_200(client, editor,
                                                         article):
    login(client, editor.email, 'secret')
    article.status = 'published'
    article.save()
    response = client.get(f'/article/{article.id}/form/')
    assert response.status_code == HTTPStatus.OK


def test_access_draft_article_form_should_return_404(client, editor, article):
    login(client, editor.email, 'secret')
    response = client.get(f'/article/{article.id}/form/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_access_no_article_form_should_return_404(client, editor):
    login(client, editor.email, 'secret')
    response = client.get(f'/article/foobarbazquxquuxquuzcorg/form/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_published_article_should_return_200(client, user, editor,
                                                    article):
    login(client, editor.email, 'secret')
    article.status = 'published'
    article.save()
    data = {
        'title': 'updated',
        'author': user.id
    }
    response = client.post(f'/article/{article.id}/', data=data,
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    article.reload()
    assert article.title == 'updated'
    assert article.author == user
    assert article.editor == editor
    assert get_flashed_messages() == ['Your article was successfully saved.']


def test_update_article_with_user_should_return_403(client, user, article):
    login(client, user.email, 'secret')
    article.status = 'published'
    article.save()
    data = {
        'title': 'updated',
        'author': user.id
    }
    response = client.post(f'/article/{article.id}/', data=data)
    assert response.status_code == HTTPStatus.FORBIDDEN
    article.reload()
    assert article.title == 'title'


def test_update_unpublished_article_should_return_404(client, user, editor,
                                                      article):
    login(client, editor.email, 'secret')
    data = {
        'title': 'updated',
        'author': user.id
    }
    response = client.post(f'/article/{article.id}/', data=data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    article.reload()
    assert article.title == 'title'


def test_delete_article_should_return_200(client, editor, article):
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert Article.objects.all().count() == 0
    assert get_flashed_messages() == ['Article was deleted.']


def test_delete_article_regular_user_should_return_403(client, user, article):
    login(client, user.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/')
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert Article.objects.all().count() == 1


def test_delete_incorrect_id_should_return_404(client, editor, article):
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}foo/delete/')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Article.objects.all().count() == 1


def test_delete_inexistent_article_should_return_404(client, editor, article):
    article.delete()
    login(client, editor.email, 'secret')
    response = client.post(f'/article/{article.id}/delete/')
    assert response.status_code == HTTPStatus.NOT_FOUND
