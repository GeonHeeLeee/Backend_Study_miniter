from functools import wraps 

def test_decorator(f): 
    @wraps(f) 
    def decorated_function(*args, **kwargs): #가능한 모든 인자를 받기 위해 *args, **kwargs
        print("Decorated Function")
        return f(*args, **kwargs)

    return decorated_function

@test_decorator #데코레이터 함수 지정하는 법
def func():
    print("Calling func function")

#이렇게 코드를 작성 시 실행순서는 
# decorated_fucntion > func 순으로 실행된다.
