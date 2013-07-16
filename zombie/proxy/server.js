var net = require('net');
var Browser = require('zombie');

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
function cleanup() {
    for (var key in CLIENTS) {
        CLIENTS[key][0].destroy();
    }
    CLIENTS = {};
}

function check_field(browser, node, value) {
    var type = node.getAttribute('type');
    if (type == "radio") browser.choose(node);
    else node.checked = value;
}

function set_field(browser, node, value) {
    var tagName = node.tagName;
    if (tagName == "TEXTAREA") {
        node.textContent = value;
    } else {
        var type = node.getAttribute('type');
        if(type == "checkbox"){
            value ? browser.check(node) : browser.uncheck(node);
        }else if(type == "radio"){
            browser.choose(node);
        }else{
            browser.fill(node, value);
        }
    }
}

function ctx_switch(id){
    if(!CLIENTS[id])
        CLIENTS[id] = [new Browser(), []];
    return CLIENTS[id];
}

function create_elements(ELEMENTS, results) {
    var result = [];
    for(var i = 0; i < results.length; i++) {
        ELEMENTS.push(results[i]);
        result.push(ELEMENTS.length - 1);
    }
    return result;
}

function create_element(ELEMENTS, result) {
    if (result) {
        ELEMENTS.push(result);
        return ELEMENTS.length - 1;
    }
    return null;
}

net.createServer(function (stream){
  stream.setEncoding('utf8');

    function return_error(err) {
      stream.end(JSON.stringify([1, err.stack]));
    };

    function return_result(result) {
      stream.end(JSON.stringify([0, result]));
    };

    function wait_callback(err, browser) {
      if (err) return_error(err);
      else return_result(null);
    };

    function wait_n_return_callback(err, value) {
      if (err) return_error(err);
      else return_result(value);
    };

  stream.on('data', function (data){
    var result = null;
    try {
        eval(data);
    } catch(err) {
        return_error(err);
    }
  });

}).listen(process.argv[2], function(){
    console.log('Zombie.js server running on ' + process.argv[2] + '...');
});
