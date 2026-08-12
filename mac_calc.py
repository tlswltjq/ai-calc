import time

# 성능 측정을 몇 번 반복할지 정한다.
REPEAT_COUNT = 10


class MacCalc:
    def check_size(pattern, filter):
        # 패턴과 필터의 모양이 같은지 확인한다.
        # 2차원 방식과 1차원 방식이 똑같은 기준으로 검사하도록 한곳에 모아 둔다.

        # 1) 행 개수가 같은지 확인한다.
        if len(pattern) != len(filter):
            message = '크기 불일치: 행 개수가 다릅니다. (패턴 '
            message = message + str(len(pattern))
            message = message + ', 필터 ' + str(len(filter)) + ')'
            raise ValueError(message)

        # 2) 각 행의 열 개수가 같은지 확인한다.
        for row in range(len(pattern)):
            if len(pattern[row]) != len(filter[row]):
                message = '크기 불일치: ' + str(row) + '번째 행의 열 개수가 다릅니다. (패턴 '
                message = message + str(len(pattern[row]))
                message = message + ', 필터 ' + str(len(filter[row])) + ')'
                raise ValueError(message)

    def calculate_2d_array(pattern, filter):
        # 패턴과 필터의 같은 위치에 있는 값을 곱해서 전부 더한다. (MAC 연산)
        # 외부 라이브러리 없이 반복문으로만 계산한다.
        MacCalc.check_size(pattern, filter)

        total = 0.0

        # 한 행씩 내려가면서 곱하고(Multiply) 더한다(Accumulate).
        for row in range(len(pattern)):
            for col in range(len(pattern[row])):
                total = total + pattern[row][col] * filter[row][col]

        return total

    def measure_time_2d_array(pattern, filter):
        # MAC 연산만 REPEAT_COUNT 번 반복해서 평균 시간(ms)을 구한다.
        # 입력받기, 파일 읽기, 화면 출력 시간은 재지 않는다.
        start = time.perf_counter()

        for i in range(REPEAT_COUNT):
            MacCalc.calculate_2d_array(pattern, filter)

        end = time.perf_counter()

        # 초 단위를 ms 로 바꾸고 반복 횟수로 나눠 평균을 낸다.
        return (end - start) * 1000 / REPEAT_COUNT

    # -----------------------------------------------------------
    # 보너스 : 1차원 배열 방식
    #
    # 2차원 배열은 값 하나를 꺼낼 때마다 pattern[row] 로 행 목록을 찾고
    # 다시 [col] 로 값을 찾는, 두 단계를 거친다.
    # 미리 한 줄로 펴 두면 flat[i] 한 단계로 끝나고 안쪽 반복문도 사라져서
    # 같은 결과를 더 적은 일로 얻을 수 있다.
    # -----------------------------------------------------------

    def flatten_2d_array(matrix):
        # 2차원 배열을 위에서부터 한 행씩 이어 붙여 1차원 배열로 만든다.
        # 예) [[1, 2], [3, 4]] -> [1, 2, 3, 4]
        flat = []

        for row in range(len(matrix)):
            for col in range(len(matrix[row])):
                flat.append(matrix[row][col])

        return flat

    def calculate_flat_array(flat_pattern, flat_filter):
        # 이미 1차원으로 펴 둔 두 배열로 MAC 연산을 한다. 반복문이 하나뿐이다.
        if len(flat_pattern) != len(flat_filter):
            message = '크기 불일치: 값 개수가 다릅니다. (패턴 '
            message = message + str(len(flat_pattern))
            message = message + ', 필터 ' + str(len(flat_filter)) + ')'
            raise ValueError(message)

        total = 0.0

        for i in range(len(flat_pattern)):
            total = total + flat_pattern[i] * flat_filter[i]

        return total

    def calculate_1d_array(pattern, filter):
        # 2차원 패턴과 필터를 1차원으로 편 뒤 MAC 연산을 한다.
        # 받는 값과 돌려주는 값이 calculate_2d_array 와 똑같아서 그대로 바꿔 쓸 수 있다.

        # 1차원으로 펴면 행 구분이 사라진다.
        # 예를 들어 2x3 과 3x2 는 둘 다 값이 6개라서 그냥 펴면 오류를 놓친다.
        # 그래서 펴기 전에 2차원 방식과 같은 기준으로 모양을 먼저 확인한다.
        MacCalc.check_size(pattern, filter)

        flat_pattern = MacCalc.flatten_2d_array(pattern)
        flat_filter = MacCalc.flatten_2d_array(filter)

        return MacCalc.calculate_flat_array(flat_pattern, flat_filter)

    def measure_time_1d_array(pattern, filter):
        # 1차원 방식의 평균 시간(ms)을 구한다.
        # 2차원 방식과 같은 REPEAT_COUNT, 같은 방법으로 재야 비교가 된다.
        #
        # 1차원으로 펴는 일은 계산을 시작하기 전에 한 번만 하면 되는 준비 작업이라
        # 파일 읽기와 마찬가지로 측정 대상에서 뺀다.
        # 재는 것은 양쪽 모두 'MAC 연산에 걸리는 시간' 하나다.
        MacCalc.check_size(pattern, filter)

        flat_pattern = MacCalc.flatten_2d_array(pattern)
        flat_filter = MacCalc.flatten_2d_array(filter)

        start = time.perf_counter()

        for i in range(REPEAT_COUNT):
            MacCalc.calculate_flat_array(flat_pattern, flat_filter)

        end = time.perf_counter()

        return (end - start) * 1000 / REPEAT_COUNT
