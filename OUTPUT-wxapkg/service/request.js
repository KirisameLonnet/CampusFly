var t, e = (t = require("../lib/md5")) && t.__esModule ? t : {
  default: t
};
var n = {
  Accept: "*/*;",
  "Content-Type": "application/json; charset=UTF-8"
};

function o(t, n, o) {
  for (var r = Object.assign({}, {
      snTime: n,
      token: o
    }, t), s = "", i = Object.keys(r).sort(), a = i.length, u = 0; u < a; u++) s += i[u] + "=" + r[i[u]] + "&";
  return s = s.substring(0, s.length - 1), (0, e.default)(s)
}

function r(t) {
  var e = "",
    n = (new Date).getTime(),
    r = "";
  try {
    var s = wx.getStorageSync("token");
    s && (r = s)
  } catch (t) {}
  void 0 !== r && "" !== r && (e = r);
  var i = {
    body: t,
    header: {
      token: e,
      snTime: n,
      sn: o(t, n, e),
      from: "wx"
    }
  };
  return JSON.stringify(i)
}
var s = {
  post: function(t, o) {
    var s = r(o);
    return n["X-Sn-Verify"] = (0, e.default)(s), new Promise((function(e, o) {
      wx.request({
        method: "post",
        url: t,
        data: s,
        header: n,
        success: function(t) {
          (t.statusCode < 200 || t.statusCode >= 300) && wx.showToast({
            title: "网络服务器错误",
            icon: "none",
            duration: 2e3
          }), e(t)
        },
        fail: function(t) {
          console.log(t), wx.showToast({
            title: JSON.stringify(t),
            icon: "none",
            duration: 4e3
          }), o(t)
        }
      })
    }))
  }
};
module.exports = s;