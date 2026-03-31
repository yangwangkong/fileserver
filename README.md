# FileServer

中文 | [English](#english)

## 中文

FileServer 是一个基于 FastAPI 的轻量级文件管理服务，提供浏览器文件管理界面、运行时挂载路径管理、密码管理，以及适合 Windows 桌面环境的 EXE 打包与托盘运行能力。

### 功能特点

- 支持多个本地目录或网络目录挂载
- 支持图片、音频、视频、PDF、文本等常见文件预览
- 可对可写挂载点执行上传和删除
- 可在后台页面直接管理挂载路径，无需手改 `config.yaml`
- 支持后台修改管理员密码
- 运行时密码使用哈希存储
- 支持打包为 Windows `EXE`
- 启动后自动打开浏览器
- 支持系统托盘后台运行

### 适用场景

这个项目适合以下场景：

- 局域网内部文件浏览
- 个人电脑上的轻量文件门户
- 不希望部署复杂网盘系统时的简易替代方案

### 项目结构

```text
fileserver/
|-- main.py
|-- config.py
|-- config.yaml
|-- requirements.txt
|-- build_exe.ps1
|-- routers/
|   |-- auth.py
|   |-- files.py
|   `-- admin.py
`-- templates/
    |-- base.html
    |-- index.html
    |-- login.html
    |-- preview.html
    `-- settings.html
```

### 配置说明

`config.yaml` 是基础配置文件。

程序运行过程中，用户在后台修改的内容会写入 `runtime_config.yaml`，包括：

- 挂载点配置
- 密码哈希

这样可以做到：

- 仓库中的默认配置保持稳定
- 后台修改不会覆盖源码中的基础配置

### 从源码运行

安装依赖：

```powershell
pip install -r requirements.txt
```

启动程序：

```powershell
python main.py
```

访问地址：

```text
http://127.0.0.1:8591
```

### 构建 Windows EXE

```powershell
.\build_exe.ps1
```

生成文件：

```text
dist\FileServer.exe
```

打包后的程序会：

- 在后台启动 FastAPI 服务
- 等待本地端口可访问后自动打开浏览器
- 在系统托盘中保持运行

### 安全说明

- 后台修改后的密码使用 `PBKDF2-HMAC-SHA256` 哈希保存
- 运行时密码不会以明文形式写入公开仓库
- 文件访问会限制在已配置的挂载根目录内
- 只有标记为可写的挂载点才允许上传和删除

### 发布说明

示例配置文件中的密码和密钥均为占位内容，不包含真实可用凭据。部署前请根据自己的环境修改。

### 许可证

本项目使用 MIT License，详见 [LICENSE](LICENSE)。

---

## English

FileServer is a lightweight FastAPI-based file management service with a browser UI, runtime mount management, password management, and a Windows desktop packaging flow with tray support.

### Highlights

- Supports multiple local or network-mounted directories
- Preview support for images, audio, video, PDF, and text files
- Upload and delete support for writable mounts
- Runtime mount management from the admin page without editing `config.yaml`
- Admin password change from the web UI
- Runtime password storage with hashing
- Windows EXE packaging
- Auto-open browser on startup
- System tray background mode

### Typical Use Cases

This project is suitable for:

- lightweight LAN file browsing
- personal workstation file portals
- simple internal file access without deploying a large storage platform

### Project Structure

```text
fileserver/
|-- main.py
|-- config.py
|-- config.yaml
|-- requirements.txt
|-- build_exe.ps1
|-- routers/
|   |-- auth.py
|   |-- files.py
|   `-- admin.py
`-- templates/
    |-- base.html
    |-- index.html
    |-- login.html
    |-- preview.html
    `-- settings.html
```

### Configuration Model

`config.yaml` is the base configuration file.

At runtime, user-managed settings are written to `runtime_config.yaml`, including:

- mount definitions
- password hash

This keeps repository defaults separate from runtime-only settings changed through the admin UI.

### Run From Source

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the server:

```powershell
python main.py
```

Open:

```text
http://127.0.0.1:8591
```

### Build the Windows EXE

```powershell
.\build_exe.ps1
```

Build output:

```text
dist\FileServer.exe
```

The packaged app:

- starts the FastAPI service in the background
- waits for the local port to become ready
- opens the browser automatically
- stays available from the system tray

### Security Notes

- Passwords changed from the UI are stored using PBKDF2-HMAC-SHA256
- Runtime-generated passwords are not committed in plain text
- File access is constrained to configured mount roots
- Only writable mounts can upload or delete content

### Publishing Notes

Example configuration files only contain placeholder values and do not include real usable credentials. Replace them with your own environment-specific settings before deployment.

### License

This project is released under the MIT License. See [LICENSE](LICENSE).
