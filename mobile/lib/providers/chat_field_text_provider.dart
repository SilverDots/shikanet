import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'chat_field_text_provider.g.dart';

@Riverpod(keepAlive: true)
TextEditingController chatFieldText(Ref ref) {
  return TextEditingController();
}