import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

part 'chat_response_provider.g.dart';

@riverpod
Future<Map<String, dynamic>> chatResponse(Ref ref, String query) async {
  User user = ref.read(userInfoProvider);
  Map<String, Friend> friends = ref.read(friendsProvider);
  Map<String, Map<String, dynamic>> jsonFriends = {};
  for (String id in friends.keys) {
    jsonFriends[id] = friends[id]!.toJson();
  }
  // debug.log(user.appPreferences['appearance'].toString());
  String body = jsonEncode({
    'query': query,
    'user': user.toJson(),
    'friends': jsonFriends
  });
  // debug.log(body);
  var response = await http.post(
    Uri.http('10.0.2.2:5000', '/generateTSSemChunkSQ'),
    headers: {'Content-Type': 'application/json'},
    body: body
  );
  Map<String, dynamic> decoded = jsonDecode(response.body);
  return decoded;
  // // await Future.delayed(Duration(seconds: 20));
  // var answer = "**Hello World** That text was **bold**.";
  // return answer;
}