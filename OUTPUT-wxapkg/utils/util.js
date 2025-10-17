require("../@babel/runtime/helpers/Arrayincludes");
var t = function(t) {
    return (t = t.toString())[1] ? t : "0" + t
  },
  n = Math.PI;

function e(t) {
  return t * n / 180
}
module.exports = {
  formatTime: function(n) {
    var e = n.getFullYear(),
      r = n.getMonth() + 1,
      a = n.getDate(),
      i = n.getHours(),
      o = n.getMinutes(),
      c = n.getSeconds();
    return [e, r, a].map(t).join("/") + " " + [i, o, c].map(t).join(":")
  },
  calcTimes: function(t) {
    if (0 === t || t < -1 || null == t) return "00:00:00";
    t = Math.floor(t);
    var n = Math.floor(t / 3600),
      e = n < 10 ? "0".concat(n) : n,
      r = t % 3600,
      a = Math.floor(r / 60),
      i = a < 10 ? "0".concat(a) : a,
      o = r % 60,
      c = o < 10 ? "0".concat(o) : o;
    return "".concat(e, ":").concat(i, ":").concat(c)
  },
  getFlatternDistance: function(t, n, r, a) {
    var i, o, c, u, l = e((t + r) / 2),
      s = e((t - r) / 2),
      f = e((n - a) / 2),
      d = Math.sin(s),
      h = Math.sin(f),
      M = Math.sin(l);
    i = (d *= d) * (1 - (h *= h)) + (1 - (M *= M)) * h, o = (1 - d) * (1 - h) + M * h;
    var g = 2 * (c = Math.atan(Math.sqrt(i / o))) * 6378137 * (1 + 1 / 298.257 * ((3 * (u = Math.sqrt(i * o) / c) - 1) / 2 / o * M * (1 - d) - (3 * u + 1) / 2 / i * (1 - M) * d));
    return Math.ceil(g)
  },
  appendParams: function(t, n) {
    if (n) {
      var e = t.split("#")[0],
        r = t.split("#")[1];
      for (var a in n) {
        var i = n[a];
        if (void 0 !== i) {
          var o = a + "=" + encodeURIComponent(i);
          if (e.indexOf("?") > 0) {
            var c = new RegExp(a + "=[-%.!~*'()\\w]*", "g");
            c.test(e) ? e = e.replace(c, o) : e += "&" + o
          } else e += "?" + o
        }
      }
      t = r ? e + "#" + r : e
    }
    return t
  },
  judgeAgencyId: function(t) {
    return ["null", null, "undefined", void 0, ""].includes(t) || t && Number(t) < 100
  }
};