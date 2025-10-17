var e, n = (e = require("../../utils/util")) && e.__esModule ? e : {
  default: e
};
Page({
  data: {
    url: ""
  },
  onLoad: function(e) {
    var t = this,
      o = e.id,
      a = e.agencyId;
    wx.removeStorage({
      key: "id"
    }), wx.removeStorage({
      key: "token"
    });
    try {
      wx.removeStorageSync("environment")
    } catch (e) {}
    if (null == a) try {
      a = wx.getStorageSync("agencyId")
    } catch (e) {}
    if (null == o) try {
      o = wx.getStorageSync("environment")
    } catch (e) {}
    n.default.judgeAgencyId(a) ? wx.showActionSheet({
      itemList: ["上海大学", "上海中医药大学"],
      success: function(e) {
        var n = e.tapIndex;
        a = [1977, 1036][n], t.goWebView(a, o)
      },
      fail: function(e) {
        var n = getCurrentPages(),
          o = n[n.length - 1];
        t.onLoad(o.options)
      }
    }) : this.goWebView(a, o)
  },
  goWebView: function(e, n) {
    try {
      wx.setStorageSync("agencyId", e), wx.setStorageSync("environment", "false" == n ? "false" : "true")
    } catch (e) {}
    wx.redirectTo({
      url: "/pages/fitnessWeb/fitnessWeb?agencyId=".concat(e, "&flag=").concat(n)
    })
  },
  onReady: function() {},
  onShow: function() {},
  onHide: function() {},
  onUnload: function() {},
  onPullDownRefresh: function() {},
  onReachBottom: function() {},
  onShareAppMessage: function() {}
});