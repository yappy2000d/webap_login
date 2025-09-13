import 'matrix.dart';

/// Connected-component labeling
/// Labels the connected components of a binary image.
///
/// Parameters:
/// - [a]: A 2D binary matrix where non-background pixels are considered foreground.
/// - [structure]: A 2D binary matrix defining the connectivity. If null, defaults to 4-connectivity.
/// - [background]: The pixel value representing the background. Defaults to 0.
///
/// Returns:
/// - A record containing:
///   - The labeled image as a matrix of integers, where each connected component is assigned a
///    unique integer label starting from 1. Background pixels are labeled with 0.
///   - The number of connected components found in the image.
(Matrix<int>, int) label(
  Matrix<int> a, {
  Matrix? structure,
  int? background = 0,
}) {
  // Validate input image
  if (a.width == 0 || a.height == 0) {
    throw ArgumentError('Cannot label an empty image.');
  }

  final foreground = a.notEqualMask(background!);

  // Construct footprint
  // Default to 4-connectivity
  structure ??= Matrix.fromList([
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0],
  ]);

  final neighborOffsets = _computeCausalNeighborOffsets(structure);

  final labels = Matrix<int>.fromDimensions(a.width, a.height, 0);

  // Union-Find data structure
  final parent = <int>[];
  final rank = <int>[];

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

    while (parent[x] != x) {
      final next = parent[x];
      parent[x] = root;
      x = next;
    }
    return root;
  }

  int ufUnion(int x, int y) {
    final rootX = ufFind(x);
    final rootY = ufFind(y);
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

      final neighborLabels = <int>{};

      for (final offset in neighborOffsets) {
        final nx = x + offset[0];
        final ny = y + offset[1];
        if (nx >= 0 && nx < a.width && ny >= 0 && ny < a.height) {
          final neighborLabel = labels.get(nx, ny);
          if (neighborLabel > 0) {
            neighborLabels.add(neighborLabel);
          }
        }
      }

      if (neighborLabels.isEmpty) {
        // New component
        final newLabel = ufMake() + 1; // Labels start from 1
        labels.set(x, y, newLabel);
      } else {
        // Assign the smallest label among neighbors
        final minLabel = neighborLabels.reduce((a, b) => a < b ? a : b);
        labels.set(x, y, minLabel);

        // Union all neighbor labels
        for (final nl in neighborLabels) {
          ufUnion(minLabel - 1, nl - 1); // Convert to zero-based index
        }
      }
    }
  }

  // Second pass
  if (labels.max() == 0) return (labels, 0);


  final used = labels.unique();
  used.remove(0); // Remove background (label 0)

  final roots = <int, int>{};
  for (final label in used) {
    final root = ufFind(label - 1); // Convert to zero-based index
    roots[label] = root;
  }

  // Relabeling
  final rootSet = <int>[];
  final seen = <int>{};
  for (final lab in used) {
    final r = roots[lab]!;
    if (!seen.contains(r)) {
      seen.add(r);
      rootSet.add(r);
    }
  }
  rootSet.sort();

  final rootToCompact = <int, int>{};
  for (int i = 0; i < rootSet.length; i++) {
    rootToCompact[rootSet[i]] = i + 1; // Compact labels start from 1
  }

  final labToCompact = <int, int>{};
  for (final lab in used) {
    final r = roots[lab]!;
    labToCompact[lab] = rootToCompact[r]!;
  }

  final maxLab = labels.max();
  final lut = List<int>.filled(maxLab + 1, 0);
  for (final entry in labToCompact.entries) {
    lut[entry.key] = entry.value;
  }

  // Apply LUT
  final mask = labels.notEqualMask(0);
  for (int y = 0; y < a.height; y++) {
    for (int x = 0; x < a.width; x++) {
      if (mask.get(x, y)) {
        final oldLabel = labels.get(x, y);
        labels.set(x, y, lut[oldLabel]);
      }
    }
  }

  return (labels, rootSet.length);
}

List<List<int>> _computeCausalNeighborOffsets(Matrix structure) {
  final offsets = <List<int>>[];
  final centerX = structure.width ~/ 2;
  final centerY = structure.height ~/ 2;

  for (int y = 0; y < structure.height; y++) {
    for (int x = 0; x < structure.width; x++) {
      if (structure.get(x, y) == 0) continue;

      // Only consider neighbors above and to the left of the center
      if (y < centerY || (y == centerY && x < centerX)) {
        offsets.add([x - centerX, y - centerY]);
      }
    }
  }

  return offsets;
}
