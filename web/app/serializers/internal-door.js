import JSONAPISerializer from '@ember-data/serializer/json-api';

export default class InternalDoorSerializer extends JSONAPISerializer {
  keyForAttribute(attr) {
    // console.log('InternalDoorSerializer.keyForAttribute', attr);
    return attr.replace('/-/g', '_');
  }

  // serialize(snapshot, options) {
  //   console.log(
  //     'InternalDoorSerializer.serialize',
  //     JSON.stringify(snapshot, null, 2),
  //   );
  // }

  // pushPayload(type, payload) {
  //   console.log(
  //     'InternalDoorSerializer.pushPayload',
  //     JSON.stringify(payload, null, 2),
  //   );
  // }
}
