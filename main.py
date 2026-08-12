from mac_calc import MacCalc
from mac_calc import REPEAT_COUNT
from pattern_maker import PatternMaker
from data_loader import DATA_FILE
from data_loader import load_json_data
from data_loader import load_filters
from data_loader import load_patterns


# 두 점수의 차이가 이 값보다 작으면 같은 점수로 본다. (부동소수점 오차 때문)
EPSILON = 1e-9


# ---------------------------------------------------------------
# 공통으로 쓰는 함수들
# ---------------------------------------------------------------

def print_title(text):
    print('')
    print('#---------------------------------------')
    print('# ' + text)
    print('#---------------------------------------')


def format_number(value):
    # 0.0 처럼 소수점이 지저분하게 보이지 않도록 짧게 만든다.
    return '%g' % value


def print_matrix(matrix):
    for row in range(len(matrix)):
        line = ''
        for col in range(len(matrix[row])):
            line = line + format_number(matrix[row][col]) + ' '
        print('  ' + line.rstrip())


def judge(first_score, second_score, first_label, second_label):
    # 두 점수를 비교해서 이긴 쪽의 라벨을 돌려준다.
    # 차이가 아주 작으면 판정하지 않는다.
    # 라벨을 밖에서 받으므로 'Cross'/'X' 든 'A'/'B' 든 같은 규칙을 쓸 수 있다.
    if abs(first_score - second_score) < EPSILON:
        return 'UNDECIDED'
    if first_score > second_score:
        return first_label
    return second_label


# ---------------------------------------------------------------
# 모드 1 : 사용자 모드
#
# 패턴을 직접 입력할 수도 있고, 만들어서 쓸 수도 있다.
# 어느 쪽을 골라도 뒤쪽(MAC 결과 -> 성능 분석)은 똑같은 코드를 지난다.
# 그래서 두 갈래는 아래 setup 한 가지 모양으로만 결과를 넘긴다.
#
#   size          : 패턴 한 변의 길이
#   pattern       : 판정할 2차원 배열
#   first_filter  : 첫 번째 필터, second_filter : 두 번째 필터
#   first_label   : 첫 번째 라벨, second_label  : 두 번째 라벨
#   expected      : 정답을 아는 경우 그 라벨, 모르면 None
#   steps         : 이 갈래가 이미 써 버린 단계 번호 개수
# ---------------------------------------------------------------

def parse_line(line, size):
    # 한 줄을 숫자 목록으로 바꾼다. 형식이 틀리면 None 을 돌려준다.
    parts = line.split()

    if len(parts) != size:
        print('입력 형식 오류: 각 줄에 ' + str(size) + '개의 숫자를 공백으로 구분해 입력하세요.')
        return None

    row = []
    for part in parts:
        try:
            row.append(float(part))
        except ValueError:
            print('입력 형식 오류: 숫자가 아닌 값이 있습니다. (' + part + ')')
            return None
    return row


def input_matrix(title, size):
    # 형식이 맞을 때까지 계속 다시 입력받는다.
    while True:
        print(title)

        matrix = []
        for i in range(size):
            row = parse_line(input(), size)
            if row is None:
                break
            matrix.append(row)

        if len(matrix) == size:
            return matrix

        print('처음부터 다시 입력해 주세요.')
        print('')


def input_size():
    # 만들 패턴의 크기를 입력받는다.
    while True:
        text = input('크기 N 을 입력하세요 (1 이상): ').strip()
        try:
            size = int(text)
        except ValueError:
            print('입력 형식 오류: 숫자를 입력하세요. (' + text + ')')
            continue

        if size < 1:
            print('입력 형식 오류: 1 이상을 입력하세요.')
            continue

        return size


def input_shape():
    # 만들 패턴의 모양을 고르게 한다.
    while True:
        print('만들 패턴의 모양을 고르세요.')
        print('1. 십자가 (Cross)')
        print('2. X')

        choice = input('선택: ').strip()
        if choice == '1':
            return 'Cross'
        if choice == '2':
            return 'X'

        print('1 또는 2 를 입력하세요.')


def input_source():
    # 패턴을 직접 넣을지, 만들어 쓸지 고르게 한다.
    while True:
        print('')
        print('[입력 방식 선택]')
        print('1. 직접 입력 (3x3)')
        print('2. 패턴 자동 생성 (보너스)')

        choice = input('선택: ').strip()
        if choice == '1' or choice == '2':
            return choice

        print('1 또는 2 를 입력하세요.')


