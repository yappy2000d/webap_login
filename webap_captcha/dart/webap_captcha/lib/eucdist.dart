import 'utils.dart' show readImage;
import 'matrix.dart' show Matrix;

const _characters = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

/// Load reference images from the assets directory.
final _referenceImages = List<Future<Matrix<int>>>.generate(_characters.length, (
  index,
) async {
  String char = _characters[index];
  String path = 'assets/$char.bmp';
  Matrix<int> img = await readImage(path);
  return img;
});

/// Calculate the Euclidean distance between two gray-scale images.
num eucDist(Matrix<int> a, Matrix<int> b) {
  if (a.width != b.width || a.height != b.height) {
    throw ArgumentError('Images must have the same dimensions');
  }

  num sum = 0;
  for (int y = 0; y < a.height; y++) {
    for (int x = 0; x < a.width; x++) {
      num diff =
         a.get(x, y) - b.get(x, y); // Assuming grayscale images
      sum += diff * diff;
    }
  }

  return sum;
}

/// Get the character represented by the image.
/// The image should be a preprocessed, cropped character gray-scale image.
Future<String> getCharacter(Matrix<int> img) async {
  // Compute distances to reference images
  List<Future<num>> distances = _referenceImages
      .map((ref) async => eucDist(img, await ref))
      .toList();

  // Wait for all distances to be computed
  List<num> resolvedDistances = await Future.wait(distances);
  // Find the index of the minimum distance
  int index = resolvedDistances.indexOf(resolvedDistances.reduce((a, b) => a < b ? a : b));

  return _characters[index];
}
