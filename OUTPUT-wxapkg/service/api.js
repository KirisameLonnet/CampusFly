var e, l = (e = require("./domian")) && e.__esModule ? e : {
  default: e
};
var t = l.default.fitUrl,
  r = {
    makeStroll: t + "/webservice/wechat/student/stroll/makeStroll.do",
    saveStroll: t + "/webservice/wechat/student/stroll/saveStroll.do",
    submitStroll: t + "/webservice/wechat/student/stroll/submitStroll.do",
    checkStrollAbnormal: t + "/webservice/wechat/student/stroll/checkStrollAbnormal.do",
    renewal: l.default.userymq + "/public/token/renewal"
  };
module.exports = r;