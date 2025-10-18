export default class NumberTransform {
  deserialize(serialized) {
    return serialized;
  }

  serialize(deserialized) {
    return deserialized;
  }

  static create() {
    return new this();
  }
}
