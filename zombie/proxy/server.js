var net = require('net');
var zombie = require('zombie');

// Defaults
var ping = 'pong'
var browser = null;
var ELEMENTS = [];

//
// Store global client states indexed by ZombieProxyClient (memory address):
//
// {
//   'CLIENTID': [X, Y]
// }
//
// ...where X is some zombie.Browser instance...
//
// ...and Y is a per-browser cache (a list) used to store  NodeList results.
// Subsequent TCP API calls will reference indexes to retrieve DOM
// attributes/properties accumulated in previous browser.querySelectorAll()
// calls.
//
//
var CLIENTS = {};

//
// Simple proxy server implementation
// for proxying streamed (Javascript) content via HTTP
// to a running Zombie.js
//
// Borrowed (heavily) from the Capybara-Zombie project
// https://github.com/plataformatec/capybara-zombie
//
//
function ctx_switch(id){
    if(!CLIENTS[id])
        CLIENTS[id] = [new zombie.Browser(), []];
    return CLIENTS[id];
}

net.createServer(function (stream){
  stream.setEncoding('utf8');

  stream.on('data', function (data){
    eval(data);
  });

}).listen(process.argv[2], function(){
    console.log('Zombie.js server running on ' + process.argv[2] + '...');
});
