/* 반드시 page 1인 상태에서 사용해 주세요! */
/* UTF-8 형식으로 저장됩니다 */

var totalPages = +$('.-totalPages').textContent;
var nextButton = $('.-next .-btn');

var headers = [];
var header = $('.-header .rt-tr .rt-th');

while (header) {
  headers.push(header.textContent);
  header = header.nextSibling;
}

console.log('Headers:', headers);

var rows = [];
for (let i = 0; i < totalPages; i++) {
  var tRow = $('.rt-tbody .rt-tr-group');

  while (tRow) {
    var row = [];
    for (item of tRow.firstElementChild.children) {
      row.push(item.textContent.replace(/\n|\r/g, ' '));
    }
    rows.push(row);
    tRow = tRow.nextSibling;
  }

  nextButton.click();
}

var tsvHeaders = headers.join('\t');
var tsvRows = '';
for (row of rows) {
  var tsvRow = row.join('\t');
  tsvRows += '\n' + tsvRow;
}

var tsv = tsvHeaders + tsvRows;
window.location.href = `data:text/tab-separated-values,${encodeURIComponent(tsv)}`;
