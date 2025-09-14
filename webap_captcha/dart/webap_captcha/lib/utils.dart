import 'dart:io' show PathNotFoundException;

import 'package:image/image.dart' show Image, decodeBmpFile, getLuminance;

import 'matrix.dart';

/// Read an image from the given path.
/// Throws [PathNotFoundException] if the file is not found.
/// Throws [Exception] if there is an error reading the image.
Future<Matrix<int>> readImage(String path) async {
  Image? image;

  image = await decodeBmpFile(path);

  if (image == null) {
    throw Exception('Error reading image from $path');
  }

  return imageToMatrix(image);
}

Matrix<int> imageToMatrix(Image image) {
  final int width = image.width;
  final int height = image.height;

  return Matrix<int>.fromList(
    List<List<int>>.generate(
      height,
      (int y) => List<int>.generate(
        width,
        (int x) => getLuminance(image.getPixel(x, y)).toInt(),
      ),
    ),
  );
}

Matrix<int> binaryThreshold(Matrix<int> image, int threshold) {
  final Matrix<int> result = Matrix<int>.fromDimensions(
    image.width,
    image.height,
    0,
  );
  for (int y = 0; y < image.height; y++) {
    for (int x = 0; x < image.width; x++) {
      result.set(x, y, image.get(x, y) < threshold ? 255 : 0);
    }
  }
  return result;
}

Matrix<int> _cropAndPad(
  Matrix<int> labeledImage,
  int x,
  int y,
  int width,
  int height,
) {
  final Matrix<int> result = Matrix<int>.fromDimensions(width, height, 0);

  // Crop the image
  for (int j = 0; j < height; j++) {
    for (int i = 0; i < width; i++) {
      result.set(i, j, labeledImage.get(x + i, y + j));
    }
  }

  /// Add padding to make it square
  /// The final size is 22x22
  assert(width > 0 && height > 0 && width <= 22 && height <= 22);

  final Matrix<int> canvas = Matrix<int>.fromDimensions(22, 22, 0);
  final int offsetX = (22 - width) ~/ 2;
  final int offsetY = (22 - height) ~/ 2;
  for (int j = 0; j < height; j++) {
    for (int i = 0; i < width; i++) {
      canvas.set(offsetX + i, offsetY + j, result.get(i, j) > 0 ? 255 : 0);
    }
  }

  return canvas;
}

List<Matrix<int>?> cropImage(
  Matrix<int> labeledImage,
  int labelCount, {
  int bgColor = 0,
}) {
  final Map<int, (int, int, int, int)> bboxes =
      <int, (int, int, int, int)>{}; // label -> (minX, minY, maxX, maxY)
  for (int label = 1; label <= labelCount; label++) {
    int minX = labeledImage.width;
    int minY = labeledImage.height;
    int maxX = 0;
    int maxY = 0;

    for (int y = 0; y < labeledImage.height; y++) {
      for (int x = 0; x < labeledImage.width; x++) {
        if (labeledImage.get(x, y) == label) {
          if (x < minX) minX = x;
          if (x > maxX) maxX = x;
          if (y < minY) minY = y;
          if (y > maxY) maxY = y;
        }
      }
    }

    // filter out too small boxes
    if (maxX - minX < 5 || maxY - minY < 5) continue;
    bboxes[label] = (minX, minY, maxX, maxY);
  }

  // Sort bounding boxes by x coordinate
  final List<MapEntry<int, (int, int, int, int)>> sortedBboxes =
      bboxes.entries.toList()..sort(
        (
          MapEntry<int, (int, int, int, int)> a,
          MapEntry<int, (int, int, int, int)> b,
        ) => a.value.$1.compareTo(b.value.$1),
      );

  // Crop characters
  // Use fixed length list to avoid dynamic resizing, length should be 4
  final List<Matrix<int>?> result = List<Matrix<int>?>.filled(4, null);
  int index = 0;
  for (final MapEntry<int, (int, int, int, int)> bbox in sortedBboxes) {
    final (int minX, int minY, int maxX, int maxY) = bbox.value;
    final Matrix<int> cropped = _cropAndPad(
      labeledImage,
      minX,
      minY,
      maxX - minX + 1,
      maxY - minY + 1,
    );
    result[index++] = cropped;
  }
  return result;
}
