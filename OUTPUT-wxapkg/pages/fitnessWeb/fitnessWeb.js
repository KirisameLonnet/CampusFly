var t, n = (t = require("../../utils/util")) && t.__esModule ? t : {
  default: t
};
Page({
  data: {
    url: "",
    privacyContractName: "",
    showPrivacy: !1,
    agencyId: 1036,
    flag: "true"
  },
  onLoad: function(t) {
    var n = this,
      a = t.flag,
      e = t.agencyId;
    if (null == e) try {
      e = wx.getStorageSync("agencyId")
    } catch (t) {}
    if (null == a) try {
      a = wx.getStorageSync("environment")
    } catch (t) {}
    wx.getPrivacySetting({
      success: function(t) {
        console.log(t), t.needAuthorization ? n.setData({
          privacyContractName: t.privacyContractName,
          showPrivacy: t.needAuthorization,
          agencyId: e,
          flag: a
        }) : n.setDataUrl(e, a)
      },
      fail: function() {},
      complete: function() {}
    })
  },
  setDataUrl: function(t, a) {
    var e = this;
    n.default.judgeAgencyId(t) ? wx.showActionSheet({
      itemList: ["上海大学", "上海中医药大学"],
      success: function(t) {
        var n = [1977, 1036][t.tapIndex];
        e.setData({
          url: "https://edu.ymq.me/wechat/#/?agencyId=".concat(n, "&ismini=true&t=").concat((new Date).getTime())
        })
      },
      fail: function(t) {
        var n = getCurrentPages(),
          a = n[n.length - 1];
        e.onLoad(a.options)
      }
    }) : e.setData({
      url: "https://edu.ymq.me/wechat/#/?agencyId=".concat(t, "&ismini=true&t=").concat((new Date).getTime())
    })
  },
  openPrivacyContract: function() {
    wx.openPrivacyContract({
      fail: function() {
        wx.showToast({
          title: "遇到错误",
          icon: "error"
        })
      }
    })
  },
  exitMiniProgram: function() {
    wx.exitMiniProgram()
  },
  handleAgreePrivacyAuthorization: function() {
    this.setData({
      showPrivacy: !1
    }), this.setDataUrl(this.data.agencyId, this.data.flag)
  },
  onReady: function() {},
  onShow: function() {},
  onHide: function() {},
  onUnload: function() {},
  onPullDownRefresh: function() {},
  onReachBottom: function() {},
  onShareAppMessage: function() {}
});