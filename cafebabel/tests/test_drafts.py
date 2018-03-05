from http import HTTPStatus
from pathlib import Path
from io import BytesIO

from flask import request

from ..articles.models import Article
from ..articles.tags.models import Tag
from .utils import login


def test_create_draft_requires_authentication(client):
    response = client.get('/en/article/draft/new/')
    assert response.status_code == HTTPStatus.FOUND
    assert '/login' in response.headers.get('Location')


def test_create_draft_should_display_form(client, editor):
    login(client, editor.email, 'password')
    response = client.get('/en/article/draft/new/')
    assert response.status_code == 200
    assert '<input id=title' in response


def test_create_draft_should_generate_article(client, user, editor):
    login(client, editor.email, 'password')
    response = client.post('/en/article/draft/new/', data={
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'authors': user.id
    }, follow_redirects=True)
    assert response.status_code == 200
    assert '<h1>Test article</h1>' in response
    assert '<p>Article body</p>' in response


def test_create_draft_with_tag(client, user, editor, tag):
    login(client, editor.email, 'password')
    response = client.post('/en/article/draft/new/', data={
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'authors': user.id,
        'tag-1': 'Wonderful'
    }, follow_redirects=True)
    assert response.status_code == 200
    article = Article.objects.get(title='Test article')
    assert article.tags == [tag]


def test_create_draft_with_tags(client, app, user, editor, tag):
    login(client, editor.email, 'password')
    language = app.config['LANGUAGES'][0][0]
    tag2 = Tag.objects.create(name='Sensational', language=language)
    response = client.post('/en/article/draft/new/', data={
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'authors': user.id,
        'tag-1': 'Wonderful',
        'tag-2': 'Sensational'
    }, follow_redirects=True)
    assert response.status_code == 200
    article = Article.objects.get(title='Test article')
    assert article.tags == [tag, tag2]


def test_create_draft_with_unknown_tag(client, user, editor, tag):
    login(client, editor.email, 'password')
    response = client.post('/en/article/draft/new/', data={
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'authors': user.id,
        'tag-1': 'Wonderful',
        'tag-2': 'Sensational'
    }, follow_redirects=True)
    assert response.status_code == 200
    article = Article.objects.get(title='Test article')
    tag2 = Tag.objects.get(name='Sensational')
    assert article.tags == [tag, tag2]


def test_create_draft_with_preexising_translation(client, user, editor,
                                                  article, translation):
    login(client, editor.email, 'password')
    response = client.post('/en/article/draft/new/', data={
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'authors': user.id,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert '<h1>Test article</h1>' in response
    assert '<p>Article body</p>' in response


def test_create_published_draft_should_display_article(client, user, editor):
    login(client, editor.email, 'password')
    response = client.post('/en/article/draft/new/', data={
        'title': 'Test article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'authors': user.id,
        'status': 'published',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert request.url_rule.endpoint == 'articles.detail'
    assert '<h1>Test article</h1>' in response
    assert '<p>Article body</p>' in response


def test_draft_editing_should_update_content(client, user, editor):
    login(client, editor.email, 'password')
    data = {
        'title': 'My article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'authors': [user.id],
    }
    draft = Article.objects.create(**data)
    updated_data = data.copy()
    updated_data['language'] = 'fr'
    response = client.post(f'/en/article/draft/{draft.id}/edit/',
                           data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    updated_draft = Article.objects.get(id=draft.id)
    assert updated_draft.id == draft.id
    assert updated_draft.language == 'fr'
    assert updated_draft.title == 'My article'


def test_draft_image_should_save_and_render(app, client, user, editor):
    login(client, editor.email, 'password')
    with open(Path(__file__).parent / 'dummy-image.jpg', 'rb') as content:
        image = BytesIO(content.read())
    data = {
        'title': 'My article',
        'summary': 'Summary',
        'body': 'Article body',
        'language': 'en',
        'authors': user.id,
        'image': (image, 'image-name.jpg'),
    }
    response = client.post('/en/article/draft/new/', data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    article = Article.objects.first()
    assert article.image_filename == '/articles/image-name.jpg'
    assert Path(app.config.get('UPLOADS_FOLDER') /
                'articles' / 'image-name.jpg').exists()
    assert f'<img src="{article.image_url}"' in response


def test_draft_should_not_offer_social_sharing(client, article):
    response = client.get(f'/en/article/draft/{article.id}/')
    assert response.status_code == 200
    assert 'facebook.com/sharer' not in response


def test_visitor_cannot_edit_draft(client, article):
    response = client.post(f'/en/article/draft/{article.id}/edit/', data={
        'title': 'Updated draft'
    })
    assert '/login' in response.headers.get('Location')


def test_author_cannot_edit_draft(client, user, article):
    login(client, user.email, 'password')
    response = client.post(f'/en/article/draft/{article.id}/edit/', data={
        'title': 'Updated draft'
    })
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_access_published_draft_should_return_404(client, article):
    article.status = 'published'
    article.save()
    response = client.get(f'/en/article/draft/{article.id}/')
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_editor_access_drafts_list(client, editor, article):
    login(client, editor.email, 'password')
    response = client.get('/en/article/draft/')
    assert response.status_code == HTTPStatus.OK
    assert article.title in response


def test_author_cannot_access_drafts_list(client, user):
    login(client, user.email, 'password')
    response = client.get('/en/article/draft/')
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_drafts_list_only_displays_drafts(client, editor, article,
                                          published_article):
    published_article.modify(title='published article')
    login(client, editor.email, 'password')
    response = client.get('/en/article/draft/')
    assert response.status_code == HTTPStatus.OK
    assert article.title in response
    assert published_article.title not in response


def test_draft_detail_contains_tags_without_links(client, app, tag, article):
    language = app.config['LANGUAGES'][0][0]
    tag2 = Tag.objects.create(name='Sensational', language=language)
    article.modify(tags=[tag, tag2])
    response = client.get(f'/en/article/draft/{article.id}/')
    assert response.status_code == HTTPStatus.OK
    assert 'Wonderful,' in response
    assert 'Sensational.' in response
