db = {
    'user'     : 'root', #database에 접속할 사용자 아이디
    'password' : 'test1234', #사용자 비밀번호
    'host'     : 'localhost', #접속할 데이터베이스의 주소. 현재 컴퓨터에 설치되어 있는 데이터베이스이므로 localhost. 만일 외부 데이터베이스면 주소를 입력해야된다.
    'port'     : 3306, #관계형 데이터베이스는 주로 3306 포트를 통해 연결된다.
    'database' : 'miniter' #실제 사용할 데이터베이스 이름이다.
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
#user, password, host, port, database 등의 변수는 위에 정의한 내용이다.
