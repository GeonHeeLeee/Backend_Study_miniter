def multiply_by_two(x): 
    return x * 2

def test_multiply_by_two(): #test_로 시작하는 함수만 테스트 함수로 인식한다. 또한 파일명도 test_로 시작하여야한다.
	assert multiply_by_two(4) == 8
	#만약 오류가 나면 AssertionError를 throw한다.
