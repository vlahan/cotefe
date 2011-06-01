goog.require('goog.net.XhrIo');

/**
 * Retrieve Json data using XhrIo's static send() method.
 *
 * @param {string} dataUrl The url to request.
 */
function getData(url) {
  log('Sending simple request for ['+ url + ']');
  goog.net.XhrIo.send(url, function(e) {
	  var xhr = e.target;
      var obj = xhr.getResponseJson();
      log('name = ' + obj['name'] + '');
      log('testbed = ' + obj['testbed'] + '');
      }
  );
}

/**
 * Basic logging to an element called "log".
 *
 * @param {string} msg Message to display on page
 */
function log(msg) {
  document.getElementById('log').appendChild(document.createTextNode(msg));
  document.getElementById('log').appendChild(document.createElement('br'));
}

