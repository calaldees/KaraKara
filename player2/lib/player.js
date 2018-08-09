(function () {
  'use strict';

  function h(name, attributes) {
    var rest = [];
    var children = [];
    var length = arguments.length;

    while (length-- > 2) rest.push(arguments[length]);

    while (rest.length) {
      var node = rest.pop();
      if (node && node.pop) {
        for (length = node.length; length--; ) {
          rest.push(node[length]);
        }
      } else if (node != null && node !== true && node !== false) {
        children.push(node);
      }
    }

    return typeof name === "function"
      ? name(attributes || {}, children)
      : {
          nodeName: name,
          attributes: attributes || {},
          children: children,
          key: attributes && attributes.key
        }
  }

  function app(state, actions, view, container) {
    var map = [].map;
    var rootElement = (container && container.children[0]) || null;
    var oldNode = rootElement && recycleElement(rootElement);
    var lifecycle = [];
    var skipRender;
    var isRecycling = true;
    var globalState = clone(state);
    var wiredActions = wireStateToActions([], globalState, clone(actions));

    scheduleRender();

    return wiredActions

    function recycleElement(element) {
      return {
        nodeName: element.nodeName.toLowerCase(),
        attributes: {},
        children: map.call(element.childNodes, function(element) {
          return element.nodeType === 3 // Node.TEXT_NODE
            ? element.nodeValue
            : recycleElement(element)
        })
      }
    }

    function resolveNode(node) {
      return typeof node === "function"
        ? resolveNode(node(globalState, wiredActions))
        : node != null
          ? node
          : ""
    }

    function render() {
      skipRender = !skipRender;

      var node = resolveNode(view);

      if (container && !skipRender) {
        rootElement = patch(container, rootElement, oldNode, (oldNode = node));
      }

      isRecycling = false;

      while (lifecycle.length) lifecycle.pop()();
    }

    function scheduleRender() {
      if (!skipRender) {
        skipRender = true;
        setTimeout(render);
      }
    }

    function clone(target, source) {
      var out = {};

      for (var i in target) out[i] = target[i];
      for (var i in source) out[i] = source[i];

      return out
    }

    function setPartialState(path, value, source) {
      var target = {};
      if (path.length) {
        target[path[0]] =
          path.length > 1
            ? setPartialState(path.slice(1), value, source[path[0]])
            : value;
        return clone(source, target)
      }
      return value
    }

    function getPartialState(path, source) {
      var i = 0;
      while (i < path.length) {
        source = source[path[i++]];
      }
      return source
    }

    function wireStateToActions(path, state, actions) {
      for (var key in actions) {
        typeof actions[key] === "function"
          ? (function(key, action) {
              actions[key] = function(data) {
                var result = action(data);

                if (typeof result === "function") {
                  result = result(getPartialState(path, globalState), actions);
                }

                if (
                  result &&
                  result !== (state = getPartialState(path, globalState)) &&
                  !result.then // !isPromise
                ) {
                  scheduleRender(
                    (globalState = setPartialState(
                      path,
                      clone(state, result),
                      globalState
                    ))
                  );
                }

                return result
              };
            })(key, actions[key])
          : wireStateToActions(
              path.concat(key),
              (state[key] = clone(state[key])),
              (actions[key] = clone(actions[key]))
            );
      }

      return actions
    }

    function getKey(node) {
      return node ? node.key : null
    }

    function eventListener(event) {
      return event.currentTarget.events[event.type](event)
    }

    function updateAttribute(element, name, value, oldValue, isSvg) {
      if (name === "key") ; else if (name === "style") {
        for (var i in clone(oldValue, value)) {
          var style = value == null || value[i] == null ? "" : value[i];
          if (i[0] === "-") {
            element[name].setProperty(i, style);
          } else {
            element[name][i] = style;
          }
        }
      } else {
        if (name[0] === "o" && name[1] === "n") {
          name = name.slice(2);

          if (element.events) {
            if (!oldValue) oldValue = element.events[name];
          } else {
            element.events = {};
          }

          element.events[name] = value;

          if (value) {
            if (!oldValue) {
              element.addEventListener(name, eventListener);
            }
          } else {
            element.removeEventListener(name, eventListener);
          }
        } else if (
          name in element &&
          name !== "list" &&
          name !== "type" &&
          name !== "draggable" &&
          name !== "spellcheck" &&
          name !== "translate" &&
          !isSvg
        ) {
          element[name] = value == null ? "" : value;
        } else if (value != null && value !== false) {
          element.setAttribute(name, value);
        }

        if (value == null || value === false) {
          element.removeAttribute(name);
        }
      }
    }

    function createElement(node, isSvg) {
      var element =
        typeof node === "string" || typeof node === "number"
          ? document.createTextNode(node)
          : (isSvg = isSvg || node.nodeName === "svg")
            ? document.createElementNS(
                "http://www.w3.org/2000/svg",
                node.nodeName
              )
            : document.createElement(node.nodeName);

      var attributes = node.attributes;
      if (attributes) {
        if (attributes.oncreate) {
          lifecycle.push(function() {
            attributes.oncreate(element);
          });
        }

        for (var i = 0; i < node.children.length; i++) {
          element.appendChild(
            createElement(
              (node.children[i] = resolveNode(node.children[i])),
              isSvg
            )
          );
        }

        for (var name in attributes) {
          updateAttribute(element, name, attributes[name], null, isSvg);
        }
      }

      return element
    }

    function updateElement(element, oldAttributes, attributes, isSvg) {
      for (var name in clone(oldAttributes, attributes)) {
        if (
          attributes[name] !==
          (name === "value" || name === "checked"
            ? element[name]
            : oldAttributes[name])
        ) {
          updateAttribute(
            element,
            name,
            attributes[name],
            oldAttributes[name],
            isSvg
          );
        }
      }

      var cb = isRecycling ? attributes.oncreate : attributes.onupdate;
      if (cb) {
        lifecycle.push(function() {
          cb(element, oldAttributes);
        });
      }
    }

    function removeChildren(element, node) {
      var attributes = node.attributes;
      if (attributes) {
        for (var i = 0; i < node.children.length; i++) {
          removeChildren(element.childNodes[i], node.children[i]);
        }

        if (attributes.ondestroy) {
          attributes.ondestroy(element);
        }
      }
      return element
    }

    function removeElement(parent, element, node) {
      function done() {
        parent.removeChild(removeChildren(element, node));
      }

      var cb = node.attributes && node.attributes.onremove;
      if (cb) {
        cb(element, done);
      } else {
        done();
      }
    }

    function patch(parent, element, oldNode, node, isSvg) {
      if (node === oldNode) ; else if (oldNode == null || oldNode.nodeName !== node.nodeName) {
        var newElement = createElement(node, isSvg);
        parent.insertBefore(newElement, element);

        if (oldNode != null) {
          removeElement(parent, element, oldNode);
        }

        element = newElement;
      } else if (oldNode.nodeName == null) {
        element.nodeValue = node;
      } else {
        updateElement(
          element,
          oldNode.attributes,
          node.attributes,
          (isSvg = isSvg || node.nodeName === "svg")
        );

        var oldKeyed = {};
        var newKeyed = {};
        var oldElements = [];
        var oldChildren = oldNode.children;
        var children = node.children;

        for (var i = 0; i < oldChildren.length; i++) {
          oldElements[i] = element.childNodes[i];

          var oldKey = getKey(oldChildren[i]);
          if (oldKey != null) {
            oldKeyed[oldKey] = [oldElements[i], oldChildren[i]];
          }
        }

        var i = 0;
        var k = 0;

        while (k < children.length) {
          var oldKey = getKey(oldChildren[i]);
          var newKey = getKey((children[k] = resolveNode(children[k])));

          if (newKeyed[oldKey]) {
            i++;
            continue
          }

          if (newKey != null && newKey === getKey(oldChildren[i + 1])) {
            if (oldKey == null) {
              removeElement(element, oldElements[i], oldChildren[i]);
            }
            i++;
            continue
          }

          if (newKey == null || isRecycling) {
            if (oldKey == null) {
              patch(element, oldElements[i], oldChildren[i], children[k], isSvg);
              k++;
            }
            i++;
          } else {
            var keyedNode = oldKeyed[newKey] || [];

            if (oldKey === newKey) {
              patch(element, keyedNode[0], keyedNode[1], children[k], isSvg);
              i++;
            } else if (keyedNode[0]) {
              patch(
                element,
                element.insertBefore(keyedNode[0], oldElements[i]),
                keyedNode[1],
                children[k],
                isSvg
              );
            } else {
              patch(element, oldElements[i], null, children[k], isSvg);
            }

            newKeyed[newKey] = children[k];
            k++;
          }
        }

        while (i < oldChildren.length) {
          if (getKey(oldChildren[i]) == null) {
            removeElement(element, oldElements[i], oldChildren[i]);
          }
          i++;
        }

        for (var i in oldKeyed) {
          if (!newKeyed[i]) {
            removeElement(element, oldKeyed[i][0], oldKeyed[i][1]);
          }
        }
      }
      return element
    }
  }

  var isWebSocket = function (constructor) {
      return constructor && constructor.CLOSING === 2;
  };
  var isGlobalWebSocket = function () {
      return typeof WebSocket !== 'undefined' && isWebSocket(WebSocket);
  };
  var getDefaultOptions = function () { return ({
      constructor: isGlobalWebSocket() ? WebSocket : null,
      maxReconnectionDelay: 10000,
      minReconnectionDelay: 1500,
      reconnectionDelayGrowFactor: 1.3,
      connectionTimeout: 4000,
      maxRetries: Infinity,
      debug: false,
  }); };
  var bypassProperty = function (src, dst, name) {
      Object.defineProperty(dst, name, {
          get: function () { return src[name]; },
          set: function (value) { src[name] = value; },
          enumerable: true,
          configurable: true,
      });
  };
  var initReconnectionDelay = function (config) {
      return (config.minReconnectionDelay + Math.random() * config.minReconnectionDelay);
  };
  var updateReconnectionDelay = function (config, previousDelay) {
      var newDelay = previousDelay * config.reconnectionDelayGrowFactor;
      return (newDelay > config.maxReconnectionDelay)
          ? config.maxReconnectionDelay
          : newDelay;
  };
  var LEVEL_0_EVENTS = ['onopen', 'onclose', 'onmessage', 'onerror'];
  var reassignEventListeners = function (ws, oldWs, listeners) {
      Object.keys(listeners).forEach(function (type) {
          listeners[type].forEach(function (_a) {
              var listener = _a[0], options = _a[1];
              ws.addEventListener(type, listener, options);
          });
      });
      if (oldWs) {
          LEVEL_0_EVENTS.forEach(function (name) {
              ws[name] = oldWs[name];
          });
      }
  };
  var ReconnectingWebsocket = function (url, protocols, options) {
      var _this = this;
      if (options === void 0) { options = {}; }
      var ws;
      var connectingTimeout;
      var reconnectDelay = 0;
      var retriesCount = 0;
      var shouldRetry = true;
      var savedOnClose = null;
      var listeners = {};
      // require new to construct
      if (!(this instanceof ReconnectingWebsocket)) {
          throw new TypeError("Failed to construct 'ReconnectingWebSocket': Please use the 'new' operator");
      }
      // Set config. Not using `Object.assign` because of IE11
      var config = getDefaultOptions();
      Object.keys(config)
          .filter(function (key) { return options.hasOwnProperty(key); })
          .forEach(function (key) { return config[key] = options[key]; });
      if (!isWebSocket(config.constructor)) {
          throw new TypeError('Invalid WebSocket constructor. Set `options.constructor`');
      }
      var log = config.debug ? function () {
          var params = [];
          for (var _i = 0; _i < arguments.length; _i++) {
              params[_i] = arguments[_i];
          }
          return console.log.apply(console, ['RWS:'].concat(params));
      } : function () { };
      /**
       * Not using dispatchEvent, otherwise we must use a DOM Event object
       * Deferred because we want to handle the close event before this
       */
      var emitError = function (code, msg) { return setTimeout(function () {
          var err = new Error(msg);
          err.code = code;
          if (Array.isArray(listeners.error)) {
              listeners.error.forEach(function (_a) {
                  var fn = _a[0];
                  return fn(err);
              });
          }
          if (ws.onerror) {
              ws.onerror(err);
          }
      }, 0); };
      var handleClose = function () {
          log('handleClose', { shouldRetry: shouldRetry });
          retriesCount++;
          log('retries count:', retriesCount);
          if (retriesCount > config.maxRetries) {
              emitError('EHOSTDOWN', 'Too many failed connection attempts');
              return;
          }
          if (!reconnectDelay) {
              reconnectDelay = initReconnectionDelay(config);
          }
          else {
              reconnectDelay = updateReconnectionDelay(config, reconnectDelay);
          }
          log('handleClose - reconnectDelay:', reconnectDelay);
          if (shouldRetry) {
              setTimeout(connect, reconnectDelay);
          }
      };
      var connect = function () {
          if (!shouldRetry) {
              return;
          }
          log('connect');
          var oldWs = ws;
          var wsUrl = (typeof url === 'function') ? url() : url;
          ws = new config.constructor(wsUrl, protocols);
          connectingTimeout = setTimeout(function () {
              log('timeout');
              ws.close();
              emitError('ETIMEDOUT', 'Connection timeout');
          }, config.connectionTimeout);
          log('bypass properties');
          for (var key in ws) {
              // @todo move to constant
              if (['addEventListener', 'removeEventListener', 'close', 'send'].indexOf(key) < 0) {
                  bypassProperty(ws, _this, key);
              }
          }
          ws.addEventListener('open', function () {
              clearTimeout(connectingTimeout);
              log('open');
              reconnectDelay = initReconnectionDelay(config);
              log('reconnectDelay:', reconnectDelay);
              retriesCount = 0;
          });
          ws.addEventListener('close', handleClose);
          reassignEventListeners(ws, oldWs, listeners);
          // because when closing with fastClose=true, it is saved and set to null to avoid double calls
          ws.onclose = ws.onclose || savedOnClose;
          savedOnClose = null;
      };
      log('init');
      connect();
      this.close = function (code, reason, _a) {
          if (code === void 0) { code = 1000; }
          if (reason === void 0) { reason = ''; }
          var _b = _a === void 0 ? {} : _a, _c = _b.keepClosed, keepClosed = _c === void 0 ? false : _c, _d = _b.fastClose, fastClose = _d === void 0 ? true : _d, _e = _b.delay, delay = _e === void 0 ? 0 : _e;
          log('close - params:', { reason: reason, keepClosed: keepClosed, fastClose: fastClose, delay: delay, retriesCount: retriesCount, maxRetries: config.maxRetries });
          shouldRetry = !keepClosed && retriesCount <= config.maxRetries;
          if (delay) {
              reconnectDelay = delay;
          }
          ws.close(code, reason);
          if (fastClose) {
              var fakeCloseEvent_1 = {
                  code: code,
                  reason: reason,
                  wasClean: true,
              };
              // execute close listeners soon with a fake closeEvent
              // and remove them from the WS instance so they
              // don't get fired on the real close.
              handleClose();
              ws.removeEventListener('close', handleClose);
              // run and remove level2
              if (Array.isArray(listeners.close)) {
                  listeners.close.forEach(function (_a) {
                      var listener = _a[0], options = _a[1];
                      listener(fakeCloseEvent_1);
                      ws.removeEventListener('close', listener, options);
                  });
              }
              // run and remove level0
              if (ws.onclose) {
                  savedOnClose = ws.onclose;
                  ws.onclose(fakeCloseEvent_1);
                  ws.onclose = null;
              }
          }
      };
      this.send = function (data) {
          ws.send(data);
      };
      this.addEventListener = function (type, listener, options) {
          if (Array.isArray(listeners[type])) {
              if (!listeners[type].some(function (_a) {
                  var l = _a[0];
                  return l === listener;
              })) {
                  listeners[type].push([listener, options]);
              }
          }
          else {
              listeners[type] = [[listener, options]];
          }
          ws.addEventListener(type, listener, options);
      };
      this.removeEventListener = function (type, listener, options) {
          if (Array.isArray(listeners[type])) {
              listeners[type] = listeners[type].filter(function (_a) {
                  var l = _a[0];
                  return l !== listener;
              });
          }
          ws.removeEventListener(type, listener, options);
      };
  };
  var dist = ReconnectingWebsocket;

  var commonjsGlobal = typeof window !== 'undefined' ? window : typeof global !== 'undefined' ? global : typeof self !== 'undefined' ? self : {};

  function unwrapExports (x) {
  	return x && x.__esModule && Object.prototype.hasOwnProperty.call(x, 'default') ? x['default'] : x;
  }

  function createCommonjsModule(fn, module) {
  	return module = { exports: {} }, fn(module, module.exports), module.exports;
  }

  var subtitle_bundle = createCommonjsModule(function (module, exports) {
  (function webpackUniversalModuleDefinition(root, factory) {
  	module.exports = factory();
  })(typeof self !== 'undefined' ? self : commonjsGlobal, function() {
  return /******/ (function(modules) { // webpackBootstrap
  /******/ 	// The module cache
  /******/ 	var installedModules = {};
  /******/
  /******/ 	// The require function
  /******/ 	function __webpack_require__(moduleId) {
  /******/
  /******/ 		// Check if module is in cache
  /******/ 		if(installedModules[moduleId]) {
  /******/ 			return installedModules[moduleId].exports;
  /******/ 		}
  /******/ 		// Create a new module (and put it into the cache)
  /******/ 		var module = installedModules[moduleId] = {
  /******/ 			i: moduleId,
  /******/ 			l: false,
  /******/ 			exports: {}
  /******/ 		};
  /******/
  /******/ 		// Execute the module function
  /******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
  /******/
  /******/ 		// Flag the module as loaded
  /******/ 		module.l = true;
  /******/
  /******/ 		// Return the exports of the module
  /******/ 		return module.exports;
  /******/ 	}
  /******/
  /******/
  /******/ 	// expose the modules object (__webpack_modules__)
  /******/ 	__webpack_require__.m = modules;
  /******/
  /******/ 	// expose the module cache
  /******/ 	__webpack_require__.c = installedModules;
  /******/
  /******/ 	// define getter function for harmony exports
  /******/ 	__webpack_require__.d = function(exports, name, getter) {
  /******/ 		if(!__webpack_require__.o(exports, name)) {
  /******/ 			Object.defineProperty(exports, name, {
  /******/ 				configurable: false,
  /******/ 				enumerable: true,
  /******/ 				get: getter
  /******/ 			});
  /******/ 		}
  /******/ 	};
  /******/
  /******/ 	// getDefaultExport function for compatibility with non-harmony modules
  /******/ 	__webpack_require__.n = function(module) {
  /******/ 		var getter = module && module.__esModule ?
  /******/ 			function getDefault() { return module['default']; } :
  /******/ 			function getModuleExports() { return module; };
  /******/ 		__webpack_require__.d(getter, 'a', getter);
  /******/ 		return getter;
  /******/ 	};
  /******/
  /******/ 	// Object.prototype.hasOwnProperty.call
  /******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
  /******/
  /******/ 	// __webpack_public_path__
  /******/ 	__webpack_require__.p = "";
  /******/
  /******/ 	// Load entry module and return exports
  /******/ 	return __webpack_require__(__webpack_require__.s = 5);
  /******/ })
  /************************************************************************/
  /******/ ([
  /* 0 */
  /***/ (function(module, exports, __webpack_require__) {


  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.default = toMS;
  /**
   * Return the given SRT timestamp as milleseconds.
   * @param {string|number} timestamp
   * @returns {number} milliseconds
   */

  function toMS(timestamp) {
    if (!isNaN(timestamp)) {
      return timestamp;
    }

    var match = timestamp.match(/^(?:(\d{2,}):)?(\d{2}):(\d{2})[,.](\d{3})$/);

    if (!match) {
      throw new Error('Invalid SRT or VTT time format: "' + timestamp + '"');
    }

    var hours = match[1] ? parseInt(match[1], 10) * 3600000 : 0;
    var minutes = parseInt(match[2], 10) * 60000;
    var seconds = parseInt(match[3], 10) * 1000;
    var milliseconds = parseInt(match[4], 10);

    return hours + minutes + seconds + milliseconds;
  }

  /***/ }),
  /* 1 */
  /***/ (function(module, exports, __webpack_require__) {


  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.default = toSrtTime;

  var _zeroFill = __webpack_require__(2);

  var _zeroFill2 = _interopRequireDefault(_zeroFill);

  function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

  /**
   * Return the given milliseconds as SRT timestamp.
   * @param timestamp
   * @returns {string}
   */

  function toSrtTime(timestamp) {
    if (isNaN(timestamp)) {
      return timestamp;
    }

    var date = new Date(0, 0, 0, 0, 0, 0, timestamp);

    var hours = (0, _zeroFill2.default)(2, date.getHours());
    var minutes = (0, _zeroFill2.default)(2, date.getMinutes());
    var seconds = (0, _zeroFill2.default)(2, date.getSeconds());
    var ms = timestamp - (hours * 3600000 + minutes * 60000 + seconds * 1000);

    return hours + ':' + minutes + ':' + seconds + ',' + (0, _zeroFill2.default)(3, ms);
  } /**
     * Module dependencies.
     */

  /***/ }),
  /* 2 */
  /***/ (function(module, exports) {

  /**
   * Given a number, return a zero-filled string.
   * From http://stackoverflow.com/questions/1267283/
   * @param  {number} width
   * @param  {number} number
   * @return {string}
   */
  module.exports = function zeroFill (width, number, pad) {
    if (number === undefined) {
      return function (number, pad) {
        return zeroFill(width, number, pad)
      }
    }
    if (pad === undefined) pad = '0';
    width -= number.toString().length;
    if (width > 0) return new Array(width + (/\./.test(number) ? 2 : 1)).join(pad) + number
    return number + ''
  };


  /***/ }),
  /* 3 */
  /***/ (function(module, exports, __webpack_require__) {


  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.default = toVttTime;

  var _zeroFill = __webpack_require__(2);

  var _zeroFill2 = _interopRequireDefault(_zeroFill);

  function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

  /**
   * Return the given milliseconds as WebVTT timestamp.
   * @param timestamp
   * @returns {string}
   */

  function toVttTime(timestamp) {
    if (isNaN(timestamp)) {
      return timestamp;
    }

    var date = new Date(0, 0, 0, 0, 0, 0, timestamp);

    var hours = (0, _zeroFill2.default)(2, date.getHours());
    var minutes = (0, _zeroFill2.default)(2, date.getMinutes());
    var seconds = (0, _zeroFill2.default)(2, date.getSeconds());
    var ms = timestamp - (hours * 3600000 + minutes * 60000 + seconds * 1000);

    return hours + ':' + minutes + ':' + seconds + '.' + (0, _zeroFill2.default)(3, ms);
  } /**
     * Module dependencies.
     */

  /***/ }),
  /* 4 */
  /***/ (function(module, exports, __webpack_require__) {


  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.default = parseTimestamps;

  var _toMS = __webpack_require__(0);

  var _toMS2 = _interopRequireDefault(_toMS);

  function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

  /**
   * Timestamp regex
   * @type {RegExp}
   */

  var RE = /^((?:\d{2,}:)?\d{2}:\d{2}[,.]\d{3}) --> ((?:\d{2,}:)?\d{2}:\d{2}[,.]\d{3})(?: (.*))?$/;

  /**
   * parseTimestamps
   * @param value
   * @returns {{start: Number, end: Number}}
   */

  /**
   * Module dependencies.
   */

  function parseTimestamps(value) {
    var match = RE.exec(value);
    var cue = {
      start: (0, _toMS2.default)(match[1]),
      end: (0, _toMS2.default)(match[2])
    };
    if (match[3]) {
      cue.settings = match[3];
    }
    return cue;
  }

  /***/ }),
  /* 5 */
  /***/ (function(module, exports, __webpack_require__) {


  Object.defineProperty(exports, "__esModule", {
    value: true
  });

  var _toMS = __webpack_require__(0);

  Object.defineProperty(exports, 'toMS', {
    enumerable: true,
    get: function get() {
      return _interopRequireDefault(_toMS).default;
    }
  });

  var _toSrtTime = __webpack_require__(1);

  Object.defineProperty(exports, 'toSrtTime', {
    enumerable: true,
    get: function get() {
      return _interopRequireDefault(_toSrtTime).default;
    }
  });

  var _toVttTime = __webpack_require__(3);

  Object.defineProperty(exports, 'toVttTime', {
    enumerable: true,
    get: function get() {
      return _interopRequireDefault(_toVttTime).default;
    }
  });

  var _parse = __webpack_require__(6);

  Object.defineProperty(exports, 'parse', {
    enumerable: true,
    get: function get() {
      return _interopRequireDefault(_parse).default;
    }
  });

  var _stringify = __webpack_require__(7);

  Object.defineProperty(exports, 'stringify', {
    enumerable: true,
    get: function get() {
      return _interopRequireDefault(_stringify).default;
    }
  });

  var _stringifyVtt = __webpack_require__(8);

  Object.defineProperty(exports, 'stringifyVtt', {
    enumerable: true,
    get: function get() {
      return _interopRequireDefault(_stringifyVtt).default;
    }
  });

  var _resync = __webpack_require__(9);

  Object.defineProperty(exports, 'resync', {
    enumerable: true,
    get: function get() {
      return _interopRequireDefault(_resync).default;
    }
  });

  var _parseTimestamps = __webpack_require__(4);

  Object.defineProperty(exports, 'parseTimestamps', {
    enumerable: true,
    get: function get() {
      return _interopRequireDefault(_parseTimestamps).default;
    }
  });

  function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

  /***/ }),
  /* 6 */
  /***/ (function(module, exports, __webpack_require__) {


  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.default = parse;

  var _parseTimestamps = __webpack_require__(4);

  var _parseTimestamps2 = _interopRequireDefault(_parseTimestamps);

  function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

  /**
   * Parse a SRT or WebVTT string.
   * @param {String} srtOrVtt
   * @return {Array} subtitles
   */

  function parse(srtOrVtt) {
    if (!srtOrVtt) return [];

    var source = srtOrVtt.trim().concat('\n').replace(/\r\n/g, '\n').replace(/\n{3,}/g, '\n\n').replace(/^WEBVTT.*\n{2}/, '').split('\n');

    return source.reduce(function (captions, row, index) {
      var caption = captions[captions.length - 1];

      if (!caption.index) {
        if (/^\d+$/.test(row)) {
          caption.index = parseInt(row, 10);
          return captions;
        }
      }

      if (!caption.hasOwnProperty('start')) {
        Object.assign(caption, (0, _parseTimestamps2.default)(row));
        return captions;
      }

      if (row === '') {
        delete caption.index;
        if (index !== source.length - 1) {
          captions.push({});
        }
      } else {
        caption.text = caption.text ? caption.text + '\n' + row : row;
      }

      return captions;
    }, [{}]);
  } /**
     * Module dependencies.
     */

  /***/ }),
  /* 7 */
  /***/ (function(module, exports, __webpack_require__) {


  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.default = stringify;

  var _toSrtTime = __webpack_require__(1);

  var _toSrtTime2 = _interopRequireDefault(_toSrtTime);

  function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

  /**
   * Stringify the given array of captions.
   * @param {Array} captions
   * @return {String} srt
   */

  function stringify(captions) {
    return captions.map(function (caption, index) {
      return (index > 0 ? '\n' : '') + [index + 1, (0, _toSrtTime2.default)(caption.start) + ' --> ' + (0, _toSrtTime2.default)(caption.end), caption.text].join('\n');
    }).join('\n') + '\n';
  } /**
     * Module dependencies.
     */

  /***/ }),
  /* 8 */
  /***/ (function(module, exports, __webpack_require__) {


  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.default = stringifyVtt;

  var _toVttTime = __webpack_require__(3);

  var _toVttTime2 = _interopRequireDefault(_toVttTime);

  function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

  /**
   * Stringify the given array of captions to WebVTT format.
   * @param {Array} captions
   * @return {String} webVtt
   */

  function stringifyVtt(captions) {
    return 'WEBVTT\n\n' + captions.map(function (caption, index) {
      return (index > 0 ? '\n' : '') + [index + 1, (0, _toVttTime2.default)(caption.start) + ' --> ' + (0, _toVttTime2.default)(caption.end) + (caption.settings ? ' ' + caption.settings : ''), caption.text].join('\n');
    }).join('\n') + '\n';
  } /**
     * Module dependencies.
     */

  /***/ }),
  /* 9 */
  /***/ (function(module, exports, __webpack_require__) {


  Object.defineProperty(exports, "__esModule", {
    value: true
  });
  exports.default = resync;

  var _toMS = __webpack_require__(0);

  var _toMS2 = _interopRequireDefault(_toMS);

  function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

  /**
   * Resync the given subtitles.
   * @param captions
   * @param time
   * @returns {Array|*}
   */

  function resync(captions, time) {
    return captions.map(function (caption) {
      var start = (0, _toMS2.default)(caption.start) + time;
      var end = (0, _toMS2.default)(caption.end) + time;

      return Object.assign({}, caption, {
        start: start,
        end: end
      });
    });
  } /**
     * Module dependencies.
     */

  /***/ })
  /******/ ]);
  });
  });

  var Subtitle = unwrapExports(subtitle_bundle);
  var subtitle_bundle_1 = subtitle_bundle.Subtitle;

  var win;

  if (typeof window !== "undefined") {
      win = window;
  } else if (typeof commonjsGlobal !== "undefined") {
      win = commonjsGlobal;
  } else if (typeof self !== "undefined"){
      win = self;
  } else {
      win = {};
  }

  var window_1 = win;

  var isFunction_1 = isFunction;

  var toString = Object.prototype.toString;

  function isFunction (fn) {
    var string = toString.call(fn);
    return string === '[object Function]' ||
      (typeof fn === 'function' && string !== '[object RegExp]') ||
      (typeof window !== 'undefined' &&
       // IE8 and below
       (fn === window.setTimeout ||
        fn === window.alert ||
        fn === window.confirm ||
        fn === window.prompt))
  }

  var trim_1 = createCommonjsModule(function (module, exports) {
  exports = module.exports = trim;

  function trim(str){
    return str.replace(/^\s*|\s*$/g, '');
  }

  exports.left = function(str){
    return str.replace(/^\s*/, '');
  };

  exports.right = function(str){
    return str.replace(/\s*$/, '');
  };
  });
  var trim_2 = trim_1.left;
  var trim_3 = trim_1.right;

  var fnToStr = Function.prototype.toString;

  var constructorRegex = /^\s*class\b/;
  var isES6ClassFn = function isES6ClassFunction(value) {
  	try {
  		var fnStr = fnToStr.call(value);
  		return constructorRegex.test(fnStr);
  	} catch (e) {
  		return false; // not a function
  	}
  };

  var tryFunctionObject = function tryFunctionToStr(value) {
  	try {
  		if (isES6ClassFn(value)) { return false; }
  		fnToStr.call(value);
  		return true;
  	} catch (e) {
  		return false;
  	}
  };
  var toStr = Object.prototype.toString;
  var fnClass = '[object Function]';
  var genClass = '[object GeneratorFunction]';
  var hasToStringTag = typeof Symbol === 'function' && typeof Symbol.toStringTag === 'symbol';

  var isCallable = function isCallable(value) {
  	if (!value) { return false; }
  	if (typeof value !== 'function' && typeof value !== 'object') { return false; }
  	if (typeof value === 'function' && !value.prototype) { return true; }
  	if (hasToStringTag) { return tryFunctionObject(value); }
  	if (isES6ClassFn(value)) { return false; }
  	var strClass = toStr.call(value);
  	return strClass === fnClass || strClass === genClass;
  };

  var toStr$1 = Object.prototype.toString;
  var hasOwnProperty = Object.prototype.hasOwnProperty;

  var forEachArray = function forEachArray(array, iterator, receiver) {
      for (var i = 0, len = array.length; i < len; i++) {
          if (hasOwnProperty.call(array, i)) {
              if (receiver == null) {
                  iterator(array[i], i, array);
              } else {
                  iterator.call(receiver, array[i], i, array);
              }
          }
      }
  };

  var forEachString = function forEachString(string, iterator, receiver) {
      for (var i = 0, len = string.length; i < len; i++) {
          // no such thing as a sparse string.
          if (receiver == null) {
              iterator(string.charAt(i), i, string);
          } else {
              iterator.call(receiver, string.charAt(i), i, string);
          }
      }
  };

  var forEachObject = function forEachObject(object, iterator, receiver) {
      for (var k in object) {
          if (hasOwnProperty.call(object, k)) {
              if (receiver == null) {
                  iterator(object[k], k, object);
              } else {
                  iterator.call(receiver, object[k], k, object);
              }
          }
      }
  };

  var forEach = function forEach(list, iterator, thisArg) {
      if (!isCallable(iterator)) {
          throw new TypeError('iterator must be a function');
      }

      var receiver;
      if (arguments.length >= 3) {
          receiver = thisArg;
      }

      if (toStr$1.call(list) === '[object Array]') {
          forEachArray(list, iterator, receiver);
      } else if (typeof list === 'string') {
          forEachString(list, iterator, receiver);
      } else {
          forEachObject(list, iterator, receiver);
      }
  };

  var forEach_1 = forEach;

  var isArray = function(arg) {
        return Object.prototype.toString.call(arg) === '[object Array]';
      };

  var parseHeaders = function (headers) {
    if (!headers)
      return {}

    var result = {};

    forEach_1(
        trim_1(headers).split('\n')
      , function (row) {
          var index = row.indexOf(':')
            , key = trim_1(row.slice(0, index)).toLowerCase()
            , value = trim_1(row.slice(index + 1));

          if (typeof(result[key]) === 'undefined') {
            result[key] = value;
          } else if (isArray(result[key])) {
            result[key].push(value);
          } else {
            result[key] = [ result[key], value ];
          }
        }
    );

    return result
  };

  var immutable = extend;

  var hasOwnProperty$1 = Object.prototype.hasOwnProperty;

  function extend() {
      var target = {};

      for (var i = 0; i < arguments.length; i++) {
          var source = arguments[i];

          for (var key in source) {
              if (hasOwnProperty$1.call(source, key)) {
                  target[key] = source[key];
              }
          }
      }

      return target
  }

  var xhr = createXHR;
  // Allow use of default import syntax in TypeScript
  var default_1 = createXHR;
  createXHR.XMLHttpRequest = window_1.XMLHttpRequest || noop;
  createXHR.XDomainRequest = "withCredentials" in (new createXHR.XMLHttpRequest()) ? createXHR.XMLHttpRequest : window_1.XDomainRequest;

  forEachArray$1(["get", "put", "post", "patch", "head", "delete"], function(method) {
      createXHR[method === "delete" ? "del" : method] = function(uri, options, callback) {
          options = initParams(uri, options, callback);
          options.method = method.toUpperCase();
          return _createXHR(options)
      };
  });

  function forEachArray$1(array, iterator) {
      for (var i = 0; i < array.length; i++) {
          iterator(array[i]);
      }
  }

  function isEmpty(obj){
      for(var i in obj){
          if(obj.hasOwnProperty(i)) return false
      }
      return true
  }

  function initParams(uri, options, callback) {
      var params = uri;

      if (isFunction_1(options)) {
          callback = options;
          if (typeof uri === "string") {
              params = {uri:uri};
          }
      } else {
          params = immutable(options, {uri: uri});
      }

      params.callback = callback;
      return params
  }

  function createXHR(uri, options, callback) {
      options = initParams(uri, options, callback);
      return _createXHR(options)
  }

  function _createXHR(options) {
      if(typeof options.callback === "undefined"){
          throw new Error("callback argument missing")
      }

      var called = false;
      var callback = function cbOnce(err, response, body){
          if(!called){
              called = true;
              options.callback(err, response, body);
          }
      };

      function readystatechange() {
          if (xhr.readyState === 4) {
              setTimeout(loadFunc, 0);
          }
      }

      function getBody() {
          // Chrome with requestType=blob throws errors arround when even testing access to responseText
          var body = undefined;

          if (xhr.response) {
              body = xhr.response;
          } else {
              body = xhr.responseText || getXml(xhr);
          }

          if (isJson) {
              try {
                  body = JSON.parse(body);
              } catch (e) {}
          }

          return body
      }

      function errorFunc(evt) {
          clearTimeout(timeoutTimer);
          if(!(evt instanceof Error)){
              evt = new Error("" + (evt || "Unknown XMLHttpRequest Error") );
          }
          evt.statusCode = 0;
          return callback(evt, failureResponse)
      }

      // will load the data & process the response in a special response object
      function loadFunc() {
          if (aborted) return
          var status;
          clearTimeout(timeoutTimer);
          if(options.useXDR && xhr.status===undefined) {
              //IE8 CORS GET successful response doesn't have a status field, but body is fine
              status = 200;
          } else {
              status = (xhr.status === 1223 ? 204 : xhr.status);
          }
          var response = failureResponse;
          var err = null;

          if (status !== 0){
              response = {
                  body: getBody(),
                  statusCode: status,
                  method: method,
                  headers: {},
                  url: uri,
                  rawRequest: xhr
              };
              if(xhr.getAllResponseHeaders){ //remember xhr can in fact be XDR for CORS in IE
                  response.headers = parseHeaders(xhr.getAllResponseHeaders());
              }
          } else {
              err = new Error("Internal XMLHttpRequest Error");
          }
          return callback(err, response, response.body)
      }

      var xhr = options.xhr || null;

      if (!xhr) {
          if (options.cors || options.useXDR) {
              xhr = new createXHR.XDomainRequest();
          }else{
              xhr = new createXHR.XMLHttpRequest();
          }
      }

      var key;
      var aborted;
      var uri = xhr.url = options.uri || options.url;
      var method = xhr.method = options.method || "GET";
      var body = options.body || options.data;
      var headers = xhr.headers = options.headers || {};
      var sync = !!options.sync;
      var isJson = false;
      var timeoutTimer;
      var failureResponse = {
          body: undefined,
          headers: {},
          statusCode: 0,
          method: method,
          url: uri,
          rawRequest: xhr
      };

      if ("json" in options && options.json !== false) {
          isJson = true;
          headers["accept"] || headers["Accept"] || (headers["Accept"] = "application/json"); //Don't override existing accept header declared by user
          if (method !== "GET" && method !== "HEAD") {
              headers["content-type"] || headers["Content-Type"] || (headers["Content-Type"] = "application/json"); //Don't override existing accept header declared by user
              body = JSON.stringify(options.json === true ? body : options.json);
          }
      }

      xhr.onreadystatechange = readystatechange;
      xhr.onload = loadFunc;
      xhr.onerror = errorFunc;
      // IE9 must have onprogress be set to a unique function.
      xhr.onprogress = function () {
          // IE must die
      };
      xhr.onabort = function(){
          aborted = true;
      };
      xhr.ontimeout = errorFunc;
      xhr.open(method, uri, !sync, options.username, options.password);
      //has to be after open
      if(!sync) {
          xhr.withCredentials = !!options.withCredentials;
      }
      // Cannot set timeout with sync request
      // not setting timeout on the xhr object, because of old webkits etc. not handling that correctly
      // both npm's request and jquery 1.x use this kind of timeout, so this is being consistent
      if (!sync && options.timeout > 0 ) {
          timeoutTimer = setTimeout(function(){
              if (aborted) return
              aborted = true;//IE9 may still call readystatechange
              xhr.abort("timeout");
              var e = new Error("XMLHttpRequest timeout");
              e.code = "ETIMEDOUT";
              errorFunc(e);
          }, options.timeout );
      }

      if (xhr.setRequestHeader) {
          for(key in headers){
              if(headers.hasOwnProperty(key)){
                  xhr.setRequestHeader(key, headers[key]);
              }
          }
      } else if (options.headers && !isEmpty(options.headers)) {
          throw new Error("Headers cannot be set on an XDomainRequest object")
      }

      if ("responseType" in options) {
          xhr.responseType = options.responseType;
      }

      if ("beforeSend" in options &&
          typeof options.beforeSend === "function"
      ) {
          options.beforeSend(xhr);
      }

      // Microsoft Edge browser sends "undefined" when send is called with undefined value.
      // XMLHttpRequest spec says to pass null as body to indicate no body
      // See https://github.com/naugtur/xhr/issues/100.
      xhr.send(body || null);

      return xhr


  }

  function getXml(xhr) {
      // xhr.responseXML will throw Exception "InvalidStateError" or "DOMException"
      // See https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/responseXML.
      try {
          if (xhr.responseType === "document") {
              return xhr.responseXML
          }
          var firefoxBugTakenEffect = xhr.responseXML && xhr.responseXML.documentElement.nodeName === "parsererror";
          if (xhr.responseType === "" && !firefoxBugTakenEffect) {
              return xhr.responseXML
          }
      } catch (e) {}

      return null
  }

  function noop() {}
  xhr.default = default_1;

  var strictUriEncode = str => encodeURIComponent(str).replace(/[!'()*]/g, x => `%${x.charCodeAt(0).toString(16).toUpperCase()}`);

  var token = '%[a-f0-9]{2}';
  var singleMatcher = new RegExp(token, 'gi');
  var multiMatcher = new RegExp('(' + token + ')+', 'gi');

  function decodeComponents(components, split) {
  	try {
  		// Try to decode the entire string first
  		return decodeURIComponent(components.join(''));
  	} catch (err) {
  		// Do nothing
  	}

  	if (components.length === 1) {
  		return components;
  	}

  	split = split || 1;

  	// Split the array in 2 parts
  	var left = components.slice(0, split);
  	var right = components.slice(split);

  	return Array.prototype.concat.call([], decodeComponents(left), decodeComponents(right));
  }

  function decode(input) {
  	try {
  		return decodeURIComponent(input);
  	} catch (err) {
  		var tokens = input.match(singleMatcher);

  		for (var i = 1; i < tokens.length; i++) {
  			input = decodeComponents(tokens, i).join('');

  			tokens = input.match(singleMatcher);
  		}

  		return input;
  	}
  }

  function customDecodeURIComponent(input) {
  	// Keep track of all the replacements and prefill the map with the `BOM`
  	var replaceMap = {
  		'%FE%FF': '\uFFFD\uFFFD',
  		'%FF%FE': '\uFFFD\uFFFD'
  	};

  	var match = multiMatcher.exec(input);
  	while (match) {
  		try {
  			// Decode as big chunks as possible
  			replaceMap[match[0]] = decodeURIComponent(match[0]);
  		} catch (err) {
  			var result = decode(match[0]);

  			if (result !== match[0]) {
  				replaceMap[match[0]] = result;
  			}
  		}

  		match = multiMatcher.exec(input);
  	}

  	// Add `%C2` at the end of the map to make sure it does not replace the combinator before everything else
  	replaceMap['%C2'] = '\uFFFD';

  	var entries = Object.keys(replaceMap);

  	for (var i = 0; i < entries.length; i++) {
  		// Replace all decoded components
  		var key = entries[i];
  		input = input.replace(new RegExp(key, 'g'), replaceMap[key]);
  	}

  	return input;
  }

  var decodeUriComponent = function (encodedURI) {
  	if (typeof encodedURI !== 'string') {
  		throw new TypeError('Expected `encodedURI` to be of type `string`, got `' + typeof encodedURI + '`');
  	}

  	try {
  		encodedURI = encodedURI.replace(/\+/g, ' ');

  		// Try the built in decoder first
  		return decodeURIComponent(encodedURI);
  	} catch (err) {
  		// Fallback to a more advanced decoder
  		return customDecodeURIComponent(encodedURI);
  	}
  };

  function encoderForArrayFormat(options) {
  	switch (options.arrayFormat) {
  		case 'index':
  			return (key, value, index) => {
  				return value === null ? [
  					encode(key, options),
  					'[',
  					index,
  					']'
  				].join('') : [
  					encode(key, options),
  					'[',
  					encode(index, options),
  					']=',
  					encode(value, options)
  				].join('');
  			};
  		case 'bracket':
  			return (key, value) => {
  				return value === null ? [encode(key, options), '[]'].join('') : [
  					encode(key, options),
  					'[]=',
  					encode(value, options)
  				].join('');
  			};
  		default:
  			return (key, value) => {
  				return value === null ? encode(key, options) : [
  					encode(key, options),
  					'=',
  					encode(value, options)
  				].join('');
  			};
  	}
  }

  function parserForArrayFormat(options) {
  	let result;

  	switch (options.arrayFormat) {
  		case 'index':
  			return (key, value, accumulator) => {
  				result = /\[(\d*)\]$/.exec(key);

  				key = key.replace(/\[\d*\]$/, '');

  				if (!result) {
  					accumulator[key] = value;
  					return;
  				}

  				if (accumulator[key] === undefined) {
  					accumulator[key] = {};
  				}

  				accumulator[key][result[1]] = value;
  			};
  		case 'bracket':
  			return (key, value, accumulator) => {
  				result = /(\[\])$/.exec(key);
  				key = key.replace(/\[\]$/, '');

  				if (!result) {
  					accumulator[key] = value;
  					return;
  				}

  				if (accumulator[key] === undefined) {
  					accumulator[key] = [value];
  					return;
  				}

  				accumulator[key] = [].concat(accumulator[key], value);
  			};
  		default:
  			return (key, value, accumulator) => {
  				if (accumulator[key] === undefined) {
  					accumulator[key] = value;
  					return;
  				}

  				accumulator[key] = [].concat(accumulator[key], value);
  			};
  	}
  }

  function encode(value, options) {
  	if (options.encode) {
  		return options.strict ? strictUriEncode(value) : encodeURIComponent(value);
  	}

  	return value;
  }

  function decode$1(value, options) {
  	if (options.decode) {
  		return decodeUriComponent(value);
  	}

  	return value;
  }

  function keysSorter(input) {
  	if (Array.isArray(input)) {
  		return input.sort();
  	}

  	if (typeof input === 'object') {
  		return keysSorter(Object.keys(input))
  			.sort((a, b) => Number(a) - Number(b))
  			.map(key => input[key]);
  	}

  	return input;
  }

  function extract(input) {
  	const queryStart = input.indexOf('?');
  	if (queryStart === -1) {
  		return '';
  	}
  	return input.slice(queryStart + 1);
  }

  function parse(input, options) {
  	options = Object.assign({decode: true, arrayFormat: 'none'}, options);

  	const formatter = parserForArrayFormat(options);

  	// Create an object with no prototype
  	const ret = Object.create(null);

  	if (typeof input !== 'string') {
  		return ret;
  	}

  	input = input.trim().replace(/^[?#&]/, '');

  	if (!input) {
  		return ret;
  	}

  	for (const param of input.split('&')) {
  		let [key, value] = param.replace(/\+/g, ' ').split('=');

  		// Missing `=` should be `null`:
  		// http://w3.org/TR/2012/WD-url-20120524/#collect-url-parameters
  		value = value === undefined ? null : decode$1(value, options);

  		formatter(decode$1(key, options), value, ret);
  	}

  	return Object.keys(ret).sort().reduce((result, key) => {
  		const value = ret[key];
  		if (Boolean(value) && typeof value === 'object' && !Array.isArray(value)) {
  			// Sort object keys, not values
  			result[key] = keysSorter(value);
  		} else {
  			result[key] = value;
  		}

  		return result;
  	}, Object.create(null));
  }

  var extract_1 = extract;
  var parse_1 = parse;

  var stringify = (obj, options) => {
  	const defaults = {
  		encode: true,
  		strict: true,
  		arrayFormat: 'none'
  	};

  	options = Object.assign(defaults, options);

  	if (options.sort === false) {
  		options.sort = () => {};
  	}

  	const formatter = encoderForArrayFormat(options);

  	return obj ? Object.keys(obj).sort(options.sort).map(key => {
  		const value = obj[key];

  		if (value === undefined) {
  			return '';
  		}

  		if (value === null) {
  			return encode(key, options);
  		}

  		if (Array.isArray(value)) {
  			const result = [];

  			for (const value2 of value.slice()) {
  				if (value2 === undefined) {
  					continue;
  				}

  				result.push(formatter(key, value2, result.length));
  			}

  			return result.join('&');
  		}

  		return encode(key, options) + '=' + encode(value, options);
  	}).filter(x => x.length > 0).join('&') : '';
  };

  var parseUrl = (input, options) => {
  	return {
  		url: input.split('?')[0] || '',
  		query: parse(extract(input), options)
  	};
  };

  var queryString = {
  	extract: extract_1,
  	parse: parse_1,
  	stringify: stringify,
  	parseUrl: parseUrl
  };

  // GET /queue/${queue_id}/${url}.json
  function api(state, method, url, params, callback) {
      var uri = "https://" + get_hostname() + "/queue/" + get_queue_id() + "/" + url + ".json" + "?" + queryString.stringify(params);
      xhr({
          method: method,
          uri: uri,
          useXDR: true, // cross-domain, so file:// can reach karakara.org.uk
          json: true
      }, function (err, resp, body) {
          console.groupCollapsed("api(" + uri + ")");
          if (resp.statusCode === 200) {
              console.log(body.data);
              callback(body.data);
          } else {
              console.log(err, resp, body);
          }
          console.groupEnd();
      });
  }

  // turn milliseconds into {X}min / {X}sec
  function timedelta_str(timedelta) {
      var seconds_total = Math.floor(timedelta / 1000);
      var seconds = seconds_total % 60;
      var minutes = Math.floor(seconds_total / 60);
      if (minutes >= 1) {
          return minutes + "min";
      }
      if (seconds === 0) {
          return "Now";
      }
      return seconds + "sec";
  }

  // turn seconds into {MM}:{SS}
  function s_to_mns(t) {
      return Math.floor(t / 60) + ":" + (Math.floor(t % 60) + "").padStart(2, "0");
  }

  // find the path from the player to the media file
  function get_attachment(state, track, type) {
      for (var i = 0; i < track.attachments.length; i++) {
          if (track.attachments[i].type === type) {
              return get_protocol() + "//" + get_hostname() + "/files/" + track.attachments[i].location;
          }
      }
      return "";
  }

  // get_attachment(srt) + parse SRT file
  function get_lyrics(state, track) {
      var xhr$$1 = new XMLHttpRequest();
      var data = null;
      xhr$$1.open('GET', get_attachment(state, track, "srt"), false);
      xhr$$1.onload = function (e) {
          data = e.target.responseText;
      };
      xhr$$1.send();
      return data ? Subtitle.parse(data) : null;
  }

  // get a tag if it is defined, else blank
  function get_tag(tag) {
      if (tag) return tag[0];else return "";
  }

  // figure out where our server is, accounting for local file:// mode
  function get_protocol() {
      if (document.location.protocol === "file:") return "https:";else return document.location.protocol;
  }
  function get_hostname() {
      if (document.location.protocol === "file:") return "karakara.org.uk";else return document.location.hostname;
  }
  function get_queue_id() {
      if (document.location.protocol === "file:") return "demo";else return queryString.parse(location.search)["queue_id"];
  }

  // ====================================================================
  // State and state management functions
  // ====================================================================

  var state = {
      // global app bits
      connected: false,
      clicked: false,
      settings: {
          "karakara.player.title": "KaraKara",
          "karakara.player.theme": "metalghosts",
          "karakara.player.video.preview_volume": 0.2,
          "karakara.player.video.skip.seconds": 20,
          "karakara.player.autoplay": 30, // Autoplay after X seconds
          "karakara.player.subs_on_screen": true, // Set false if using podium
          "karakara.websocket.path": "/ws/",
          "karakara.websocket.port": null,
          "karakara.event.end": null
      },
      socket: null,

      // playlist screen
      queue: [],

      // video screen
      playing: false,
      paused: false,
      progress: 0
  };

  var actions = {
      // this has nothing to do with the player, we just need
      // to make sure that the user has clicked in order for
      // chrome to allow auto-play.
      click: function click() {
          return function () {
              return { clicked: true };
          };
      },

      // general application state
      get_state: function get_state() {
          return function (state) {
              return state;
          };
      },
      set_socket: function set_socket(value) {
          return function () {
              return { socket: value };
          };
      },
      set_connected: function set_connected(value) {
          return function () {
              return { connected: value };
          };
      },
      check_settings: function check_settings() {
          return function (state, actions) {
              api(state, "GET", "settings", {}, function (data) {
                  actions.set_settings(Object.assign(state.settings, data.settings));
              });
          };
      },
      set_settings: function set_settings(value) {
          return function () {
              return { settings: value };
          };
      },

      // current track controls
      play: function play() {
          return function (state) {
              return {
                  playing: true,
                  // if we're already playing, leave the state alone;
                  // if we're starting a new song, start it un-paused from 0s
                  paused: state.playing ? state.paused : false,
                  progress: state.playing ? state.progress : 0
              };
          };
      },
      pause: function pause() {
          return function (state) {
              var video = document.getElementsByTagName("video")[0];
              if (video) {
                  if (state.paused) {
                      video.play();
                  } else {
                      video.pause();
                  }
              }
              return { paused: !state.paused };
          };
      },
      stop: function stop() {
          return function () {
              return {
                  playing: false,
                  paused: false,
                  progress: 0
              };
          };
      },
      set_progress: function set_progress(value) {
          return function () {
              return { progress: value };
          };
      },
      seek_forwards: function seek_forwards(value) {
          return function (state, actions) {
              var skip = value || state.settings["karakara.player.video.skip.seconds"];
              var video = document.getElementsByTagName("video")[0];
              if (video) video.currentTime += skip;
              return { progress: state.progress + skip };
          };
      },
      seek_backwards: function seek_backwards(value) {
          return function (state, actions) {
              var skip = value || state.settings["karakara.player.video.skip.seconds"];
              var video = document.getElementsByTagName("video")[0];
              if (video) video.currentTime -= skip;
              return { progress: state.progress - skip };
          };
      },

      // playlist controls
      check_queue: function check_queue() {
          return function (state, actions) {
              api(state, "GET", "queue_items", {}, function (data) {
                  function merge_lyrics(item) {
                      item.track.lyrics = get_lyrics(state, item.track);
                      return item;
                  }
                  var queue_with_lyrics = data.queue.map(function (item) {
                      return merge_lyrics(item);
                  });
                  actions.set_queue(queue_with_lyrics);
              });
          };
      },
      set_queue: function set_queue(value) {
          return function () {
              return { queue: value };
          };
      },
      dequeue: function dequeue() {
          return function (state) {
              return {
                  // remove the first song
                  queue: state.queue.slice(1),
                  // and stop playing (same as .stop(), but we
                  // want to do it all in a single state update
                  // to avoid rendering an incomplete state)
                  playing: false,
                  paused: false,
                  progress: 0
              };
          };
      },

      // Tell the network what to do
      send: function send(value) {
          return function (state, actions) {
              console.log("websocket_send(" + value + ")");
              state.socket.send(value);
          };
      },
      send_ended: function send_ended(value) {
          return function (state, actions) {
              actions.dequeue();
              api(state, "PUT", "queue_items", {
                  "queue_item.id": state.queue[0].id,
                  "status": value,
                  "uncache": new Date().getTime()
              }, function (data) {
                  actions.check_queue();
              });
          };
      }
  };

  var show_tracks = 5;

  // ====================================================================
  // Common components
  // ====================================================================

  function _lineStyle(item, state) {
      var ts = state.progress * 1000;
      if (!state.playing) return "present";
      if (item.text === "-") return "past";
      if (item.start < ts && item.end > ts) return "present";
      if (item.end < ts) return "past";
      if (item.start > ts) return "future";
  }

  var Lyrics = function Lyrics(_ref) {
      var state = _ref.state;
      return h('div', { className: "lyrics" }, [h('ol', null, [state.queue[0].track.lyrics.map(function (item) {
          return h('li', { key: item.start, className: _lineStyle(item, state) }, [h('span', null, [item.text])]);
      })])]);
  };

  // ====================================================================
  // Screens
  // ====================================================================

  var ClickScreen = function ClickScreen(_ref2) {
      var state = _ref2.state,
          actions = _ref2.actions;
      return h('div', { className: "screen_title" }, [h('h1', { onclick: function onclick() {
              return actions.click();
          } }, ["Click to Activate"])]);
  };

  var TitleScreen = function TitleScreen(_ref3) {
      var state = _ref3.state,
          actions = _ref3.actions;
      return h('div', { className: "screen_title" }, [h('h1', null, [state.settings["karakara.player.title"]]), h('div', { id: "join_info" }, ["Join at ", h('strong', null, [get_hostname()]), " -" + ' ' + "Queue is ", h('strong', null, [get_queue_id()])])]);
  };

  var PreviewScreen = function PreviewScreen(_ref4) {
      var state = _ref4.state,
          actions = _ref4.actions;
      return h('div', { className: "screen_preview" }, [h('div', { className: "preview_holder" }, [h('video', { src: get_attachment(state, state.queue[0].track, 'preview'),
          poster: get_attachment(state, state.queue[0].track, 'thumbnail'),
          autoPlay: true,
          onloadstart: function onloadstart(e) {
              e.target.volume = state.settings["karakara.player.video.preview_volume"];
          },
          loop: true }), h('video', { src: get_attachment(state, state.queue[0].track, 'video'),
          preload: "auto", muted: true, style: { display: "none" } })]), h('div', { id: "playlist", key: "playlist" }, [h('ol', null, [state.queue.slice(0, show_tracks).map(function (item) {
          return h('li', { key: item.time_touched }, [h('img', { src: get_attachment(state, item.track, 'image') }), h('p', { className: "title" }, [get_tag(item.track.tags.title)]), h('p', { className: "from" }, [get_tag(item.track.tags.from)]), h('p', { className: "performer" }, [item.performer_name]), h('p', { className: "time" }, [h('span', null, [timedelta_str(item.total_duration * 1000)])])]);
      })])]), state.queue.length > show_tracks && h('div', { id: "playlist_obscured", key: "playlist_obscured" }, [h('ul', null, [state.queue.slice(show_tracks).map(function (item) {
          return h('li', { key: item.time_touched }, [item.performer_name]);
      })])]),

      /* key= to make sure this element stays put while the above may disappear */
      h('div', { id: "join_info", key: "join_info" }, ["Join at ", h('strong', null, [get_hostname()]), " -" + ' ' + "Queue is ", h('strong', null, [get_queue_id()]), state.settings["karakara.event.end"] && h('span', null, [h('br'), "Event ends at ", h('strong', null, [state.settings["karakara.event.end"]])])])]);
  };

  var VideoScreen = function VideoScreen(_ref5) {
      var state = _ref5.state,
          actions = _ref5.actions;
      return h('div', { className: "screen_video" }, [h('video', { src: get_attachment(state, state.queue[0].track, 'video'),
          autoPlay: true,
          ontimeupdate: function ontimeupdate(e) {
              return actions.set_progress(e.target.currentTime);
          },
          onended: function onended() {
              return actions.send_ended("ended");
          } }), h('div', { id: "seekbar", style: {
              left: state.progress / state.queue[0].track.duration * 100 + "%"
          } }), h('div', { id: "pimpkk", className: "pimp" }, ["KaraKara"]), h('div', { id: "pimpsong", className: "pimp" }, [get_tag(state.queue[0].track.tags.title), h('br'), "Performed by ", state.queue[0].performer_name]),
      /* too much on screen at once?
      <div id="pimpcontributor" className="pimp">
          Contributed by {get_tag(state.queue[0].track.tags.contributor)}
      </div>
      */
      state.settings["karakara.player.subs_on_screen"] && state.queue[0].track.lyrics ? Lyrics({ state: state }) : null]);
  };

  var PodiumScreen = function PodiumScreen(_ref6) {
      var state = _ref6.state,
          actions = _ref6.actions;
      return h('div', { className: "screen_podium" }, [h('h1', null, [state.queue[0].performer_name, " - ", get_tag(state.queue[0].track.tags.title)]),

      /*
      if we have lyrics, show them, else show the video,
      give the video key=playing so that it creates a new
      object when switching from preview to play
       */
      state.queue[0].track.lyrics ? Lyrics({ state: state }) : h('div', { className: "preview_holder" }, [h('video', { src: get_attachment(state, state.queue[0].track, 'video'),
          autoPlay: true, muted: !state.playing,
          key: state.playing })]), state.playing ? h('div', { className: "progressBar",
          style: { "background-position": 100 - state.progress / state.queue[0].track.duration * 100 + "%" } }, ["Track Playing", h('small', null, ["(", s_to_mns(state.progress), ' ', "/", ' ', s_to_mns(state.queue[0].track.duration), ")"])]) : h('div', { className: "startButton", onclick: function onclick() {
              return actions.send("play");
          },
          style: { "background-position": 100 - state.progress / state.settings["karakara.player.autoplay"] * 100 + "%" } }, [h('span', null, ["Press to Start", state.settings["karakara.player.autoplay"] === 0 ? h('small', null, ["(autoplay disabled)"]) : h('small', null, ["(autoplay in ", Math.ceil(state.settings["karakara.player.autoplay"] - state.progress), " seconds)"])])])]);
  };

  // ====================================================================
  // Decide which screen to use based on current state
  // ====================================================================

  function view(state, actions) {
      var screen = h('div', null, ["Unknown state :("]);

      if (!state.clicked) screen = ClickScreen({ state: state, actions: actions });else if (state.queue.length === 0) screen = TitleScreen({ state: state, actions: actions });else if (window.location.hash === "#podium") screen = PodiumScreen({ state: state, actions: actions });else if (state.queue.length > 0 && !state.playing) screen = PreviewScreen({ state: state, actions: actions });else if (state.queue.length > 0 && state.playing) screen = VideoScreen({ state: state, actions: actions });

      return h('div', { className: "theme-" + state.settings["karakara.player.theme"] }, [screen]);
  }

  var player = app(state, actions, view, document.body);
  window.player = player; // make this global for debugging


  // ====================================================================
  // Network controls
  // ====================================================================

  function create_websocket() {
      var settings = player.get_state().settings;
      var ws_path = settings['karakara.websocket.path'];
      var ws_port = settings['karakara.websocket.port'];

      if (!ws_port && !ws_path) {
          console.error("setup_websocket", "Websocket port or path not specified - remote control disabled");
          return;
      }

      var websocket_url = (get_protocol() === "http:" ? 'ws://' : 'wss://') + get_hostname() + (ws_port && !ws_path ? ":" + ws_port : "") + (ws_path ? ws_path : "");
      console.log("setup_websocket", websocket_url);

      var socket = new dist(websocket_url);
      socket.onopen = function () {
          console.log("websocket_onopen()");
          player.set_connected(true);
          // player.send("ping"); // auth doesn't actually happen until the first packet
          // now that we're connected, make sure state is in
          // sync for the websocket to send incremental updates
          player.check_settings();
          player.check_queue();
      };
      socket.onclose = function () {
          console.log("websocket_onclose()");
          player.set_connected(false);
      };
      socket.onmessage = function (msg) {
          var cmd = msg.data.trim();
          console.log("websocket_onmessage(" + cmd + ")");
          var commands = {
              "skip": player.dequeue,
              "play": player.play,
              "stop": player.stop,
              "pause": player.pause,
              "seek_forwards": player.seek_forwards,
              "seek_backwards": player.seek_backwards,
              "ended": player.dequeue,
              "queue_updated": player.check_queue,
              "settings": player.check_settings
          };
          if (cmd in commands) {
              commands[cmd]();
          } else {
              console.log("unknown command: " + cmd);
          }
      };
      return socket;
  }
  player.set_socket(create_websocket());

  // ====================================================================
  // Local controls
  // ====================================================================

  document.onkeydown = function (e) {
      var handled = true;
      switch (e.key) {
          case "s":
              player.dequeue();break; // skip
          //case "a"          : player.enqueue(); break; // add
          case "Enter":
              player.play();break;
          case "Escape":
              player.stop();break;
          case "ArrowLeft":
              player.seek_backwards();break;
          case "ArrowRight":
              player.seek_forwards();break;
          case "Space":
              player.pause();break;
          default:
              handled = false;
      }
      if (handled) {
          e.preventDefault();
      }
  };

  // ====================================================================
  // Auto-play for podium mode
  // ====================================================================

  if (window.location.hash === "#podium") {
      var FPS = 5;
      setInterval(function () {
          var state$$1 = player.get_state();
          if (state$$1.paused) return;
          if (!state$$1.playing) {
              if (state$$1.settings["karakara.player.autoplay"] === 0) return;
              if (state$$1.progress >= state$$1.settings["karakara.player.autoplay"]) {
                  player.send("play");
              } else {
                  player.set_progress(state$$1.progress + 1 / FPS);
              }
          } else {
              if (state$$1.progress >= state$$1.queue[0].track.duration) {
                  player.dequeue();
              } else {
                  player.set_progress(state$$1.progress + 1 / FPS);
              }
          }
      }, 1000 / FPS);
  }

}());
//# sourceMappingURL=player.js.map
