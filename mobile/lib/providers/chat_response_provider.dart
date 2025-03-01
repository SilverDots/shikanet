import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

part 'chat_response_provider.g.dart';

@riverpod
Future<String> chatResponse(Ref ref, String query) async {
  var response = await http.post(
    Uri.http('10.0.2.2:5000', '/generate'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'query': query})
  );
  var answer = response.body.trim();
  if (answer[0] == '"' && answer[answer.length - 1] == '"') {
    answer = answer.substring(1, answer.length - 1);
  }

  answer = answer
    .replaceAll('\\"', '"')
    .replaceAll('\\n', '\n');
  // var answer = "**Hello World** That text was **bold**.";
  return answer;
}