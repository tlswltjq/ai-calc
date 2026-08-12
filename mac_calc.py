import time

# 성능 측정을 몇 번 반복할지 정한다.
REPEAT_COUNT = 10


class MacCalc:
    def calculate_2d_array(pattern, filter):
        # 패턴과 필터의 같은 위치에 있는 값을 곱해서 전부 더한다. (MAC 연산)
        # 외부 라이브러리 없이 반복문으로만 계산한다.

        # 1) 행 개수가 같은지 확인한다.
        if len(pattern) != len(filter):
            message = '크기 불일치: 행 개수가 다릅니다. (패턴 '
            message = message + str(len(pattern))
            message = message + ', 필터 ' + str(len(filter)) + ')'
            raise ValueError(message)

        total = 0.0

        # 2) 한 행씩 내려가면서 계산한다.
        for row in range(len(pattern)):

            # 2-1) 그 행의 열 개수가 같은지 확인한다.
            if len(pattern[row]) != len(filter[row]):
                message = '크기 불일치: ' + str(row) + '번째 행의 열 개수가 다릅니다. (패턴 '
                message = message + str(len(pattern[row]))
                message = message + ', 필터 ' + str(len(filter[row])) + ')'
                raise ValueError(message)

            # 2-2) 곱하고(Multiply) 더한다(Accumulate).
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
