import 'package:webap_captcha/eucdist.dart';
import 'package:webap_captcha/utils.dart';

void main(List<String> arguments) async {
  final imgA = await readImage('assets/M.bmp');

  print(await getCharacter(imgA));
}
