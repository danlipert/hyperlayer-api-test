import unirest

#add mashape key
unirest.default_header('X-Mashape-User','Value1')

hostname = 'http://localhost'

def test_health_check():
    response = unirest.get(hostname + '/health/')
    assert response.code == 200

def test_no_auth():
    response = unirest.get(hostname + '/detection/')
    print response.code
    assert response.code == 302


