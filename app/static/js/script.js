tagClass: function(item) {
  return 'label label-info';
},
itemValue: function(item) {
  return item ? item.toString() : item;
},
itemText: function(item) {
  return this.itemValue(item);
},
itemTitle: function(item) {
  return null;
},
freeInput: true,
addOnBlur: true,
maxTags: undefined,
maxChars: undefined,
confirmKeys: [13, 44],
onTagExists: function(item, $tag) {
  $tag.hide().fadeIn();
},
trimValue: false,
allowDuplicates: false

// #############Multi input script###############
