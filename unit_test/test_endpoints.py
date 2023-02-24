import pytest #유닛 테스트를 위해 Pytest를 import 한다.
import bcrypt
import json
import config

from app import create_app #미니터 api 소스 코드 파일인 app.py에서 create_app 함수를 import 한다.
from sqlalchemy import create_engine, text

database = create_engine(config.test_config['DB_URL'], encoding= 'utf-8', max_overflow = 0) #유닛 테스트를 위한 테스트 DB를 연결한다.

@pytest.fixture #데코레이터를 적용한다. fixture decorator가 적용된 함수와 같은 이름의 인자가 다른 test함수에 지정되어 있으면 pytest가 알아서 같은 이름의 함수의 리턴값을 해당 인자에 넣어준다.
def api():
    app = create_app(config.test_config)
    app.config['TESTING'] = True #Flask에서 에러가 발생 시, HTTP 요청 오류 부분은 핸들링하지 않는다.
    api = app.test_client() #test_client 함수를 호출하여 테스트용 클라이언트를 생성한다. 이를 이용해 URL기반으로 원하는 엔드포인트 호출이 가능하다.

    return api #호출한 test_client를 리턴해준다.
def setup_function():
    ## Create a test user
    hashed_password = bcrypt.hashpw(
        b"test password",
        bcrypt.gensalt()
    )
    new_users = [
        {
            'id'              : 1,
            'name'            : '송은우',
            'email'           : 'songew@gmail.com',
            'profile'         : 'test profile',
            'hashed_password' : hashed_password
        }, {
            'id'              : 2,
            'name'            : '김철수',
            'email'           : 'tet@gmail.com',
            'profile'         : 'test profile',
            'hashed_password' : hashed_password
        }
    ]
    database.execute(text("""
        INSERT INTO users (
            id,
            name,
            email,
            profile,
            hashed_password
        ) VALUES (
            :id,
            :name,
            :email,
            :profile,
            :hashed_password
        )
    """), new_users)
    
    ## User 2 의 트윗 미리 생성해 놓기
    database.execute(text("""
        INSERT INTO tweets (
            user_id,
            tweet
        ) VALUES (
            2,
            "Hello World!"
        )
    """))
'''
가장 중요한 것이, 유닛 테스트를 진행하고 난 후 생성된 사용자나 트윗은 지워주어야 하는데, 이를 매번 하기는 번거롭다. 그래서 Unit Test가 끝날때마다 실행되는 teardown_function()에
사용자, 트윗, 팔로우 리스트를 지우는 코드를 작성한다.
TRUNCATE는 해당 값을 지운다.
'''

def teardown_function(): 
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))

def test_ping(api):
    resp = api.get('/ping')#HTTP GET함수를 이용해 해당 값을 테스트한다.
    assert b'pong' in resp.data

def test_login(api):
    resp = api.post( #HTTP POST함수를 이용해 단위 테스트 진행
        '/login',
        data         = json.dumps({'email' : 'songew@gmail.com', 'password' : 'test password'}),
        content_type = 'application/json'
    )
    assert b"access_token" in resp.data #ACCESS TOKEN 확인
    
def test_unauthorized(api):
    # access token이 없이는 401 응답을 리턴하는지를 확인
    resp = api.post(
        '/tweet', 
        data         = json.dumps({'tweet' : "Hello World!"}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401

    resp  = api.post(
        '/follow',
        data         = json.dumps({'follow' : 2}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401

    resp  = api.post(
        '/unfollow',
        data         = json.dumps({'unfollow' : 2}),
        content_type = 'application/json'
    )
    assert resp.status_code == 401

#밑 함수들은 위에 함수들과 다르게 사전에 실행되어야 하는 함수들이 존재한다. (Ex: Tweet을 위해선 Login을 해야함)

def test_tweet(api):
    ## 로그인
    resp = api.post(
        '/login',
        data         = json.dumps({'email' : 'songew@gmail.com', 'password' : 'test password'}),
        content_type = 'application/json'
    )
    resp_json    = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    ## tweet
    resp = api.post(
        '/tweet', 
        data         = json.dumps({'tweet' : "Hello World!"}),
        content_type = 'application/json',
        headers      = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    ## tweet 확인
    resp   = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets           == { 
        'user_id'  : 1, 
        'timeline' : [
            {
                'user_id' : 1,
                'tweet'   : "Hello World!"
            }
        ]
    }

def test_follow(api):
    # 로그인
    resp = api.post(
        '/login',
        data         = json.dumps({'email' : 'songew@gmail.com', 'password' : 'test password'}),
        content_type = 'application/json'
    )
    resp_json    = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    ## 먼저 유저 1의 tweet 확인 해서 tweet 리스트가 비어 있는것을 확인
    resp   = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets           == {
        'user_id'  : 1,
        'timeline' : [ ]
    }

    # follow 유저 아이디 = 2
    resp  = api.post(
        '/follow',
        data         = json.dumps({'follow' : 2}),
        content_type = 'application/json',
        headers      = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    ## 이제 유저 1의 tweet 확인 해서 유저 2의 tweet의 리턴 되는것을 확인
    resp   = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets           == {
        'user_id' : 1,
        'timeline' : [
            {
                'user_id' : 2,
                'tweet'   : "Hello World!"
            }
        ]
    }

def test_unfollow(api):
    # 로그인
    resp = api.post(
        '/login',
        data         = json.dumps({'email' : 'songew@gmail.com', 'password' : 'test password'}),
        content_type = 'application/json'
    )
    resp_json    = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    # follow 유저 아이디 = 2
    resp  = api.post(
        '/follow',
        data         = json.dumps({'follow' : 2}),
        content_type = 'application/json',
        headers      = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

    ## 이제 유저 1의 tweet 확인 해서 유저 2의 tweet의 리턴 되는것을 확인
    resp   = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets           == {
        'user_id'  : 1,
        'timeline' : [
            {
                'user_id' : 2,
                'tweet'   : "Hello World!"
            }
        ]
    }

    # unfollow 유저 아이디 = 2
    resp  = api.post(
        '/unfollow',
        data         = json.dumps({'unfollow' : 2}),
        content_type = 'application/json',
        headers      = {'Authorization' : access_token}
    )
    assert resp.status_code == 200

     ## 이제 유저 1의 tweet 확인 해서 유저 2의 tweet이 더 이상 리턴 되지 않는 것을 확인
    resp   = api.get(f'/timeline/1')
    tweets = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == 200
    assert tweets           == {
        'user_id'  : 1,
        'timeline' : [ ]
    }
