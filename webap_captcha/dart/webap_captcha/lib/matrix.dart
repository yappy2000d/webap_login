class Matrix<T> {
  final List<List<T>> _data;

  Matrix(this._data) {
    if (_data.isEmpty || _data.any((row) => row.length != _data[0].length)) {
      throw ArgumentError(
        'All rows must have the same length and matrix cannot be empty.',
      );
    }
  }

  // 2D constructor
  Matrix.fromDimensions(int width, int height, T initialValue)
    : _data = List.generate(height, (_) => List.filled(width, initialValue));

  // Construct from 2D list
  Matrix.fromList(List<List<T>> data) : _data = data {
    if (data.isEmpty || data.any((row) => row.length != data[0].length)) {
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

  Matrix clone() {
    return Matrix(_data.map((row) => List<T>.from(row)).toList());
  }

  Matrix<bool> notEqualMask(T value) {
    Matrix<bool> result = Matrix<bool>.fromDimensions(width, height, false);
    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        result.set(x, y, _data[y][x] != value);
      }
    }
    return result;
  }

  @override
  String toString() {
    return _data.map((row) => row.join(' ')).join('\n');
  }
}

extension MatrixIntExtensions on Matrix<int> {
  int max() {
    int maxValue = _data[0][0];
    for (var row in _data) {
      for (var value in row) {
        if (value > maxValue) {
          maxValue = value;
        }
      }
    }
    return maxValue;
  }

  List<int> unique() {
    final values = <int>{};
    for (var row in _data) {
      values.addAll(row);
    }
    return values.toList();
  }
}
