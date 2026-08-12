import json


# 읽어올 데이터 파일 이름이다. 바뀔 일이 없으므로 여기에 고정해 둔다.
DATA_FILE = 'data.json'


# ---------------------------------------------------------------
# JSON 파일 읽기
# ---------------------------------------------------------------

def load_json_data():
    # DATA_FILE 을 읽어서 파이썬 딕셔너리로 돌려준다.
    with open(DATA_FILE, 'r', encoding='utf-8') as data_file:
        data = json.load(data_file)
    return data


# ---------------------------------------------------------------
# 라벨 정규화 (프로그램 안에서는 항상 'Cross' 와 'X' 만 사용한다)
# ---------------------------------------------------------------

def normalize_filter_key(key):
    # data.json 의 필터 키를 표준 라벨로 바꾼다.
    if key == 'cross':
        return 'Cross'
    if key == 'x':
        return 'X'
    return None


def normalize_expected(value):
    # data.json 의 expected 값을 표준 라벨로 바꾼다.
    if value == '+':
        return 'Cross'
    if value == 'x':
        return 'X'
    return None


def get_size_from_key(key):
    # 'size_5_1' 같은 이름에서 5 를 꺼낸다.
    parts = key.split('_')
    if len(parts) < 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


# ---------------------------------------------------------------
# 필터 읽어오기
# ---------------------------------------------------------------

def load_filters(data):
    # 필터를 읽어서 표준 라벨로 바꿔 저장한다.
    #
    # 돌려주는 값 : (filters, messages)
    #   filters  : { 5: {'Cross': [[...]], 'X': [[...]]}, 13: {...} }
    #   messages : 화면에 보여줄 안내 문구 목록
    #
    # 화면 출력은 main.py 가 담당하므로 여기서는 문구만 모아서 돌려준다.
    filters = {}
    messages = []

    raw_filters = data.get('filters', {})

    for filter_key in raw_filters:
        size = get_size_from_key(filter_key)
        if size is None:
            messages.append('필터 이름을 알 수 없어 건너뜁니다. (' + filter_key + ')')
            continue

        one_filter = {}
        for label_key in raw_filters[filter_key]:
            label = normalize_filter_key(label_key)
            if label is None:
                messages.append('알 수 없는 필터 라벨이라 건너뜁니다. (' + label_key + ')')
                continue
            one_filter[label] = raw_filters[filter_key][label_key]

        if 'Cross' in one_filter and 'X' in one_filter:
            filters[size] = one_filter
            messages.append('size_' + str(size) + ' 필터 로드 완료 (Cross, X)')
        else:
            messages.append('size_' + str(size) + ' 필터에 Cross 또는 X 가 없어 건너뜁니다.')

    return filters, messages


# ---------------------------------------------------------------
# 패턴 읽어오기
# ---------------------------------------------------------------

def make_pattern_record(name, pattern_data):
    # 패턴 하나를 읽어서 검사하고 표준 라벨로 바꾼다.
    #
    # 돌려주는 값 (딕셔너리)
    #   name     : 'size_5_1' 같은 이름
    #   size     : 5 (이름에서 꺼낸 크기)
    #   input    : 2차원 배열
    #   expected : 'Cross' 또는 'X'
    #   error    : 문제가 있으면 그 이유, 없으면 빈 문자열
    record = {}
    record['name'] = name
    record['size'] = get_size_from_key(name)
    record['input'] = None
    record['expected'] = None
    record['error'] = ''

    # 1) 필요한 항목이 있는지 확인한다.
    if 'input' not in pattern_data or 'expected' not in pattern_data:
        record['error'] = 'input 또는 expected 항목이 없습니다.'
        return record

    # 2) 이름에서 크기를 읽을 수 있는지 확인한다.
    if record['size'] is None:
        record['error'] = '패턴 이름에서 크기를 읽을 수 없습니다.'
        return record

    # 3) expected 를 표준 라벨로 바꾼다.
    expected = normalize_expected(pattern_data['expected'])
    if expected is None:
        record['error'] = '알 수 없는 expected 값입니다. (' + str(pattern_data['expected']) + ')'
        return record

    record['input'] = pattern_data['input']
    record['expected'] = expected
    return record


def load_patterns(data):
    # 모든 패턴을 읽어서 크기가 작은 것부터 정렬한 목록으로 돌려준다.
    raw_patterns = data.get('patterns', {})

    # (크기, 이름) 짝으로 만들어 정렬한다. 크기를 못 읽으면 맨 앞에 둔다.
    order = []
    for name in raw_patterns:
        size = get_size_from_key(name)
        if size is None:
            size = 0
        order.append((size, name))
    order.sort()

    records = []
    for item in order:
        name = item[1]
        records.append(make_pattern_record(name, raw_patterns[name]))

    return records
