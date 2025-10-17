var n = require("../@babel/runtime/helpers/typeof");
! function(t) {
  function r(n, t) {
    var r = (65535 & n) + (65535 & t);
    return (n >> 16) + (t >> 16) + (r >> 16) << 16 | 65535 & r
  }

  function e(n, t, e, u, o, f) {
    return r(function(n, t) {
      return n << t | n >>> 32 - t
    }(r(r(t, n), r(u, f)), o), e)
  }

  function u(n, t, r, u, o, f, c) {
    return e(t & r | ~t & u, n, t, o, f, c)
  }

  function o(n, t, r, u, o, f, c) {
    return e(t & u | r & ~u, n, t, o, f, c)
  }

  function f(n, t, r, u, o, f, c) {
    return e(t ^ r ^ u, n, t, o, f, c)
  }

  function c(n, t, r, u, o, f, c) {
    return e(r ^ (t | ~u), n, t, o, f, c)
  }

  function i(n, t) {
    n[t >> 5] |= 128 << t % 32, n[14 + (t + 64 >>> 9 << 4)] = t;
    var e, i, d, a, h, l = 1732584193,
      g = -271733879,
      v = -1732584194,
      m = 271733878;
    for (e = 0; e < n.length; e += 16) i = l, d = g, a = v, h = m, l = u(l, g, v, m, n[e], 7, -680876936), m = u(m, l, g, v, n[e + 1], 12, -389564586), v = u(v, m, l, g, n[e + 2], 17, 606105819), g = u(g, v, m, l, n[e + 3], 22, -1044525330), l = u(l, g, v, m, n[e + 4], 7, -176418897), m = u(m, l, g, v, n[e + 5], 12, 1200080426), v = u(v, m, l, g, n[e + 6], 17, -1473231341), g = u(g, v, m, l, n[e + 7], 22, -45705983), l = u(l, g, v, m, n[e + 8], 7, 1770035416), m = u(m, l, g, v, n[e + 9], 12, -1958414417), v = u(v, m, l, g, n[e + 10], 17, -42063), g = u(g, v, m, l, n[e + 11], 22, -1990404162), l = u(l, g, v, m, n[e + 12], 7, 1804603682), m = u(m, l, g, v, n[e + 13], 12, -40341101), v = u(v, m, l, g, n[e + 14], 17, -1502002290), l = o(l, g = u(g, v, m, l, n[e + 15], 22, 1236535329), v, m, n[e + 1], 5, -165796510), m = o(m, l, g, v, n[e + 6], 9, -1069501632), v = o(v, m, l, g, n[e + 11], 14, 643717713), g = o(g, v, m, l, n[e], 20, -373897302), l = o(l, g, v, m, n[e + 5], 5, -701558691), m = o(m, l, g, v, n[e + 10], 9, 38016083), v = o(v, m, l, g, n[e + 15], 14, -660478335), g = o(g, v, m, l, n[e + 4], 20, -405537848), l = o(l, g, v, m, n[e + 9], 5, 568446438), m = o(m, l, g, v, n[e + 14], 9, -1019803690), v = o(v, m, l, g, n[e + 3], 14, -187363961), g = o(g, v, m, l, n[e + 8], 20, 1163531501), l = o(l, g, v, m, n[e + 13], 5, -1444681467), m = o(m, l, g, v, n[e + 2], 9, -51403784), v = o(v, m, l, g, n[e + 7], 14, 1735328473), l = f(l, g = o(g, v, m, l, n[e + 12], 20, -1926607734), v, m, n[e + 5], 4, -378558), m = f(m, l, g, v, n[e + 8], 11, -2022574463), v = f(v, m, l, g, n[e + 11], 16, 1839030562), g = f(g, v, m, l, n[e + 14], 23, -35309556), l = f(l, g, v, m, n[e + 1], 4, -1530992060), m = f(m, l, g, v, n[e + 4], 11, 1272893353), v = f(v, m, l, g, n[e + 7], 16, -155497632), g = f(g, v, m, l, n[e + 10], 23, -1094730640), l = f(l, g, v, m, n[e + 13], 4, 681279174), m = f(m, l, g, v, n[e], 11, -358537222), v = f(v, m, l, g, n[e + 3], 16, -722521979), g = f(g, v, m, l, n[e + 6], 23, 76029189), l = f(l, g, v, m, n[e + 9], 4, -640364487), m = f(m, l, g, v, n[e + 12], 11, -421815835), v = f(v, m, l, g, n[e + 15], 16, 530742520), l = c(l, g = f(g, v, m, l, n[e + 2], 23, -995338651), v, m, n[e], 6, -198630844), m = c(m, l, g, v, n[e + 7], 10, 1126891415), v = c(v, m, l, g, n[e + 14], 15, -1416354905), g = c(g, v, m, l, n[e + 5], 21, -57434055), l = c(l, g, v, m, n[e + 12], 6, 1700485571), m = c(m, l, g, v, n[e + 3], 10, -1894986606), v = c(v, m, l, g, n[e + 10], 15, -1051523), g = c(g, v, m, l, n[e + 1], 21, -2054922799), l = c(l, g, v, m, n[e + 8], 6, 1873313359), m = c(m, l, g, v, n[e + 15], 10, -30611744), v = c(v, m, l, g, n[e + 6], 15, -1560198380), g = c(g, v, m, l, n[e + 13], 21, 1309151649), l = c(l, g, v, m, n[e + 4], 6, -145523070), m = c(m, l, g, v, n[e + 11], 10, -1120210379), v = c(v, m, l, g, n[e + 2], 15, 718787259), g = c(g, v, m, l, n[e + 9], 21, -343485551), l = r(l, i), g = r(g, d), v = r(v, a), m = r(m, h);
    return [l, g, v, m]
  }

  function d(n) {
    var t, r = "",
      e = 32 * n.length;
    for (t = 0; e > t; t += 8) r += String.fromCharCode(n[t >> 5] >>> t % 32 & 255);
    return r
  }

  function a(n) {
    var t, r = [];
    for (r[(n.length >> 2) - 1] = void 0, t = 0; t < r.length; t += 1) r[t] = 0;
    var e = 8 * n.length;
    for (t = 0; e > t; t += 8) r[t >> 5] |= (255 & n.charCodeAt(t / 8)) << t % 32;
    return r
  }

  function h(n) {
    var t, r, e = "0123456789abcdef",
      u = "";
    for (r = 0; r < n.length; r += 1) t = n.charCodeAt(r), u += e.charAt(t >>> 4 & 15) + e.charAt(15 & t);
    return u
  }

  function l(n) {
    return unescape(encodeURIComponent(n))
  }

  function g(n) {
    return function(n) {
      return d(i(a(n), 8 * n.length))
    }(l(n))
  }

  function v(n, t) {
    return function(n, t) {
      var r, e, u = a(n),
        o = [],
        f = [];
      for (o[15] = f[15] = void 0, u.length > 16 && (u = i(u, 8 * n.length)), r = 0; 16 > r; r += 1) o[r] = 909522486 ^ u[r], f[r] = 1549556828 ^ u[r];
      return e = i(o.concat(a(t)), 512 + 8 * t.length), d(i(f.concat(e), 640))
    }(l(n), l(t))
  }

  function m(n, t, r) {
    return t ? r ? v(t, n) : function(n, t) {
      return h(v(n, t))
    }(t, n) : r ? g(n) : function(n) {
      return h(g(n))
    }(n)
  }
  "function" == typeof define && define.amd ? define((function() {
    return m
  })) : "object" == ("undefined" == typeof module ? "undefined" : n(module)) && module.exports ? module.exports = m : (void 0).md5 = m
}();