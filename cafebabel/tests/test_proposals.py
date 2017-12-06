from flask.helpers import get_flashed_messages

from .. import mail


def test_proposal_display_form(app, client):
    response = client.get('/article/proposal/new/')
    assert response.status_code == 200
    assert '<form action=. method=post>' in response


def test_proposal_send_email(app, client):
    mail.init_app(app)  # Re-load using test configuration.
    with mail.record_messages() as outbox:
        response = client.post('/article/proposal/new/', data={
            'language': app.config['LANGUAGES'][0][0],
            'email': 'email@example.com',
            'topic': 'Topic',
            'name': 'Name',
            'media': 'video',
            'section': 'creative',
            'city': 'City',
            'angle': 'Angle',
            'format': 'Format',
            'additional': 'Additional'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert len(outbox) == 1
        assert outbox[0].subject == 'Article proposal: Topic'
        assert outbox[0].body == f'''
Language: {app.config['LANGUAGES'][0][0]}
Name: Name
Email: email@example.com
City: City
Topic: Topic
Media: video
Format: Format
Section: creative
Addiction comment: Additional
'''
    assert get_flashed_messages() == ['Your proposal was successfully sent.']