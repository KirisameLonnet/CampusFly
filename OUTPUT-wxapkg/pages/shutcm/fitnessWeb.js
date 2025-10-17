Page({
  data: {
    url: ""
  },
  onLoad: function(n) {
    wx.setStorageSync("agencyId", "1036"), this.setData({
      url: "https://edu.ymq.me/wechat/#/?agencyId=".concat(1036, "&ismini=true&t=").concat((new Date).getTime())
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