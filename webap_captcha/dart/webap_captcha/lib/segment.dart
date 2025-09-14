import 'matrix.dart';

/// Connected-component labeling
/// Labels the connected components of a binary image.
///
/// Parameters:
/// - [a]: A 2D binary matrix.
/// - [structure]: A 2D binary matrix defining the connectivity. defaults to 4-connectivity.
/// - [background]: The pixel value representing the background. Defaults to 0.
///
/// Returns:
/// - A record containing:
///   - The labeled image as a matrix of integers, where each connected component is assigned a
///    unique integer label starting from 1. Background pixels are labeled with 0.
///   - The number of connected components found in the image.
(Matrix<int>, int) label(
  Matrix<int> a, {
  Matrix<int>? structure,
  int? background = 0,
}) {
  // Validate input image
  if (a.width == 0 || a.height == 0) {
    throw ArgumentError('Cannot label an empty image.');
  }

  final Matrix<bool> foreground = a.notEqualMask(background!);

  // Construct footprint
  // Default to 4-connectivity
  structure ??= Matrix<int>.fromList(<List<int>>[
    <int>[0, 1, 0],
    <int>[1, 1, 1],
    <int>[0, 1, 0],
  ]);

  final List<List<int>> neighborOffsets =
      _computeCausalNeighborOffsets(structure);

  final Matrix<int> labels = Matrix<int>.fromDimensions(a.width, a.height, 0);

  // Union-Find data structure
  final List<int> parent = <int>[];
  final List<int> rank = <int>[];

  int ufMake() {
    parent.add(parent.length);
    rank.add(0);
    return parent.length - 1;
  }

  /// Path compression
  int ufFind(int x) {
    int root = x;
    while (parent[root] != root) {
      root = parent[root];
    }

    int curr = x;
    while (parent[curr] != curr) {
      final int next = parent[curr];
      parent[curr] = root;
      curr = next;
    }
    return root;
  }

  int ufUnion(int x, int y) {
    final int rootX = ufFind(x);
    final int rootY = ufFind(y);
    if (rootX == rootY) return rootX;
    if (rank[rootX] < rank[rootY]) {
      parent[rootX] = rootY;
      return rootY;
    } else if (rank[rootX] > rank[rootY]) {
      parent[rootY] = rootX;
      return rootX;
    } else {
      parent[rootY] = rootX;
      rank[rootX]++;
      return rootX;
    }
  }

  // First pass
  for (int y = 0; y < a.height; y++) {
    for (int x = 0; x < a.width; x++) {
      if (!foreground.get(x, y)) continue;

      final Set<int> neighborLabels = <int>{};

      for (final List<int> offset in neighborOffsets) {
        final int nx = x + offset[0];
        final int ny = y + offset[1];
        if (nx >= 0 && nx < a.width && ny >= 0 && ny < a.height) {
          final int neighborLabel = labels.get(nx, ny);
          if (neighborLabel > 0) {
            neighborLabels.add(neighborLabel);
          }
        }
      }

      if (neighborLabels.isEmpty) {
        // New component
        final int newLabel = ufMake() + 1; // Labels start from 1
        labels.set(x, y, newLabel);
      } else {
        // Assign the smallest label among neighbors
        final int minLabel =
            neighborLabels.reduce((int a, int b) => a < b ? a : b);
        labels.set(x, y, minLabel);

        // Union all neighbor labels
        for (final int nl in neighborLabels) {
          ufUnion(minLabel - 1, nl - 1); // Convert to zero-based index
        }
      }
    }
  }

  // Second pass
  if (labels.max() == 0) return (labels, 0);

  final List<int> used = labels.unique();
  used.remove(0); // Remove background (label 0)

  final Map<int, int> roots = <int, int>{};
  for (final int label in used) {
    final int root = ufFind(label - 1); // Convert to zero-based index
    roots[label] = root;
  }

  // Relabeling
  final List<int> rootSet = <int>[];
  final Set<int> seen = <int>{};
  for (final int lab in used) {
    final int r = roots[lab]!;
    if (!seen.contains(r)) {
      seen.add(r);
      rootSet.add(r);
    }
  }
  rootSet.sort();

  final Map<int, int> rootToCompact = <int, int>{};
  for (int i = 0; i < rootSet.length; i++) {
    rootToCompact[rootSet[i]] = i + 1; // Compact labels start from 1
  }

  final Map<int, int> labToCompact = <int, int>{};
  for (final int lab in used) {
    final int r = roots[lab]!;
    labToCompact[lab] = rootToCompact[r]!;
  }

  final int maxLab = labels.max();
  final List<int> lut = List<int>.filled(maxLab + 1, 0);
  for (final MapEntry<int, int> entry in labToCompact.entries) {
    lut[entry.key] = entry.value;
  }

  // Apply LUT
  final Matrix<bool> mask = labels.notEqualMask(0);
  for (int y = 0; y < a.height; y++) {
    for (int x = 0; x < a.width; x++) {
      if (mask.get(x, y)) {
        final int oldLabel = labels.get(x, y);
        labels.set(x, y, lut[oldLabel]);
      }
    }
  }

  return (labels, rootSet.length);
}

List<List<int>> _computeCausalNeighborOffsets(Matrix structure) {
  final List<List<int>> offsets = <List<int>>[];
  final int centerX = structure.width ~/ 2;
  final int centerY = structure.height ~/ 2;

  for (int y = 0; y < structure.height; y++) {
    for (int x = 0; x < structure.width; x++) {
      if (structure.get(x, y) == 0) continue;

      // Only consider neighbors above and to the left of the center
      if (y < centerY || (y == centerY && x < centerX)) {
        offsets.add(<int>[x - centerX, y - centerY]);
      }
    }
  }

  return offsets;
}
