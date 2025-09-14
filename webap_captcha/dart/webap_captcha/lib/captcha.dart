import 'utils.dart';
import 'segment.dart';
import 'eucdist.dart';
import 'matrix.dart';

import 'package:image/image.dart';
import 'package:tflite_flutter/tflite_flutter.dart';

class SegmentationException implements Exception {
  final String message;
  SegmentationException(this.message);

  @override
  String toString() => 'SegmentationException: $message';
}

Future<String> solveByEucDist(Image image) async {
  final Matrix<int> img = imageToMatrix(image);

  final Matrix<int> binaryImg = binaryThreshold(img, 138);
  final (Matrix<int> labeledImg, int numLabels) = label(binaryImg);

  if (numLabels != 4) {
    throw SegmentationException('connected components != 4, found: $numLabels');
  }

  final List<Matrix<int>?> characters = cropImage(labeledImg, numLabels);

  final StringBuffer results = StringBuffer();
  for (final Matrix<int>? charImg in characters) {
    results.write(
      await getCharacter(charImg!),
    ); // null is placeholder, should be non-null
  }
  return results.toString();
}

const List<String> labels = <String>[
  'A',  'B',  'C',  'D',
  'E',  'F',  'G',  'H',
  'I',  'J',  'K',  'L',
  'M',  'N',  'O',  'P',
  'Q',  'R',  'S',  'T',
  'U',  'V',  'W',  'X',
  'Y',  'Z',  '0',  '1',
  '2',  '3',  '4',  '5',
  '6',  '7',  '8',  '9',
];

Future<String> solveByTfLite(Image image) async {
  const int digitsCount = 4;
  const int imageHeight = 40;
  const int imageWidth = 85;
  
  final Image grayscaleImage = grayscale(image);
  final Interpreter interpreter = await Interpreter.fromAsset(
    'assets/webap_captcha.tflite',
  );

  final StringBuffer replaceText = StringBuffer();
  const int w = imageWidth ~/ digitsCount;
  const int h = imageHeight;
  for (int i = 0; i < digitsCount; i++) {
    final Image target = copyCrop(
      grayscaleImage,
      x: (imageWidth ~/ digitsCount) * i,
      y: 0,
      width: w,
      height: h,
    );
    final List<dynamic> output = List<dynamic>.filled(
      1 * labels.length,
      0,
    ).reshape(<int>[1, labels.length]);
    interpreter.run(imageToByteListFloat32(target, w, h, 127.5, 255.0), output);
    if (output.first case final List<double> list?) {
      final List<double> flattedOutputs = list.toList();
      flattedOutputs.sort();
      final int maxIndex = list.indexOf(flattedOutputs.last);
      replaceText.write(labels[maxIndex]);
    }
  }
  interpreter.close();
  return replaceText.toString();
}
