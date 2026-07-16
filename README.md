# 两相交错并联 Buck 控制环路设计与仿真系统 (2-Phase Interleaved Buck Control & Simulation)

这是一个基于 **Streamlit** 开发的专业级双相交错并联 Buck 变换器小信号建模、频域环路设计与时域开关级暂态仿真工具。本项目集成数学推导、高精细传递函数求解、四阶龙格库塔（RK4）时域仿真以及自动化 PDF 报告导出，可直接使用真实 MCU 固件控制常数进行在线调试。

## 🚀 快速开始

### 本地直接运行
1. **安装 Python 3.10+**。
2. **安装依赖包**：
   ```bash
   pip install -r requirements.txt
   ```
3. **启动应用**：
   ```bash
   streamlit run app.py
   ```
   启动后可在浏览器中访问 `http://localhost:8501`。

---

## 🐳 容器化部署 (Docker)

项目已内置 `Dockerfile`。可直接打包并运行：

1. **构建镜像**：
   ```bash
   docker build -t 2ph-buck-sim:latest .
   ```
2. **启动容器**（映射宿主机 8501 端口）：
   ```bash
   docker run -d -p 8501:8501 --name buck-simulator 2ph-buck-sim:latest
   ```
   随后便可通过服务器 IP 访问（例如 `http://<服务器IP>:8501`），供全组同事使用。

---

## ☁️ 云端一键发布 (Streamlit Community Cloud - 推荐且免费)

如果希望直接发布到公网，且不需要租用服务器，可使用 Streamlit 官方提供的免费托管服务：

1. **新建 GitHub 仓库**并将本项目全部代码上传（需包含 `requirements.txt`）。
2. 登录 [Streamlit Share](https://share.streamlit.io/)，点击 **"Create App"**。
3. 选择对应的 GitHub 仓库、分支（如 `main`）以及入口文件 `app.py`。
4. 点击 **"Deploy"**，等待数分钟，即可获得一个永久公开的网址（例如 `https://yourname-2ph-buck-sim.streamlit.app`）。

> **💡 安全建议**：如果代码中涉及敏感算法或参数，可在 Streamlit Cloud 的设置中配置 **Google Auth / Email Whitelist**（邮箱白名单）以保护数据不被外部公开访问。
