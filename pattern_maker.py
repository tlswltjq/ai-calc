class PatternMaker:
    def make_pattern(size, shape):

        if size < 1:
            raise ValueError('크기는 1 이상이어야 합니다. (입력: ' + str(size) + ')')

        if shape != 'Cross' and shape != 'X':
            raise ValueError('모양은 Cross 또는 X 여야 합니다. (입력: ' + str(shape) + ')')

        matrix = []
        middle = size // 2

        for row in range(size):
            line = []
            for col in range(size):
                if shape == 'Cross':
                    filled = (row == middle or col == middle)
                else:
                    filled = (row == col or row + col == size - 1)

                if filled:
                    line.append(1.0)
                else:
                    line.append(0.0)

            matrix.append(line)

        return matrix
