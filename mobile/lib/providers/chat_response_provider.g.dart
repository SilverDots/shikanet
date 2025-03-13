// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'chat_response_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$chatResponseHash() => r'72fbc49979da8395dd8572c02424486e1d6541ef';

/// Copied from Dart SDK
class _SystemHash {
  _SystemHash._();

  static int combine(int hash, int value) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + value);
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x0007ffff & hash) << 10));
    return hash ^ (hash >> 6);
  }

  static int finish(int hash) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x03ffffff & hash) << 3));
    // ignore: parameter_assignments
    hash = hash ^ (hash >> 11);
    return 0x1fffffff & (hash + ((0x00003fff & hash) << 15));
  }
}

/// See also [chatResponse].
@ProviderFor(chatResponse)
const chatResponseProvider = ChatResponseFamily();

/// See also [chatResponse].
class ChatResponseFamily extends Family<AsyncValue<String>> {
  /// See also [chatResponse].
  const ChatResponseFamily();

  /// See also [chatResponse].
  ChatResponseProvider call(
    String query,
  ) {
    return ChatResponseProvider(
      query,
    );
  }

  @override
  ChatResponseProvider getProviderOverride(
    covariant ChatResponseProvider provider,
  ) {
    return call(
      provider.query,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'chatResponseProvider';
}

/// See also [chatResponse].
class ChatResponseProvider extends AutoDisposeFutureProvider<String> {
  /// See also [chatResponse].
  ChatResponseProvider(
    String query,
  ) : this._internal(
          (ref) => chatResponse(
            ref as ChatResponseRef,
            query,
          ),
          from: chatResponseProvider,
          name: r'chatResponseProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$chatResponseHash,
          dependencies: ChatResponseFamily._dependencies,
          allTransitiveDependencies:
              ChatResponseFamily._allTransitiveDependencies,
          query: query,
        );

  ChatResponseProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.query,
  }) : super.internal();

  final String query;

  @override
  Override overrideWith(
    FutureOr<String> Function(ChatResponseRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: ChatResponseProvider._internal(
        (ref) => create(ref as ChatResponseRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        query: query,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<String> createElement() {
    return _ChatResponseProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is ChatResponseProvider && other.query == query;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, query.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin ChatResponseRef on AutoDisposeFutureProviderRef<String> {
  /// The parameter `query` of this provider.
  String get query;
}

class _ChatResponseProviderElement
    extends AutoDisposeFutureProviderElement<String> with ChatResponseRef {
  _ChatResponseProviderElement(super.provider);

  @override
  String get query => (origin as ChatResponseProvider).query;
}
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
