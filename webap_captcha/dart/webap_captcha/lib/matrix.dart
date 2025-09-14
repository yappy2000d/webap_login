class Matrix<T> {
  final List<List<T>> _data;

  Matrix(this._data) {
    if (_data.isEmpty ||
        _data.any((List<T> row) => row.length != _data[0].length)) {
      throw ArgumentError(
        'All rows must have the same length and matrix cannot be empty.',
      );
    }
  }

  // 2D constructor
  Matrix.fromDimensions(int width, int height, T initialValue)
    : _data = List<List<T>>.generate(
        height,
        (_) => List<T>.filled(width, initialValue),
      );

  // Construct from 2D list
  Matrix.fromList(List<List<T>> data) : _data = data {
    if (data.isEmpty ||
        data.any((List<T> row) => row.length != data[0].length)) {
      throw ArgumentError(
        'All rows must have the same length and matrix cannot be empty.',
      );
    }
  }

  int get width => _data[0].length;
  int get height => _data.length;

  T get(int x, int y) => _data[y][x];
  void set(int x, int y, T value) {
    _data[y][x] = value;
  }

  Matrix<T> clone() {
    return Matrix<T>(_data.map((List<T> row) => List<T>.from(row)).toList());
  }

  Matrix<bool> notEqualMask(T value) {
    final Matrix<bool> result = Matrix<bool>.fromDimensions(
      width,
      height,
      false,
    );
    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        result.set(x, y, _data[y][x] != value);
      }
    }
    return result;
  }

  @override
  String toString() {
    return _data.map((List<T> row) => row.join(' ')).join('\n');
  }
}

extension MatrixIntExtensions on Matrix<int> {
  int max() {
    int maxValue = _data[0][0];
    for (final List<int> row in _data) {
      for (final int value in row) {
        if (value > maxValue) {
          maxValue = value;
        }
      }
    }
    return maxValue;
  }

  List<int> unique() {
    final Set<int> values = <int>{};
    for (final List<int> row in _data) {
      values.addAll(row);
    }
    return values.toList();
  }
}
