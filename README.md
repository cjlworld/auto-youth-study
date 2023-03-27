# 青春浙江定时打卡并推送消息至钉钉

感谢 项目 [浙江/上海青年大学习一键打卡](https://github.com/lthero-big/ZheJiangYouthstudyAutoSign)

本项目为该项目的简单改版。

1. 添加了一个获取积分的步骤，使得在打卡前后都获取一次积分，便于判断打卡结果。
2. 打卡后由发送邮件变为发送给 Dingding 机器人。

运行环境：

本项目部署于 linux 服务器上，须在环境变量中添加 `DING_WEBHOOK` 以及 `DING_SECRET` (分别对应 钉钉机器人的 webhook 和 签)

具体运行方式与原项目相同，再次感谢 [浙江/上海青年大学习一键打卡](https://github.com/lthero-big/ZheJiangYouthstudyAutoSign)。
