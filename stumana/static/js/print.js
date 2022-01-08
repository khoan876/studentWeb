var max_pages = 100;
var page_count = 0;

function snipMe() {
  page_count++;
  if (page_count > max_pages) {
    return;
  }
  var long = $(this)[0].scrollHeight - Math.ceil($(this).innerHeight());
  var children = $(this).children().toArray();
  var removed = [];
  while (long > 0 && children.length > 0) {
    var child = children.pop();
    $(child).detach();
    removed.unshift(child);
    long = $(this)[0].scrollHeight - Math.ceil($(this).innerHeight());
  }
  if (removed.length > 0) {
    var a4 = $('<div class="A4"></div>');
    a4.append(removed);
    $(this).after(a4);
    snipMe.call(a4[0]);
  }
}

$(document).ready(function() {
  $('.A4').each(function() {
    snipMe.call(this);
  });
});