Page({
  data: {
    url: ""
  },
  onLoad: function(n) {
    var e = n.id,
      t = n.agencyId;
    if (null != t) try {
      wx.setStorageSync("agencyId", t)
    } catch (n) {} else try {
      t = wx.getStorageSync("agencyId")
    } catch (n) {}
    try {
      wx.setStorageSync("environment", "false" == e ? "false" : "true")
    } catch (n) {}
    null != t ? "false" === e ? (t = null == t ? 86 : t, this.setData({
      url: "https://edu.iyundong.me/wechat/#/user/mobile/user/mini?agencyId=".concat(t)
    })) : this.setData({
      url: "https://edu.ymq.me/wechat/#/user/mobile/user/mini?agencyId=".concat(t, "&t=").concat((new Date).getTime())
    }) : wx.showModal({
      title: "提示",
      content: "请返回重试",
      showCancel: !1
    })
  },
  onReady: function(n) {},
  onShow: function() {},
  bindmessage: function() {},
  endclick: function() {
    wx.redirectTo({
      url: "../index/index"
    })
  },
  onHide: function() {},
  onUnload: function() {},
  onPullDownRefresh: function() {},
  onReachBottom: function() {},
  onShareAppMessage: function() {}
});