def test_create_incident(client, auth_tokens):
    response = client.post('/api/incidents',
        headers={'Authorization': f'Bearer {auth_tokens}'},
        json={
            'title': 'Test Incident',
            'description': 'Test description',
            'latitude': -1.292066,
            'longitude': 36.821946
        }
    )
    assert response.status_code == 201
    assert b'Incident created successfully' in response.data

def test_get_incidents(client, auth_tokens):
    # First create an incident
    client.post('/api/incidents',
        headers={'Authorization': f'Bearer {auth_tokens}'},
        json={...}
    )
    
    # Then test getting incidents
    response = client.get('/api/incidents')
    assert response.status_code == 200
    assert len(response.json) > 0

def test_incident_status_update(client, auth_tokens, admin_tokens):
    # Create incident
    res = client.post('/api/incidents',
        headers={'Authorization': f'Bearer {auth_tokens}'},
        json={...}
    )
    incident_id = res.json['id']
    
    # Update status (admin only)
    response = client.put(f'/api/incidents/{incident_id}/status',
        headers={'Authorization': f'Bearer {admin_tokens}'},
        json={'status': 'under_investigation'}
    )
    assert response.status_code == 200