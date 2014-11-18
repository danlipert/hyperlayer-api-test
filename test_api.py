import unirest
import time
import string
import random

#add mashape key
def set_unirest_defaults():
    unirest.default_header("X-Mashape-User", "TESTUSER")
    unirest.default_header("X-Mashape-Proxy-Secret", "DEBUG")

unirest.timeout(100)

hostname = 'http://localhost'

MODEL_COMPILATION_SECONDS = 5

def test_health_check():
    response = unirest.get(hostname + '/health/')
    assert response.code == 200

'''
def test_no_auth(): 
    #doesnt work with DEBUG = True in settings.py
    response = unirest.get(hostname + '/')
    assert response.code == 403
'''

# --- AUTH TESTING ---
def test_random_new_user():
    unirest.clear_default_headers()
    set_unirest_defaults()
    random_username = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    print random_username
    #permissions_response = unirest.get(hostname + '/users/',
    #    headers={"X-Mashape-User":random_username, "X-Mashape-Proxy-Secret":"DEBUG"})
    permissions_response = unirest.get(hostname + '/users/')
    print permissions_response.body
    set_unirest_defaults()
    assert permissions_response.code == 200


def test_mashape_user_auth():
    response = unirest.get(hostname + '/')
    assert response.code == 200

def test_mashape_failed_secret():
    unirest.clear_default_headers()
    response = unirest.get(hostname + '/',
        headers={"X-Mashape-User":"TESTUSER", "X-Mashape-Proxy-Secret":"asdfasdfasdf"})
    set_unirest_defaults()
    assert response.code == 403

#def test_token_auth():
#    assert 1==1

# --- DETECTION TESTING ---

def test_detect_url():
    response = unirest.post(hostname + '/detect-upload/',
        params={"image_url":"http://img1.wikia.nocookie.net/__cb20130930223832/armoredheroes/images/3/37/Arnold_Schwarzenegger.jpg"})
    print response.body
    assert response.code == 200


def test_detect_post():
    response = unirest.post(hostname + '/detect-upload/',
        params={"image": open("./arnold.jpg", mode="r")})
    print response.body
    assert response.code == 200
    assert response.body


# --- PREDICTION TESTING ---

def test_enroll_image_url_and_create_training_set():
    response = unirest.post(hostname + '/enroll-image/',
        params={"image_url":"http://img1.wikia.nocookie.net/__cb20130930223832/armoredheroes/images/3/37/Arnold_Schwarzenegger.jpg", "label":"Arnold"})
    #print response.body
    #print response.code
    assert response.code == 200
    print response.body
    face_images = response.body['face_images']
    #check first face image
    face_image_link = face_images[0]
    face_image_response = unirest.get(face_image_link)
    face_image_url = face_image_response.body['url']
    assert face_image_url.startswith('http') == True

def test_enroll_image_post_and_create_training_set():
    response = unirest.post(hostname + '/enroll-image/',
        params={"image": open("./arnold.jpg", mode="r"), "label":"Arnold"})
    assert response.code == 200

def test_enroll_image_in_existing_training_set():
    first_image_response = unirest.post(hostname + '/enroll-image/',
        params={"image": open("./arnold.jpg", mode="r"), "label":"Arnold"})
    assert first_image_response.code == 200
    print first_image_response.body
    training_set_id = first_image_response.body['id']
    second_image_response = unirest.post(hostname + '/enroll-image/',
        params={"image": open("./arnold.jpg", mode="r"), "label":"Arnold", "training_set_id":training_set_id})
    assert second_image_response.code == 200
    print second_image_response.body
    #check training set
    training_set_response = unirest.get(hostname + '/trainingset/' + training_set_id + '/')
    print training_set_response.body
    face_images = training_set_response.body['face_images']
    assert len(face_images) == 2


def test_compile_model():
    first_image_response = unirest.post(hostname + '/enroll-image/',
        params={"image": open("./arnold.jpg", mode="r"), "label":"Arnold"})
    assert first_image_response.code == 200
    print first_image_response.body
    training_set_id = first_image_response.body['id']
    second_image_response = unirest.post(hostname + '/enroll-image/',
        params={"image": open("./arnold.jpg", mode="r"), "label":"Arnold", "training_set_id":training_set_id})
    assert second_image_response.code == 200
    print second_image_response.body
    #check training set
    training_set_response = unirest.get(hostname + '/trainingset/' + training_set_id)
    print training_set_response.body
    face_images = training_set_response.body['face_images']
    assert len(face_images) == 2
    response = unirest.post(hostname + '/compile-training-set/',
        params={"training_set_id":training_set_id})
    print response.body
    assert response.code == 200


def test_predict_recognition():
    set_unirest_defaults()
    first_image_response = unirest.post(hostname + '/enroll-image/',
        params={"image": open("./arnold.jpg", mode="r"), "label":"Arnold Schwarzenegger"})
    print first_image_response.body
    assert first_image_response.code == 200
    training_set_id = first_image_response.body['id']
    second_image_response = unirest.post(hostname + '/enroll-image/',
        params={"image_url": "http://images.politico.com/global/click/101103_schwarznegger_face_ap_392_regular.jpg", "label":"Arnold Schwarzenegger", "training_set_id":training_set_id})
    assert second_image_response.code == 200
    print second_image_response.body
    third_image_response = unirest.post(hostname + '/enroll-image/',
        params={"image_url": "http://www.theepochtimes.com/n2/images/stories/large/2011/02/08/72460251.jpg", 
        "label":"Donald Rumsfeld", "training_set_id":training_set_id})
    assert third_image_response.code == 200
    #check training set
    training_set_response = unirest.get(hostname + '/trainingset/' + training_set_id)
    print training_set_response.body
    face_images = training_set_response.body['face_images']
    assert len(face_images) == 3
    response = unirest.post(hostname + '/compile-training-set/',
        params={"training_set_id":training_set_id})
    print response.body
    predictive_model_id = response.body['id']
    time.sleep(MODEL_COMPILATION_SECONDS)
    prediction_response = unirest.post(hostname + '/recognize-face/',
        params={"predictive_model_id":predictive_model_id, "image_url":"http://img1.wikia.nocookie.net/__cb20130930223832/armoredheroes/images/3/37/Arnold_Schwarzenegger.jpg"})
    print prediction_response.body
    assert prediction_response.code == 200
    assert prediction_response.body['person']['name'] == "Arnold Schwarzenegger"
'''
'''
def test_predict_recognition():
    assert 1==1

# --- REST TESTING ---

def test_get_persons():
    assert 1==1

def update_persons():
    assert 1==1

def delete_persons():
    assert 1==1

def create_persons():
    assert 1==1
'''
'''
# --- PERMISSIONS TESTING ---

def test_not_your_objects():
    first_image_response = unirest.post(hostname + '/enroll-image/',
        params={"image": open("./arnold.jpg", mode="r"), "label":"Arnold Schwarzenegger"})
    assert first_image_response.code == 200
    training_set_id = first_image_response.body['id']
    training_set_response = unirest.get(hostname + '/trainingset/' + training_set_id + '/')
    assert training_set_response.code == 200
    unirest.clear_default_headers()
    random_username = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    permissions_response = unirest.get(hostname + '/trainingset/' + training_set_id + '/',
        headers={"X-Mashape-User":random_username, "X-Mashape-Proxy-Secret":"DEBUG"})
    print permissions_response.code
    print permissions_response.body
    assert permissions_response.code != 200

# --- PUBLIC DATA TESTING ---
'''
'''
def recognize_celeb():
    assert 1==1

def headless_recognize():
    assert 1==1
'''





