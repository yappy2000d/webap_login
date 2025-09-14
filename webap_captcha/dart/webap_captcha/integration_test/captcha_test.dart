@Timeout(Duration(minutes: 3))
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart';
import 'package:integration_test/integration_test.dart';
import 'package:webap_captcha/captcha.dart';
import 'package:webap_captcha/bmp_assets.dart' show bmpFiles;
import 'package:webap_captcha/utils.dart' show readImage;
import 'package:tflite_flutter/tflite_flutter.dart';

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
        final img = await readImage('assets_test/labeled/$fileName');
        final result = await solveByEucDist(img);
        if (result == ans) {
          correct++;
        } else {
          error++;
        }
      } on SegmentationException {
        error++;
      } catch (e) {
        print('EucDist: Exception for $ans: $e');
        error++;
      }
    }
    var end = DateTime.now();
    print(
      'EucDist: Correct: $correct, Error: $error, Time: \\${end.difference(start).inMilliseconds} ms',
    );
    // expect(error, equals(0), reason: 'There should be no errors in Euclidean solver');
  });

  test('TensorFlow Lite based solver', () async {
    var correct = 0;
    var error = 0;
    var start = DateTime.now();
    final Interpreter interpreter = await Interpreter.fromAsset(
      'assets/webap_captcha.tflite',
    );

    for (final fileName in bmpFiles) {
      var ans = basenameWithoutExtension(fileName);
      if (ans.contains('_')) {
        ans = ans.split('_').first;
      }

      try {
        final img = await readImage('assets_test/labeled/$fileName');
        final result = await solveByTfLite(img, interpreter);
        if (result == ans) {
          correct++;
        } else {
          error++;
        }
      } catch (e) {
        print('TfLite: Exception for $ans: $e');
        error++;
      }
    }
    interpreter.close();

    var end = DateTime.now();
    print(
      'TfLite: Correct: $correct, Error: $error, Time: \\${end.difference(start).inMilliseconds} ms',
    );
    // expect(error, equals(0), reason: 'There should be no errors in TfLite solver');
  });
}
