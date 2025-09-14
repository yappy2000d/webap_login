import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart';
import 'package:webap_captcha/captcha.dart';
import 'package:image/image.dart';
import 'package:tflite_flutter/tflite_flutter.dart';


void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  final testDir = Directory("assets_test/labeled");

  test('Euclidean Distance based solver', () async {
    var correct = 0;
    var error = 0;
    var start = DateTime.now();

    for (final file in testDir.listSync()) {
      if (file is File && file.path.endsWith('.bmp')) {
        var ans = basenameWithoutExtension(file.path);
        if (ans.contains('_')) {
          ans = ans.split('_').first;
        }

        final img = decodeBmp(file.readAsBytesSync());
        expect(img, isNotNull, reason: 'Failed to decode image for $ans');
        try {
          final result = await solveByEucDist(img!);
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
    for (final file in testDir.listSync()) {
      if (file is File && file.path.endsWith('.bmp')) {
        var ans = basenameWithoutExtension(file.path);
        if (ans.contains('_')) {
          ans = ans.split('_').first;
        }

        final img = decodeBmp(file.readAsBytesSync());
        expect(img, isNotNull, reason: 'Failed to decode image for $ans');
        final result = await solveByTfLite(img!, interpreter);
        if (result == ans) {
          correct++;
        } else {
          error++;
        }
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
