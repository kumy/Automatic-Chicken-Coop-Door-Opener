export default class BooleanTransform {
  deserialize(serialized) {
    // console.log('BooleanTransform.deserialize', serialized);
    return serialized;
  }

  serialize(deserialized) {
    // console.log('BooleanTransform.serialize', deserialized);
    if (deserialized === 'ON') return true;
    if (deserialized === 'OFF') return false;
    if (deserialized === 'OPEN') return true;
    if (deserialized === 'CLOSED') return false;
    return deserialized;
  }

  static create() {
    // console.log('BooleanTransform.create');
    return new this();
  }
}
