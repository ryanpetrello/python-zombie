var net = require('net');
var sys = require('sys');
var zombie = require('zombie');

//
// Store a global reference to the Zombie.js
// browser object and a buffered collection
// of Zombie.js calls.
//
var browser = null;

//
// This is used as a per-browser cache to store
// NodeList results.  Subsequent TCP API calls
// will reference indexes of ELEMENTS to retrieve
// DOM attributes/properties accumulated in previous
// browser.querySelectorAll() calls.
//
var ELEMENTS = [];

//
// Simple proxy server implementation
// for proxying streamed (Javascript) content via HTTP
// to a running Zombie.js
//
// Borrowed (heavily) from the Capybara-Zombie project
// https://github.com/plataformatec/capybara-zombie
//

net.createServer(function (stream){
  stream.setEncoding('utf8');

  stream.on('data', function (data){
    if (browser == null){
      browser = new zombie.Browser();
      ELEMENTS = [];
    }
    eval(data);
  });

}).listen(process.argv[2]);

console.log('Node TCP server running on '+process.argv[2]+'...');
