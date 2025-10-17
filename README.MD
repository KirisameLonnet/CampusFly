# 华体运动会-体育管理的逆向分析

* 有关校园跑，截止至笔者书写时间：2025年10月17日1：36AM，已知的，已上线的业务逻辑如下：

```javascript

   judgeIn: function(t, e) {
       return t > 31.19141 && t < 31.193705 && e > 121.594352 && e < 121.596808 || t > 31.052121 && t < 31.053421 && e > 121.752672 && e < 121.753916 || t >
     31.221011 && t < 31.222512 && e > 121.630334 && e < 121.632343 || t > 31.318217 && t < 31.31997 && e > 121.392548 && e < 121.393845 || t > 31.318391 && t <
     31.320292 && e > 121.396041 && e < 121.39726 || t > 31.275604 && t < 31.277297 && e > 121.456016 && e < 121.457606 || t > 31.376768 && t < 31.378306 && e >
     121.248733 && e < 121.250344
   }
```

> 该函数定义了多个坐标，如果用户当前的坐标（纬度 t 和经度 e）在这些区域中的任何一个之内，函数就会返回 true，否则返回 false。

```javascript
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
  }
```

> 上述为在指定区域内开始跑步：winthInRange 函数在开始跑步时，会先获取当前位置，然后调用 judgeIn 函数判断是否在允许的跑步区域内。

```javascript
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
  }
```

> 上述为跑步过程中的计时和数据收集：_startMethods 函数启动跑步后，会开始计时并实时更新跑步时间，同时启动位置变化监听和数据记录。

```javascript

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
  }

```

> 上述为数据收集和验证的核心逻辑：commonRecord 函数会遍历所有的路径点，计算出在围栏外的点的数量 m，如果 m 超过总路径点数量 d.length 的一半，则成绩无效。同时构建包含完整跑步数据的对象。

```javascript

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
  }

```

> 上述为结束跑步时的位置验证：endclick 函数在结束跑步时，会先判断当前位置。如果不在围栏内，则会警告用户，若用户执意结束，则调用 stillEnd 函数，最终将跑步距离判定为不合格（距离清零）。

```javascript

  setEndRun: function(t) {
    var e = this,
      i = t;
    1977 == e.data.agencyId && Number(t.strollDistance) > 8e3 && (i.strollDistance = 8e3), 
    console.log("执行了", i), 
    a.default.post(n.default.submitStroll, i).then((function(t) {
      var n = t.data;
      0 === n.status ? (clearInterval(e.data.timer), clearInterval(e.data.submit_timer), e.setData({
        status: 2
      }), wx.offLocationChange()) : wx.showModal({
        title: "提示",
        content: "".concat(n.message),
        showCancel: !1
      })
    }))
  }

```

> 上述为最终数据提交逻辑：setEndRun 函数首先检查是否为上海大学（agencyId=1977），如果是则限制最大跑步距离为8公里；然后调用 submitStroll 接口提交数据；成功则清理所有定时器和监听器，失败则显示错误信息。

三个守则：

* 在指定区域内开始跑步
* 一半以上跑步轨迹需在指定区域内
* 在指定区域内结束跑步
* 每次仅仅能上传8km的有效距离，超过8km自动截断，源码在下方部分

## 跑步数据上传API业务逻辑分析

* 上传跑步数据API（submitStroll）需要以下6个核心信息：

```javascript

  h = {
    fitnessId: c,                    // 体测计划ID
    gradeType: l,                    // 成绩类型
    strollDistance: u,               // 跑步距离(米)
    submitTimestamp: Date.parse(new Date),  // 提交时间戳
    strollRecordId: r,               // 跑步记录ID
    strollDetail: JSON.stringify(g)  // 轨迹详情(JSON字符串)
  };

```

> 上述数据结构为上传跑步数据的完整格式：fitnessId标识体测计划，gradeType标识成绩类型，strollDistance记录跑步距离，submitTimestamp记录提交时间，strollRecordId唯一标识跑步记录，strollDetail包含完整的GPS轨迹数据。

```javascript

  strollDetail: JSON.stringify({
    map: [
      { y: 31.19141, x: 121.594352 },   // 第一个轨迹点
      { y: 31.19142, x: 121.594353 },   // 第二个轨迹点
      // ... 更多轨迹点
    ]
  })

```

> 轨迹详情格式：每个轨迹点包含y(纬度)和x(经度)，所有轨迹点组成完整的跑步路径。

```javascript

  1977 == e.data.agencyId && Number(t.strollDistance) > 8e3 && (i.strollDistance = 8e3)

```

> 特殊处理：上海大学(agencyId=1977)的跑步距离最大限制为8公里，超过则自动截断。

上传跑步数据API需要的信息：

* **fitnessId**: 体测计划ID（必填）
* **gradeType**: 成绩类型（必填）
* **strollDistance**: 跑步距离，单位米（必填）
* **submitTimestamp**: 提交时间戳（必填）
* **strollRecordId**: 跑步记录ID（必填）
* **strollDetail**: GPS轨迹详情，JSON格式（必填）

想要构造有效的跑步数据，需要确保这6个字段都正确填写，特别是fitnessId和strollDetail这两个关键字段。
