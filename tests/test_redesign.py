"""Dataset integrity and end-to-end management flows for the Orbit redesign."""
from datetime import timedelta
from html import unescape
from uuid import uuid4

from bson import ObjectId
from fastapi.testclient import TestClient
import pytest

from app.database import database
from app.main import app
from scripts.seed_database import NOW, USERS, build_events


def test_demo_dataset_integrity():
    user_ids = [ObjectId() for _ in USERS]
    events = build_events(user_ids)
    assert len(USERS) == 42
    assert len(events) == 30
    assert len({u['email'] for u in USERS}) == 42
    assert sum(len(e['registrations']) for e in events) == 445
    assert sum(e['startDate'] < NOW for e in events) == 11
    assert len({e['category'] for e in events}) == 7
    registered = set()
    for event in events:
        assert event['startDate'] < event['endDate']
        assert event['organizerId'] in user_ids
        assert USERS[user_ids.index(event['organizerId'])]['role'] in ('staff', 'organizer')
        ids = [r['userId'] for r in event['registrations']]
        assert len(ids) == len(set(ids)) <= event['capacity']
        assert event['organizerId'] not in ids
        for registration in event['registrations']:
            assert registration['userId'] in user_ids
            assert event['createdAt'] <= registration['registeredAt'] < event['startDate']
        registered.update(ids)
    assert len(set(user_ids) - registered) == 6
    assert sum(len(e['registrations']) == e['capacity'] for e in events) == 3
    assert sum(not e['registrations'] for e in events) == 3


@pytest.fixture
def web():
    with TestClient(app) as client:
        yield client


def test_all_seeded_details_and_edit_forms(web):
    for event in database.events.find({}):
        for suffix in ('', '/edit'):
            response = web.get(f"/events/{event['_id']}{suffix}")
            assert response.status_code == 200
            assert event['title'] in unescape(response.text)
    for user in database.users.find({}):
        for suffix in ('', '/edit'):
            response = web.get(f"/users/{user['_id']}{suffix}")
            assert response.status_code == 200
            assert user['firstName'] in response.text


def test_event_and_user_management_flow(web):
    token = uuid4().hex
    emails = [f'qa.{token}.{i}@orbit.example' for i in range(2)]
    event_title = f'QA gathering {token}'
    created_user_ids = []
    created_event_id = None
    try:
        for i, email in enumerate(emails):
            form = dict(first_name='Test', last_name=f'Member{i}', email=email,
                        department='Test Studio', role='student', interests='Design, Arts')
            assert web.post('/users/new', data=form, follow_redirects=False).status_code == 303
            user = database.users.find_one({'email': email})
            created_user_ids.append(user['_id'])
            assert web.post('/users/new', data=form).status_code == 400
        user_id = str(created_user_ids[0])
        form['email'] = emails[0]
        form['first_name'] = 'Updated'
        assert web.post(f'/users/{user_id}/edit', data=form).status_code == 200
        assert database.users.find_one({'_id': created_user_ids[0]})['firstName'] == 'Updated'
        event_form = dict(title=event_title, description='A temporary QA event.', category='Making',
                          tags='Design, Arts', start_date=(NOW + timedelta(days=10)).isoformat(),
                          end_date=(NOW + timedelta(days=10, hours=2)).isoformat(), capacity=1,
                          building='Test Studio', room='QA Room', address='Test Campus', organizer_id=user_id)
        assert web.post('/events/new', data={**event_form, 'capacity': 0}).status_code == 400
        assert web.post('/events/new', data=event_form, follow_redirects=False).status_code == 303
        event = database.events.find_one({'title': event_title})
        created_event_id = event['_id']
        url = f'/events/{created_event_id}'
        assert web.post(f'{url}/edit', data={**event_form, 'description': 'Updated event description.'}).status_code == 200
        assert 'Updated event description.' in web.get(url).text
        participant = str(created_user_ids[1])
        assert web.post(f'{url}/registrations', data={'user_id': participant}).status_code == 200
        assert len(database.events.find_one({'_id': created_event_id})['registrations']) == 1
        response = web.post(f'{url}/registrations', data={'user_id': participant})
        assert 'already registered' in response.text
        response = web.post(f'{url}/registrations', data={'user_id': user_id})
        assert 'event is full' in response.text
        assert len(database.events.find_one({'_id': created_event_id})['registrations']) == 1
        assert web.post(f'/users/{user_id}/delete').status_code == 200
        assert database.users.find_one({'_id': created_user_ids[0]}) is not None
        assert web.post(f'{url}/registrations/{participant}/delete').status_code == 200
        assert database.events.find_one({'_id': created_event_id})['registrations'] == []
        assert web.post(f'{url}/delete').status_code == 200
        assert database.events.find_one({'_id': created_event_id}) is None
        for ident in created_user_ids:
            assert web.post(f'/users/{ident}/delete').status_code == 200
            assert database.users.find_one({'_id': ident}) is None
    finally:
        if created_event_id:
            database.events.delete_one({'_id': created_event_id})
        database.users.delete_many({'email': {'$in': emails}})


def test_status_filters_and_empty_results(web):
    assert 'Quantum Puzzle Room' in web.get('/events?status=upcoming').text
    assert 'Satellite Signal Sprint' not in unescape(web.get('/events?status=upcoming').text)
    assert 'Quantum Puzzle Room' not in web.get('/events?status=past').text
    assert 'Drone Control Simulator' not in web.get('/events?status=available').text
    assert 'No events match' in web.get('/events?q=does-not-exist-qa').text
    assert 'No users' in web.get('/users?q=does-not-exist-qa').text
