@Timeout(Duration(minutes: 2))
library;

import 'dart:io' as io;
import 'dart:math' as math;

import 'package:path/path.dart';
import 'package:opencv_dart/opencv.dart' as cv;
import 'package:flutter_test/flutter_test.dart';

class SegmentationException implements Exception {
  final String message;
  SegmentationException(this.message);

  @override
  String toString() => 'SegmentationException: $message';
}

const String _characters = '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';

/// Load reference images from the assets directory.
final List<Future<cv.Mat>> _referenceImages = List<Future<cv.Mat>>.generate(
  _characters.length,
  (int index) async {
    final String char = _characters[index];
    final String path = 'assets/eucdist/$char.bmp';
    return cv.imreadAsync(path);
  },
);

/// Get the character represented by the image.
/// The image should be a preprocessed, cropped character gray-scale image.
Future<String> getCharacter(cv.Mat img) async {
  // Compute distances to reference images
  final resolvedDistances = _referenceImages.map(
    (ref) async => eucDist(img, await ref),
  );

  // Wait for all distances to be computed
  final resolvedDistancesList = await Future.wait(resolvedDistances);

  // Find the index of the minimum distance
  final int index = resolvedDistancesList
      .indexOf(resolvedDistancesList.reduce((num a, num b) => a < b ? a : b));

  return _characters[index];
}

/// Calculate the Euclidean distance between two gray-scale images.
num eucDist(cv.Mat matA, cv.Mat matB) {
  if (matA.cols != matB.cols || matA.rows != matB.rows) {
    throw ArgumentError('Images must have the same dimensions');
  }

  num sum = 0;
  for (int y = 0; y < matA.rows; y++) {
    for (int x = 0; x < matA.cols; x++) {
      final int diff = matA.at<int>(x, y) - matB.at<int>(x, y); // Assuming grayscale images
      sum += math.pow(diff, 2);
      // sum += diff * diff;
    }
  }

  return sum;
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  final testDir = io.Directory("assets_test/labeled");

  test('Euclidean Distance based solver (OpenCV)', () async {
    var correct = 0;
    var error = 0;
    var start = DateTime.now();

    for (final file in testDir.listSync()) {
      if (file is io.File && file.path.endsWith('.bmp')) {
        var ans = basenameWithoutExtension(file.path);
        if (ans.contains('_')) {
          ans = ans.split('_').first;
        }

        final img = await cv.imreadAsync(file.path);
        // expect(img, isNotNull, reason: 'Failed to read image for $ans');

        // Convert to grayscale
        final gray = await cv.cvtColorAsync(img, cv.COLOR_BGR2GRAY);

        // Apply binary thresholding
        final (_, thresh) = await cv.thresholdAsync(
          gray,
          138,
          255,
          cv.THRESH_BINARY_INV,
        );

        // remove noise
        // final kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2));
        // final erosion = await cv.erodeAsync(thresh, kernel);
        // final dilation = await cv.dilateAsync(erosion, kernel);

        // Find contours
        final (contours, hierarchy) = await cv.findContoursAsync(
          thresh,
          cv.RETR_EXTERNAL,
          cv.CHAIN_APPROX_SIMPLE,
        );

        if (contours.length != 4) {
          error++;
          continue;
          // throw SegmentationException(
          //   'connected components != 4, found: ${contours.length} for $ans',
          // );
        }

        final boundingRects = await Future.wait(
          contours.map((c) => cv.boundingRectAsync(c)),
        );

        // Sort bounding rectangles by x coordinate
        boundingRects.sort((a, b) => a.x.compareTo(b.x));

        // Crop and resize each character
        final charImages = boundingRects.map((rect) {
            final charImg = thresh.submat(rect);
            // pad to 22x22
            const targetSize = 22;
            final top = (targetSize - charImg.rows) ~/ 2;
            final bottom = targetSize - charImg.rows - top;
            final left = (targetSize - charImg.cols) ~/ 2;
            final right = targetSize - charImg.cols - left;
            final resizedCharImg = cv.copyMakeBorderAsync(
              charImg,
              top,
              bottom,
              left,
              right,
              cv.BORDER_CONSTANT,
              value: cv.Scalar.all(0),
            );
            return resizedCharImg;
          });
        
        // Wait for all charImages to be ready
        final charImagesList = await Future.wait(charImages);

        // solve each character
        final result = await Future.wait(
          charImagesList.map((charImg) async => await getCharacter(charImg)),
        );

        final resultStr = result.join();
        if (resultStr == ans) {
          correct++;
        } else {
          error++;
        }
      }
    }
    var end = DateTime.now();
    print(
      'OpenCV: Correct: $correct, Error: $error, Time: \\${end.difference(start).inMilliseconds} ms',
    );
  });
}

extension on cv.Mat {
  cv.Mat submat(cv.Rect rect) {
    return cv.Mat.fromRange(
      this,
      rect.y,
      rect.y + rect.height,
      colStart: rect.x,
      colEnd: rect.x + rect.width,
    );
  }
}
