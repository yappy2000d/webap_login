import 'utils.dart';
import 'segment.dart';
import 'eucdist.dart';
import 'matrix.dart';

import 'package:image/image.dart';

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
    results.write(await getCharacter(charImg!));  // null is placeholder, should be non-null
  }
  return results.toString();
}
