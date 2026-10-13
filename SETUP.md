# 安装到真正的 GitHub 个人主页

目标：https://github.com/Rocdna
主页仓库：https://github.com/Rocdna/Rocdna

## 1. 上传文件

将本目录内容放进公开仓库 Rocdna/Rocdna 的根目录。README.md 必须在根目录，不能多套一层文件夹。保留 .github/workflows/refresh-profile.yml。

Windows 推荐通过 VSCode / Git 提交：

```powershell
git clone https://github.com/Rocdna/Rocdna.git
cd Rocdna
# 将解压目录的内容复制到当前目录（包括 .github）
git add .
git commit -m "feat: add anime GitHub profile"
git push
```

如果仓库已经在本地，进入现有目录后先 git pull，再复制文件并提交。
如果仓库尚未初始化，也可以在 GitHub 的 Add file → Upload files 上传。网页提交无法添加工作流时，用本地 Git 提交。

## 2. 运行自动更新

Actions → Refresh Profile → Run workflow。
首次运行成功后，README 会自动加入贪吃蛇动画并重新生成项目卡片。之后每天北京时间 04:17 更新；GitHub 定时任务可能延迟，因此这属于定时自动更新，不能保证实时。
项目卡片展示全部非 Fork 公开仓库（排除主页仓库本身），按创建时间从新到旧排列。新建仓库会在下一次成功刷新后加入；删除、转为私有的仓库会移除。名称、描述、主语言和 Stars 均来自 GitHub API。
手动运行工作流可以提前刷新，无需等待下一次定时任务。

工作流也支持 `repository_dispatch`，事件类型为 `refresh-profile`。如果之后配置能够接收仓库创建事件的 GitHub App / 外部服务，可由它调用 `POST /repos/Rocdna/Rocdna/dispatches`，请求体为 `{"event_type":"refresh-profile"}`，触发更新。外部调用需要有目标仓库访问权限和 Contents 写入权限的令牌。当前项目未部署这个事件服务，仅添加了触发入口；卡片仍需等待工作流执行和 GitHub 图片缓存刷新。
不需要手动创建 Personal Access Token，工作流使用 GitHub 自动提供的 GITHUB_TOKEN。

若 push 因权限设置失败：Settings → Actions → General → Workflow permissions 检查仓库或组织是否允许 Read and write permissions。不要修改其他项目权限。
若默认分支受保护，允许这份工作流写入主页分支，或改为由你手动提交更新图片。

## 3. 置顶代表项目

回到 github.com/Rocdna → Customize your pins，选择：
- mini-agent
- rag-assistant
- transformer_learn
- ml-notes

GitHub 主页背景、侧栏和字体由 GitHub 控制。README 只能装饰主内容区，不能把整页改成动态背景。

## 4. 更换成网上的动态壁纸

README 目前包含原创动漫横幅，以及链接到原作品页的芙莉莲 GIF 预览。壁纸都只是图片，不含音乐或交互场景。

你可以把 README 顶部图片换成自己选好的 GIF：

```html
<p align="center">
  <img src="./assets/banner.gif" width="900" alt="动漫动态封面" />
</p>
```

然后把 GIF 保存为 assets/banner.gif。建议宽度 900–1200px，横向构图，循环 4–8 秒，控制在 3–8MB。完整 4K 视频或 Wallpaper Engine Scene 不能直接嵌入 README。

外部预览图可能失效；上传你获得使用许可的本地 GIF 会更稳定。保留原画与动态作者署名。

已找到的壁纸参考：
- Frieren: Beyond Journey’s End [4K]：https://steamcommunity.com/workshop/filedetails/?id=3098540596
  原画：晓盆友 https://www.pixiv.net/en/artworks/106379857；动态作者：Deku Scrub。
- Aeolian by WLOP：https://steamcommunity.com/sharedfiles/filedetails/?id=1289832516
  原画：WLOP；动态作者：Eliza。作品页含低画质动态预览，适合作为风格参考。
- Lofi Anime Vibes: Cozy Aesthetic Room at Sunset：https://gifs.alphacoders.com/gifs/view/220239
  页面署名 Augastin Cart；页面声明仅供私人个人使用，公开主页使用前应取得许可。
- Wallpaper Engine 动漫榜单：https://steamcommunity.com/workshop/browse/?appid=431960&requiredtags%5B0%5D=anime
  在页面中选择 Most Popular (One Week) 查看实时榜单；本包没有把旧作品当作本周新榜排名。

## 文件说明

- README.md：真正展示在 GitHub 主页的内容。
- assets/：封面、技术栈、项目卡片、真实统计。
- profile-3d-contrib/profile-customize.svg：根据真实公开贡献记录绘制的 3D 贡献图。
- scripts/refresh_profile.py：更新贡献图与统计；只使用 Python 标准库。
- .github/workflows/refresh-profile.yml：每天自动更新，支持手动和外部事件触发。

统计口径：Stars 为公开仓库当前获星总数；主语言分布按非 Fork 公开仓库计数；贡献和活跃天数来自过去一年的公开贡献日历。没有添加假的排名、熟练度或项目成果。

本地已运行真实数据更新，检查 Python 语法、SVG 结构和 README 本地图片引用。GitHub Actions 与 GitHub 的最终渲染需要上传后确认。

动画使用开源 Platane/snk：https://github.com/Platane/snk
另一个可选 3D 贡献图项目：https://github.com/yoshi389111/github-profile-3d-contrib
本包的紫粉色 3D 图由自己的脚本绘制，与上面的项目独立。
