Page({
  data: {
    stuNo: "",
    planId: 0
  },
  onLoad: function(t) {
    t.planId && this.setData({
      planId: t.planId
    })
  },
  bindKeyInput: function(t) {
    this.setData({
      stuNo: t.detail.value
    })
  },
  startClick: function() {
    "" !== this.data.stuNo ? this.hasGetStuNo(this.data.stuNo) : wx.showToast({
      title: "请输入学号",
      icon: "none",
      duration: 2e3
    })
  },
  scanClick: function() {
    var t = this;
    wx.scanCode({
      success: function(n) {
        var o = n.result;
        t.hasGetStuNo(o)
      }
    })
  },
  hasGetStuNo: function(t) {
    var n = this.data.planId;
    wx.redirectTo({
      url: "/pages/score/score?stuNo=".concat(t, "&planId=").concat(n)
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