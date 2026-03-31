# FileServer

[Changelog](CHANGELOG.md)

中文 | [English](#english)

## 中文

FileServer 是一个基于 FastAPI 的轻量级文件管理服务，提供浏览器文件管理界面、运行时挂载路径管理、后台密码管理，以及适合 Windows 桌面环境的 EXE 打包与托盘运行能力。

### 功能特点

- 支持多个本地目录或网络目录挂载
- 支持图片、音频、视频、PDF、文本等常见文件预览
- 支持 Office 文件预览，优先通过 LibreOffice 转换为 PDF 后展示
- 支持 `DOC`、`DOCX`、`XLS`、`XLSX`、`PPT`、`PPTX` 等格式的兼容预览
- 对可写挂载点支持上传和删除
- 可在后台页面直接管理挂载路径，无需手改 `config.yaml`
- 支持后台修改管理员密码
- 运行时密码使用哈希存储
- 支持打包为 Windows `EXE`
- 启动后自动打开浏览器
- 支持系统托盘后台运行

### Office 预览说明

- Office 文件会优先尝试使用 LibreOffice 转换为 PDF，以获得更接近原稿版式的预览效果
- 如果 PDF 转换不可用，会回退到内置兼容预览逻辑
- 旧版 Office 文件会在需要时先转换为新格式再预览
- 发布时请保留完整 `dist` 目录，而不是只复制 `FileServer.exe`
- 若使用打包产物，请确保 `dist\LibreOffice` 目录和 `dist\FileServer.exe` 保持同级

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
- 运行时生成的安全密钥

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
dist\LibreOffice\
```

打包后的程序会：

- 在后台启动 FastAPI 服务
- 等待本地端口可访问后自动打开浏览器
- 在系统托盘中保持运行
- 优先使用随包携带的 LibreOffice 做 Office 转 PDF 预览

### 安全说明

- 后台修改后的密码使用 `PBKDF2-HMAC-SHA256` 哈希保存
- 运行时生成的密码和密钥不会以明文写入公开仓库
- 文件访问会限制在已配置的挂载根目录内
- 只有标记为可写的挂载点才允许上传和删除
- 登录、挂载管理、密码修改、上传、删除接口都带有 CSRF 防护

### 发布说明

示例配置文件中的密码和密钥均为占位内容，不包含真实可用凭据。部署前请根据自己的环境修改。

### 许可证

本项目使用 MIT License，详见 [LICENSE](LICENSE)。

---

## English

FileServer is a lightweight FastAPI-based file management service with a browser UI, runtime mount management, admin password management, and a Windows desktop packaging flow with tray support.

### Highlights

- Supports multiple local or network-mounted directories
- Preview support for images, audio, video, PDF, and text files
- Office preview with LibreOffice-first PDF rendering for better layout fidelity
- Compatible preview support for `DOC`, `DOCX`, `XLS`, `XLSX`, `PPT`, and `PPTX`
- Upload and delete support for writable mounts
- Runtime mount management from the admin page without editing `config.yaml`
- Admin password change from the web UI
- Runtime password storage with hashing
- Windows EXE packaging
- Auto-open browser on startup
- System tray background mode

### Office Preview Notes

- Office files try LibreOffice-to-PDF conversion first for a preview closer to the original layout
- If PDF conversion is unavailable, the app falls back to built-in compatibility preview logic
- Legacy Office files can be converted to newer formats before previewing
- When distributing the packaged app, keep the full `dist` directory instead of copying only `FileServer.exe`
- For packaged builds, `dist\LibreOffice` should stay next to `dist\FileServer.exe`

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
- runtime-generated secure secret key

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
dist\LibreOffice\
```

The packaged app:

- starts the FastAPI service in the background
- waits for the local port to become ready
- opens the browser automatically
- stays available from the system tray
- prefers the bundled LibreOffice runtime for Office-to-PDF preview

### Security Notes

- Passwords changed from the UI are stored using PBKDF2-HMAC-SHA256
- Runtime-generated passwords and secrets are not committed in plain text
- File access is constrained to configured mount roots
- Only writable mounts can upload or delete content
- Login and privileged operations are protected with CSRF validation

### Publishing Notes

Example configuration files only contain placeholder values and do not include real usable credentials. Replace them with your own environment-specific settings before deployment.

### License

This project is released under the MIT License. See [LICENSE](LICENSE).
