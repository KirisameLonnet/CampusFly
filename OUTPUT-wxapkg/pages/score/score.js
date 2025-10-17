Page({
  data: {
    url: ""
  },
  onLoad: function(n) {
    var t = n.stuNo,
      o = n.planId,
      a = "true";
    try {
      a = wx.getStorageSync("environment")
    } catch (n) {}
    "false" === a ? this.setData({
      url: "https://edu.iyundong.me/wechat/#/fitness?stuNo=".concat(t, "&planId=").concat(o)
    }) : this.setData({
      url: "https://edu.ymq.me/wechat/#/fitness?stuNo=".concat(t, "&planId=").concat(o)
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