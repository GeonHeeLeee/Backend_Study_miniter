import hashlib
#단방향 암호화를 해주는 hashlib

m = hashlib.sha256()
m.update(b"test password") #바이트 단위로 받기 떄문에 앞에 b를 붙여준다.
m.hexdigest()  # >>> '0b47c69b1033498d5f33f5f7d97bb6a3126134751629f4d0185c115db44c094e'
