var t = require("../../@babel/runtime/helpers/toConsumableArray"),
  e = i(require("../../utils/util")),
  n = i(require("../../service/api")),
  a = i(require("../../service/request"));

function i(t) {
  return t && t.__esModule ? t : {
    default: t
  }
}
getApp();
Page({
  data: {
    latitude: 0,
    longitude: 0,
    markers: [{
      iconPath: "https://mapapi.qq.com/web/lbs/javascriptGL/demo/img/start.png",
      id: 0,
      latitude: 0,
      longitude: 0,
      width: 25,
      height: 35
    }],
    polyline: [{
      points: [],
      color: "#3777FF",
      width: 6,
      arrowLine: !0,
      borderColor: "#fff",
      borderWidth: 5
    }],
    time: "00:00:00",
    timeNum: 0,
    timer: null,
    status: 0,
    gradeType: 0,
    strollDistance: 0,
    strollRecordId: 0,
    fitnessId: 0,
    startTemp: 0,
    submit_timer: null,
    submit_num: 0,
    agencyId: 0
  },
  onReady: function() {
    wx.setKeepScreenOn({
      keepScreenOn: !0
    }), this.mapCtx = wx.createMapContext("myMap")
  },
  onLoad: function(t) {
    var e = this,
      i = t.planId,
      o = t.token,
      s = t.urlFlag,
      c = t.agencyId;
    if (!i || "undefined" == i) try {
      i = wx.getStorageSync("id")
    } catch (t) {}
    if (!o) try {
      o = wx.getStorageSync("token")
    } catch (t) {}
    if (!s) try {
      s = wx.getStorageSync("environment")
    } catch (t) {}
    if (!c) try {
      c = wx.getStorageSync("agencyId")
    } catch (t) {}
    this.setData({
      fitnessId: i,
      agencyId: c
    });
    try {
      wx.setStorageSync("environment", "false" == s ? "false" : "true"), wx.setStorageSync("token", o), wx.setStorageSync("id", i)
    } catch (t) {}
    a.default.post(n.default.renewal, {
      token: o
    }), a.default.post(n.default.checkStrollAbnormal, {
      fitnessId: i
    }).then((function(t) {
      var n = t.data;
      0 === n.status ? 0 === n.detail.existStrollAbnormal ? e._initGetPos(!0) : e.getInfoOrStart(i, !0) : (e._initGetPos(!0), wx.showModal({
        title: "提示",
        content: "".concat(n.message),
        showCancel: !1
      }))
    })), wx.startLocationUpdate(), wx.startLocationUpdateBackground()
  },
  getInfoOrStart: function(i, o) {
    var s = this,
      c = this;
    a.default.post(n.default.makeStroll, {
      fitnessId: i
    }).then((function(n) {
      var a = n.data;
      if (0 === a.status) {
        var i = a.detail,
          l = i.strollDetail,
          r = null == i.submitTimestamp ? 0 : i.submitTimestamp - i.beginTimestamp;
        r = null == r ? 0 : r, r = Math.floor(r / 1e3);
        var u = e.default.calcTimes(r),
          d = "" === l || "{}" === l || null == l ? [] : JSON.parse(l).map,
          f = c.data.polyline,
          m = f[0].points;
        d.map((function(e) {
          m = [].concat(t(m), [{
            latitude: e.y,
            longitude: e.x
          }])
        })), f[0].points = m;
        var g = null == d[0] ? 0 : d[0].y,
          h = null == d[0] ? 0 : d[0].x,
          p = c.data.markers[0];
        p.latitude = g, p.longitude = h, c.setData({
          markers: [p],
          gradeType: i.gradeType,
          strollDistance: i.strollDistance,
          strollRecordId: i.strollRecordId,
          polyline: f,
          timeNum: r,
          time: u,
          longitude: h,
          latitude: g,
          startTemp: i.beginTimestamp
        }), o ? (s._initGetPos(0 === d.length), s._startMethods(1)) : (s._initGetPos(!1), s._startMethods(1))
      } else s._initGetPos(!0), wx.showModal({
        title: "提示",
        content: "".concat(a.message),
        showCancel: !1
      })
    }))
  },
  onHide: function() {},
  openConfirm: function() {
    wx.showModal({
      content: "检测到您没打开定位权限,无法获取位置，是否去设置打开？",
      confirmText: "确认",
      cancelText: "取消",
      success: function(t) {
        t.confirm && wx.openSetting({
          success: function(t) {}
        })
      }
    })
  },
  getPosChange: function() {
    var n = this;
    wx.onLocationChange((function(a) {
      if (a.longitude > 0) {
        var i = a.latitude,
          o = a.longitude,
          s = n.data.polyline,
          c = s[0].points,
          l = c[c.length - 1],
          r = null == l ? -1 : l.latitude,
          u = null == l ? -1 : l.longitude;
        if (r != i || u != o) {
          c = [].concat(t(c), [{
            latitude: i,
            longitude: o
          }]), s[0].points = c;
          var d = n.data.strollDistance,
            f = 0;
          null != l && (f = e.default.getFlatternDistance(r, u, i, o), f = isNaN(f) ? 0 : Math.ceil(.9 * f)), n.setData({
            longitude: o,
            latitude: i,
            polyline: s,
            strollDistance: d + f
          })
        }
      }
    }))
  },
  setRecordPath: function() {
    var t = this,
      e = this.data,
      n = e.status;
    e.submit_num;
    if (1 === n) {
      var a = 0;
      this.data.submit_timer = setInterval((function() {
        10 === (a += 1) && (clearInterval(t.data.submit_timer), t.commonRecord(!1))
      }), 1e3)
    }
  },
  setEndRun: function(t) {
    var e = this,
      i = t;
    1977 == e.data.agencyId && Number(t.strollDistance) > 8e3 && (i.strollDistance = 8e3), console.log("执行了", i), a.default.post(n.default.submitStroll, i).then((function(t) {
      var n = t.data;
      0 === n.status ? (clearInterval(e.data.timer), clearInterval(e.data.submit_timer), e.setData({
        status: 2
      }), wx.offLocationChange()) : wx.showModal({
        title: "提示",
        content: "".concat(n.message),
        showCancel: !1
      })
    }))
  },
  commonRecord: function(e, i) {
    var o = this,
      s = this.data,
      c = s.fitnessId,
      l = s.gradeType,
      r = s.strollRecordId,
      u = s.strollDistance,
      d = o.data.polyline[0].points,
      f = [],
      m = 0;
    d.map((function(e) {
      o.judgeIn(e.latitude, e.longitude) || (m += 1), f = [].concat(t(f), [{
        y: e.latitude,
        x: e.longitude
      }])
    }));
    var g = {
        map: f
      },
      h = {
        fitnessId: c,
        gradeType: l,
        strollDistance: u,
        submitTimestamp: Date.parse(new Date),
        strollRecordId: r,
        strollDetail: JSON.stringify(g)
      };
    e ? (i && (h.strollDistance = 0), m > d.length / 2 ? wx.showModal({
      title: "提示",
      content: "本次成绩无效，系统检测跑步数据异常，需进一步核实，如有疑问请及时联系管理员",
      confirmText: "确定结束",
      cancelText: "继续跑步",
      success: function(t) {
        t.confirm && (h.strollDistance = 0, o.setEndRun(h))
      }
    }) : o.setEndRun(h)) : (a.default.post(n.default.saveStroll, h), o.setRecordPath())
  },
  _startMethods: function(t) {
    var n = this;
    n.getPosChange(), n.data.timer = setInterval((function() {
      var t = n.data.startTemp,
        a = (Date.parse(new Date) - t) / 1e3,
        i = e.default.calcTimes(a);
      n.setData({
        timeNum: a,
        time: i
      })
    }), 1e3), n.setData({
      status: t
    }), n.setRecordPath()
  },
  startClick: function() {
    var t = this,
      e = t.data.fitnessId;
    e ? wx.showModal({
      title: "提示",
      content: "请先确认好地图内您所在的位置，如确认无误，请点击“开始”，如所在位置有偏差请点击地图右下角按钮更新您所在的位置；",
      confirmText: "开始",
      cancelText: "重新定位",
      success: function(n) {
        n.confirm ? (t.resetPosition(), t.winthInRange(e)) : n.cancel && t.resetPosition()
      }
    }) : wx.showModal({
      title: "提示",
      content: "未找到体测计划id",
      showCancel: !1
    })
  },
  judgeIn: function(t, e) {
    return t > 31.19141 && t < 31.193705 && e > 121.594352 && e < 121.596808 || t > 31.052121 && t < 31.053421 && e > 121.752672 && e < 121.753916 || t > 31.221011 && t < 31.222512 && e > 121.630334 && e < 121.632343 || t > 31.318217 && t < 31.31997 && e > 121.392548 && e < 121.393845 || t > 31.318391 && t < 31.320292 && e > 121.396041 && e < 121.39726 || t > 31.275604 && t < 31.277297 && e > 121.456016 && e < 121.457606 || t > 31.376768 && t < 31.378306 && e > 121.248733 && e < 121.250344
  },
  winthInRange: function(t) {
    var e = this;
    wx.getLocation({
      type: "gcj02",
      isHighAccuracy: !0,
      highAccuracyExpireTime: 5e3,
      success: function(n) {
        var a = n.latitude,
          i = n.longitude;
        e.judgeIn(a, i) ? e.getInfoOrStart(t, !1) : wx.showModal({
          title: "提示",
          content: "您当前位置不在跑步范围内,请在跑步范围内开始跑步；",
          showCancel: !1
        })
      },
      fail: function(t) {}
    })
  },
  endclick: function() {
    var t = this;
    wx.getLocation({
      type: "gcj02",
      isHighAccuracy: !0,
      highAccuracyExpireTime: 5e3,
      success: function(e) {
        var n = e.latitude,
          a = e.longitude;
        t.judgeIn(n, a) ? t.commonRecord(!0, !1) : wx.showModal({
          title: "提示",
          content: "您当前位置不在跑步范围内,请在跑步范围内结束；",
          confirmText: "仍然结束",
          cancelText: "重新定位",
          success: function(e) {
            e.confirm ? t.stillEnd() : e.cancel && t._initGetPos(!1)
          }
        })
      },
      fail: function(t) {}
    })
  },
  stillEnd: function() {
    var t = this;
    wx.showModal({
      title: "提示",
      content: "不在跑步范围内结束跑步，本次跑步距离会判定为不合格。",
      confirmText: "确认",
      cancelText: "取消",
      success: function(e) {
        e.confirm && t.commonRecord(!0, !0)
      }
    })
  },
  resetPosition: function() {
    var t = this.data.polyline[0].points,
      e = this.data.status;
    0 === t.length || 0 === e ? this._initGetPos(!0) : this._initGetPos(!1)
  },
  _initGetPos: function(t) {
    var e = this;
    wx.getLocation({
      type: "gcj02",
      isHighAccuracy: !0,
      highAccuracyExpireTime: 5e3,
      success: function(n) {
        if (e.mapCtx.moveToLocation(), t) {
          var a = n.latitude,
            i = n.longitude,
            o = e.data.markers[0];
          o.latitude = a, o.longitude = i;
          var s = e.data.polyline,
            c = s[0].points;
          return c = [{
            latitude: a,
            longitude: i
          }], s[0].points = c, e.setData({
            markers: [o],
            longitude: i,
            latitude: a,
            polyline: s
          }), n
        }
      },
      fail: function(t) {
        wx.getSetting({
          success: function(t) {
            t.authSetting["scope.userLocation"] || wx.authorize({
              scope: "scope.userLocation",
              success: function(t) {},
              fail: function(t) {
                e.openConfirm()
              }
            })
          },
          fail: function(t) {}
        })
      }
    })
  }
});