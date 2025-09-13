import 'package:webap_captcha/captcha.dart';
import 'package:image/image.dart';

void main(List<String> arguments) async {
  Image? img = await decodeBmpFile('test/1ALW.bmp');

  if (img == null) {
    print('Failed to decode image');
    return;
  }

  final result = await solveByEucDist(img);
  print(result);
}