def build_setup_by_input():
    # 직접 입력 : 필터 두 개와 패턴을 3x3 으로 받는다.
    # 사용자가 넣은 필터라 어느 쪽이 정답인지 알 수 없으므로 expected 는 None 이다.
    size = 3

    print_title('[1] 필터 입력')
    first_filter = input_matrix('필터 A (3줄 입력, 공백 구분)', size)
    print('')
    second_filter = input_matrix('필터 B (3줄 입력, 공백 구분)', size)

    print('')
    print('저장된 필터 A')
    print_matrix(first_filter)
    print('저장된 필터 B')
    print_matrix(second_filter)

    print_title('[2] 패턴 입력')
    pattern = input_matrix('패턴 (3줄 입력, 공백 구분)', size)

    print('')
    print('저장된 패턴')
    print_matrix(pattern)

    setup = {}
    setup['size'] = size
    setup['pattern'] = pattern
    setup['first_filter'] = first_filter
    setup['second_filter'] = second_filter
    setup['first_label'] = 'A'
    setup['second_label'] = 'B'
    setup['expected'] = None
    setup['steps'] = 2
    return setup


def build_setup_by_generator():
    # 자동 생성 : 크기와 모양을 받아 십자가/X 필터와 패턴을 만든다.
    # 어떤 모양으로 만들었는지 알고 있으므로 그 모양이 곧 expected 가 된다.
    print_title('[1] 패턴 생성')

    size = input_size()
    print('')
    shape = input_shape()

    # 같은 메서드로 필터 두 개와 패턴 하나를 만든다.
    first_filter = PatternMaker.make_pattern(size, 'Cross')
    second_filter = PatternMaker.make_pattern(size, 'X')
    pattern = PatternMaker.make_pattern(size, shape)

    print('')
    print('만든 패턴 (' + shape + ', ' + str(size) + 'x' + str(size) + ')')
    if size <= 25:
        print_matrix(pattern)
    else:
        print('  너무 커서 화면 출력은 생략합니다.')

    setup = {}
    setup['size'] = size
    setup['pattern'] = pattern
    setup['first_filter'] = first_filter
    setup['second_filter'] = second_filter
    setup['first_label'] = 'Cross'
    setup['second_label'] = 'X'
    setup['expected'] = shape
    setup['steps'] = 1
    return setup


def print_setup_verdict(setup):
    # 두 필터로 MAC 연산을 하고 판정을 보여준다.
    first_score = MacCalc.calculate_2d_array(setup['pattern'], setup['first_filter'])
    second_score = MacCalc.calculate_2d_array(setup['pattern'], setup['second_filter'])

    print(setup['first_label'] + ' 점수: ' + repr(first_score))
    print(setup['second_label'] + ' 점수: ' + repr(second_score))

    verdict = judge(first_score, second_score, setup['first_label'], setup['second_label'])

    # 정답을 모르면 판정만 보여주고 끝낸다.
    if setup['expected'] is None:
        if verdict == 'UNDECIDED':
            print('판정: 판정 불가 (|A-B| < 1e-9)')
        else:
            print('판정: ' + verdict)
        return

    # 정답을 알면 맞았는지까지 보여준다.
    line = '판정: ' + verdict + ' | 만든 모양: ' + setup['expected']
    if verdict == setup['expected']:
        print(line + ' | PASS')
    else:
        print(line + ' | FAIL')


def print_setup_performance(setup):
    # 이 패턴 하나의 MAC 연산 시간을 재서 표로 보여준다.
    size = setup['size']
    label = str(size) + 'x' + str(size)
    average_time = MacCalc.measure_time_2d_array(setup['pattern'], setup['first_filter'])

    print('크기       평균 시간(ms)    연산 횟수')
    print('-------------------------------------')
    print('%-10s %-16.4f %d' % (label, average_time, size * size))


def run_user_mode():
    # 두 갈래 중 하나로 setup 을 만들고, 그 뒤는 한 길로 합친다.
    if input_source() == '1':
        setup = build_setup_by_input()
    else:
        setup = build_setup_by_generator()

    # 갈래마다 앞에서 쓴 단계 개수가 달라서 번호를 이어 붙인다.
    step = setup['steps']

    step = step + 1
    print_title('[' + str(step) + '] MAC 결과')
    print_setup_verdict(setup)

    step = step + 1
    print_title('[' + str(step) + '] 성능 분석 (평균/' + str(REPEAT_COUNT) + '회)')
    print_setup_performance(setup)


# ---------------------------------------------------------------
# 모드 2 : data.json 분석
# ---------------------------------------------------------------

