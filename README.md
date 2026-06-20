# TikTokAutoSparkWeb visible chrome

抖音火花助手 Web 管理平台，基于 Vue 3 + Element Plus 构建，提供抖音好友火花自动续期的可视化管理系统。

这个仓库是可视化 Chrome 版本，后端通过 Selenium 驱动本机或服务器上的真实 Chrome 页面，方便完成抖音扫码登录和短信二次验证。

**📨 如果该项目对您有帮助,感谢您留下Start🌟**

# 法律声明

**重要提示**：本程序仅供个人学习和研究使用。请严格遵守相关法律法规，不得将本程序用于任何违法或侵权行为。如有任何侵权问题，请及时通过以下方式联系我：
- **邮箱**：3595655855@qq.com
- **群聊**: 1061290461
---
## 界面截图
<img width="2356" height="1238" alt="image" src="https://github.com/user-attachments/assets/49d3066e-ecef-42d6-a983-b3a4ae7b08a3" />

## 默认信息
账户: admin 密码:123456

## 平台支持

- 支持 Windows
- 支持 Linux
- 不依赖 Windows 专有的 Edge Driver 路径
- Linux 服务器部署时需要可用的图形显示环境，因为这里使用的是可视化 Chrome，不是 headless 模式

Linux 下如果没有桌面环境，请提前准备 X11/Xvfb。
后端会优先使用显式传入的 `DISPLAY`，也会自动尝试常见的 `:91`、`:99`、`:1`。

## 功能特性

### 账户管理
- 扫码登录（抖音 App 扫码授权）
- 手机号登录
- 手动登录（Base64Cookie 方式）
- Cookie 一键导出
- 登录状态实时监测
- 上次登录 IP 记录
- 管理员密码修改

### 好友管理
- 好友列表展示（头像、火花天数）
- 好友搜索过滤
- 实时刷新好友数据
- 一键发送消息

### 定时任务
- 为好友创建每日定时发送任务
- 支持自定义消息内容（留空使用每日名言）
- 修改已有任务执行时间
- 删除定时任务
- 最近任务快捷入口

### 首页看板
- 浏览器/登录状态监测
- 好友数量 / 定时任务数量统计
- 快速操作入口
- 系统运行信息（版本、在线时长）

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | Vue 3 (Composition API) |
| UI 组件库 | Element Plus |
| 状态管理 | Pinia |
| 构建工具 | Vite |
| 路由 | Vue Router |
| HTTP 客户端 | Axios |

---

## 项目结构

```
.
├── src/                        # 前端页面与状态管理
├── public/                     # 前端静态资源
├── backend.py                  # FastAPI + Selenium 后端
├── requirements.txt            # 后端依赖
├── start-backend.ps1           # Windows 启动脚本
├── start-backend.sh            # Linux 启动脚本
├── LOCAL_RUN.md                # 本地运行补充说明
├── dist/                       # 前端生产构建产物
├── vite.config.js              # Vite 配置（含 API 代理）
└── package.json
```

---

## 快速开始

### 环境要求
- Node.js 18+
- Python 3.10+
- Google Chrome
- 与 Chrome 版本匹配的 Chromedriver，并确保可通过 `PATH` 找到，或显式传入环境变量

可选环境变量：

```bash
CHROME_BINARY=/path/to/chrome
CHROMEDRIVER_PATH=/path/to/chromedriver
CHROME_PROFILE_DIR=./chrome-profile
PORT=9844
DISPLAY=:91
```

### Windows 启动

```powershell
.\start-backend.ps1
npm install
npm run dev
```

打开 `http://localhost:5173`。

### Linux 启动

```bash
chmod +x ./start-backend.sh
./start-backend.sh
npm install
npm run dev
```

打开 `http://localhost:5173`。

### Linux 服务器额外说明

这个版本依赖可视化 Chrome 页面，不是 headless 模式。

如果你部署在 Linux 服务器上，请确保满足以下任一条件：

- 已有桌面会话并能提供 `DISPLAY`
- 已提前启动 Xvfb

如果没有可用显示环境，后端初始化浏览器时会失败。

### 生产构建

```bash
npm run build
```

产物输出到 `dist/` 目录，可部署至任意静态服务器。

---

## API 代理配置

开发环境下 Vite 自动将 `/api` 代理至后端（`vite.config.js`）：
如有相同替换即可
```js
        location / {
            index index.php index.html;
            try_files $uri $uri/ /index.html;
            autoindex  off;
            .......
          }
        location /api/ {
            proxy_pass http://127.0.0.1:9844/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_connect_timeout 60s;
            proxy_read_timeout 60s;
        }
```

> 后端默认端口为 `9844`，请确保 FastAPI 后端已启动并监听该端口。
> Linux 服务器场景下，也请确认 Chrome 可正常连接到已有显示环境。

---

## 页面路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/login` | 登录页 | 管理员账户登录 |
| `/home` | 首页 | 状态看板、快速操作 |
| `/friends` | 好友列表 | 查看好友、发送消息 |
| `/tasks` | 定时任务 | 添加/修改/删除任务 |
| `/settings` | 设置 | 登录管理、密码修改 |

---

## License

MIT
