import 'utils.dart';
import 'segment.dart';
import 'eucdist.dart';

import 'package:image/image.dart';

class SegmentationException implements Exception {
  final String message;
  SegmentationException(this.message);

  @override
  String toString() => 'SegmentationException: $message';
}

Future<String> solveByEucDist(Image image) async {
  final img = imageToMatrix(image);

  final binaryImg = binaryThreshold(img, 138);
  final (labeledImg, numLabels) = label(binaryImg);

  if (numLabels != 4) {
    throw SegmentationException('connected components != 4, found: $numLabels');
  }

  final characters = cropImage(labeledImg, numLabels);
  
  var results = "";
  for (final charImg in characters) {
    results += await getCharacter(charImg);
  }
  return results;
}
