import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:developer' as debug;

part 'chat_response_provider.g.dart';

@riverpod
Future<String> chatResponse(Ref ref, String query) async {
  User user = ref.read(userInfoProvider);
  Map<String, Friend> friends = ref.read(friendsProvider);
  // debug.log(user.appPreferences['appearance'].toString());
  String body = jsonEncode({
    'query': query,
    'user': user.toJson(),
    'friends': friends
  });
  // debug.log(body);
  var response = await http.post(
    Uri.http('10.0.2.2:5000', '/generateTSSemChunk'),
    headers: {'Content-Type': 'application/json'},
    body: body
  );
  var answer = response.body.trim();
  if (answer[0] == '"' && answer[answer.length - 1] == '"') {
    answer = answer.substring(1, answer.length - 1);
  }

  answer = answer
    .replaceAll('\\"', '"')
    .replaceAll('\\n', '\n');
  // // await Future.delayed(Duration(seconds: 20));
  // var answer = "**Hello World** That text was **bold**.";
  return answer;
}