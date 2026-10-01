/* Render the converter's exact MathML using pinned MathJax, without a browser. */
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '../.runtime/node/mathjax-full');
const {mathjax} = require(root + '/js/mathjax.js');
const {MathML} = require(root + '/js/input/mathml.js');
const {SVG} = require(root + '/js/output/svg.js');
const {liteAdaptor} = require(root + '/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler} = require(root + '/js/handlers/html.js');
const adaptor = liteAdaptor(); RegisterHTMLHandler(adaptor);
const document = mathjax.document('', {InputJax: new MathML(), OutputJax: new SVG({fontCache:'none'})});
const inputs = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(inputs.map(item => adaptor.outerHTML(document.convert(item.mathml, {display:item.display})))));