def run_one_pattern(record, filters):
    # 패턴 하나를 판정하고 결과를 돌려준다.
    # record 는 data_loader 가 읽어서 정규화까지 끝낸 값이다.
    # 결과 모양 : {'name': ..., 'passed': True/False, 'reason': ...}
    result = {}
    result['name'] = record['name']
    result['passed'] = False
    result['reason'] = ''

    print('--- ' + record['name'] + ' ---')

    # 1) 읽어올 때 이미 문제가 발견된 패턴이면 여기서 끝낸다.
    if record['error'] != '':
        result['reason'] = record['error']
        print('FAIL (' + result['reason'] + ')')
        return result

    # 2) 크기에 맞는 필터가 있는지 확인한다.
    size = record['size']
    if size not in filters:
        result['reason'] = 'size_' + str(size) + ' 필터가 없습니다.'
        print('FAIL (' + result['reason'] + ')')
        return result

    # 3) MAC 연산을 한다. 크기가 다르면 프로그램을 멈추지 않고 이 케이스만 FAIL 처리한다.
    try:
        cross_score = MacCalc.calculate_2d_array(record['input'], filters[size]['Cross'])
        x_score = MacCalc.calculate_2d_array(record['input'], filters[size]['X'])
    except ValueError as error:
        result['reason'] = str(error)
        print('FAIL (' + result['reason'] + ')')
        return result

    # 4) 판정하고 expected 와 비교한다.
    expected = record['expected']
    verdict = judge(cross_score, x_score, 'Cross', 'X')

    print('Cross 점수: ' + repr(cross_score))
    print('X 점수: ' + repr(x_score))

    if verdict == expected:
        result['passed'] = True
        print('판정: ' + verdict + ' | expected: ' + expected + ' | PASS')
    elif verdict == 'UNDECIDED':
        result['reason'] = '동점(UNDECIDED) 처리 규칙에 따라 FAIL'
        print('판정: UNDECIDED | expected: ' + expected + ' | FAIL (' + result['reason'] + ')')
    else:
        result['reason'] = '판정(' + verdict + ')이 expected(' + expected + ')와 다릅니다.'
        print('판정: ' + verdict + ' | expected: ' + expected + ' | FAIL')

    return result


def find_pattern(pattern_records, size):
    # 그 크기의 패턴을 목록에서 찾는다. 없으면 None 을 돌려준다.
    for record in pattern_records:
        if record['size'] == size and record['input'] is not None:
            return record['input']
    return None


def print_performance(filters, pattern_records):
    # 크기별로 MAC 연산 시간을 재서 표로 보여준다.
    print('크기       평균 시간(ms)    연산 횟수')
    print('-------------------------------------')

    # 필터가 있는 크기를 작은 것부터 훑는다.
    sizes = []
    for size in filters:
        sizes.append(size)
    sizes.sort()

    for size in sizes:
        label = str(size) + 'x' + str(size)

        # 그 크기의 패턴을 data.json 에서 찾는다.
        pattern = find_pattern(pattern_records, size)
        if pattern is None:
            print('%-10s %s' % (label, '잴 패턴이 없어 건너뜁니다.'))
            continue

        try:
            average_time = MacCalc.measure_time_2d_array(pattern, filters[size]['Cross'])
        except ValueError as error:
            print('%-10s %s' % (label, '측정 실패 (' + str(error) + ')'))
            continue

        print('%-10s %-16.4f %d' % (label, average_time, size * size))


def print_summary(results):
    total = len(results)
    passed = 0
    for result in results:
        if result['passed']:
            passed = passed + 1
    failed = total - passed

    print('총 테스트: ' + str(total) + '개')
    print('통과: ' + str(passed) + '개')
    print('실패: ' + str(failed) + '개')

    if failed > 0:
        print('')
        print('실패 케이스:')
        for result in results:
            if not result['passed']:
                print('- ' + result['name'] + ': ' + result['reason'])


def run_json_mode():
    print_title('[1] 필터 로드')

    try:
        data = load_json_data()
    except FileNotFoundError:
        print(DATA_FILE + ' 파일을 찾을 수 없습니다.')
        return
    except ValueError:
        print(DATA_FILE + ' 파일의 형식이 올바르지 않습니다.')
        return

    filters, messages = load_filters(data)
    for message in messages:
        print(message)

    if len(filters) == 0:
        print('사용할 수 있는 필터가 없어 분석을 중단합니다.')
        return

    pattern_records = load_patterns(data)

    print_title('[2] 패턴 분석 (라벨 정규화 적용)')

    results = []
    for record in pattern_records:
        results.append(run_one_pattern(record, filters))

    print_title('[3] 성능 분석 (평균/' + str(REPEAT_COUNT) + '회)')
    print_performance(filters, pattern_records)

    print_title('[4] 결과 요약')
    print_summary(results)


# ---------------------------------------------------------------
# 시작 지점
# ---------------------------------------------------------------

def main():
    print('=== Mini NPU Simulator ===')
    print('')
    print('[모드 선택]')
    print('1. 사용자 모드 (직접 입력 / 패턴 자동 생성)')
    print('2. data.json 분석')

    while True:
        choice = input('선택: ').strip()
        if choice == '1':
            run_user_mode()
            return
        if choice == '2':
            run_json_mode()
            return
        print('1 또는 2 를 입력하세요.')


if __name__ == '__main__':
    main()
