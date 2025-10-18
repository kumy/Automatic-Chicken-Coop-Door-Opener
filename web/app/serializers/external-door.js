import JSONAPISerializer from '@ember-data/serializer/json-api';

export default class ExternalDoorSerializer extends JSONAPISerializer {
  keyForAttribute(attr) {
    // console.log('ExternalDoorSerializer.keyForAttribute', attr);
    return attr.replace('/-/g', '_');
  }

  // serialize(snapshot, options) {
  //   console.log(
  //     'ExternalDoorSerializer.serialize',
  //     JSON.stringify(snapshot, null, 2),
  //   );
  //   let json = {
  //     id: snapshot.id,
  //     type: 'internal-door',
  //     attributes: {},
  //   };
  //
  //   for (let key in snapshot.attributes) {
  //     json['attributes'][this.keyForAttribute(key)] = snapshot.attributes[key];
  //   }
  //
  //   console.log(
  //     'ExternalDoorSerializer.serialize',
  //     JSON.stringify(json, null, 2),
  //   );
  //   return json;
  // }
}
