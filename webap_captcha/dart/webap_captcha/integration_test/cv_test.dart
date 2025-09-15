@Timeout(Duration(minutes: 5))
library;

import 'dart:math' as math;

import 'package:webap_captcha/bmp_assets.dart' show bmpFiles;
import 'package:path/path.dart';
import 'package:opencv_dart/opencv.dart' as cv;
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:integration_test/integration_test.dart';

class SegmentationException implements Exception {
  final String message;
  SegmentationException(this.message);

  @override
  String toString() => 'SegmentationException: $message';
}

Future<cv.Mat> readImage(String path) async {
  final bytedata = await rootBundle.load(path);
  final bytes = bytedata.buffer.asUint8List();
  final gray = cv.imdecode(bytes, cv.IMREAD_GRAYSCALE);
  return gray;
}

const String _characters = '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';

/// Load reference images from the assets directory.
final List<Future<cv.Mat>> _referenceImages = List<Future<cv.Mat>>.generate(
  _characters.length,
  (int index) async {
    final String char = _characters[index];
    final String path = 'assets/eucdist/$char.bmp';
    final mat = await readImage(path);
    return mat;
  },
);

/// Get the character represented by the image.
/// The image should be a preprocessed, cropped character gray-scale image.
Future<String> getCharacter(cv.Mat img) async {
  // Compute distances to reference images
  final resolvedDistances = _referenceImages.map((refFuture) async {
    final ref = await refFuture;
    return eucDist(img, ref);
  });

  // Wait for all distances to be computed
  final resolvedDistancesList = await Future.wait(resolvedDistances);

  // Find the index of the minimum distance
  final int index = resolvedDistancesList.indexOf(
    resolvedDistancesList.reduce((num a, num b) => a < b ? a : b),
  );

  return _characters[index];
}

/// Calculate the Euclidean distance between two gray-scale images.
num eucDist(cv.Mat matA, cv.Mat matB) {
  if (matA.cols != matB.cols || matA.rows != matB.rows) {
    throw ArgumentError(
      'Images must have the same dimensions, got '
      '${matA.cols}x${matA.rows} and ${matB.cols}x${matB.rows}',
    );
  }

  num sum = 0;
  for (int y = 0; y < matA.rows; y++) {
    for (int x = 0; x < matA.cols; x++) {
      final int diff =
          matA.at<int>(x, y) - matB.at<int>(x, y); // Assuming grayscale images
      sum += math.pow(diff, 2);
    }
  }

  return sum;
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

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  test('Euclidean Distance based solver', () async {
    var correct = 0;
    var error = 0;
    var start = DateTime.now();

    for (final fileName in bmpFiles) {
      var ans = basenameWithoutExtension(fileName);
      if (ans.contains('_')) {
        ans = ans.split('_').first;
      }
      try {
        final gray = await readImage('assets_test/labeled/$fileName');

        // Apply binary thresholding
        final (_, thresh) = await cv.thresholdAsync(
          gray,
          138,
          255,
          cv.THRESH_BINARY_INV,
        );

        final (contours, hierarchy) = await cv.findContoursAsync(
          thresh,
          cv.RETR_EXTERNAL,
          cv.CHAIN_APPROX_SIMPLE,
        );

        if (contours.length != 4) {
          throw SegmentationException(
            'Expected 4 contours, found ${contours.length}',
          );
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
          print('EucDist: Correct for $ans');
        } else {
          print('EucDist: Incorrect for $ans, got $resultStr');
          error++;
        }
      } on SegmentationException {
        // print('EucDist: SegmentationException for $ans');
        error++;
      } catch (e) {
        // print('EucDist: Exception for $ans: $e');
        error++;
      }
    }
    var end = DateTime.now();
    print(
      'EucDist: Correct: $correct, Error: $error, Time: \\${end.difference(start).inMilliseconds} ms',
    );
    // expect(error, equals(0), reason: 'There should be no errors in Euclidean solver');
  });
}
