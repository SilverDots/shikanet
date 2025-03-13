import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shikanet/data/data.dart';

part 'friends_provider.g.dart';

@Riverpod(keepAlive: true)
class Friends extends _$Friends {
  @override
  Map<String, Friend> build() {
    return {};
  }

  void updateFriend(String uuid, Friend friend) {
    state = {...state, uuid: friend};
  }

  void removeFriend(String uuid) {
    Map<String, Friend> copy = Map.from(state);
    copy.remove(uuid);
    state = copy;
  }

  void clear() {
    state = {};
  }
}