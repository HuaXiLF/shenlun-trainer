# 推送到 GitHub — 操作说明

仓库已在本地完整建好（`main` 分支，2 次提交，27 个文件），
只差最后一步推送到远程。

---

## 一、为什么本地推送失败了

蛋蛋试过全部四条通道，都被网络或权限挡住：

| 通道 | 结果 | 原因 |
|:---|:---:|:---|
| `git` 直连 github.com | ❌ 超时 | 21 秒连不上 443 端口 |
| `git` 走系统代理（127.0.0.1:12026） | ❌ 502 | 代理不允许 CONNECT 到 github.com |
| SSH（git@github.com） | ❌ 失败 | host key 未信任，且同样受网络限制 |
| GitHub 连接器写入 API | ❌ 403 | 授权 token 是**只读**的（可读 profile / 仓库 / 文件，不能写） |

**结论：当前环境下没有可用的 GitHub 写入通道。** 需要在网络通畅时操作。

---

## 二、推送步骤（网络通畅时）

### 准备工作

```bash
cd "D:\xiazai\aiwork\workbuddy\2026-09-14-20-35-15\shenlun-trainer"
```

### 第 1 步：设置远程地址

```bash
git remote add origin https://github.com/HuaXiLF/shenlun-trainer.git
```

> 如果之前加过，改用：
> ```bash
> git remote set-url origin https://github.com/HuaXiLF/shenlun-trainer.git
> ```

### 第 2 步：推送

```bash
git push -u origin main
```

### 第 3 步：如果走代理

系统代理 `127.0.0.1:12026` 不支持 CONNECT 到 github.com，需要换成支持 HTTPS 隧道的代理：

```bash
# 换成你自己的代理端口
git config --local http.proxy "http://127.0.0.1:<你的HTTPS代理端口>"
git config --local https.proxy "http://127.0.0.1:<你的HTTPS代理端口>"

git push -u origin main

# 推送成功后可以清掉
git config --local --unset http.proxy
git config --local --unset https.proxy
```

### 备选：SSH 方式

```bash
# 1. 生成密钥（如果没有）
ssh-keygen -t ed25519 -C "2025281050179@whu.edu.cn"

# 2. 查看公钥，复制到 https://github.com/settings/keys
cat ~/.ssh/id_ed25519.pub

# 3. 信任 github 主机
ssh-keyscan github.com >> ~/.ssh/known_hosts

# 4. 测试
ssh -T git@github.com

# 5. 换远程地址并推送
git remote set-url origin git@github.com:HuaXiLF/shenlun-trainer.git
git push -u origin main
```

---

## 三、如果推送时提示认证失败

GitHub 从 2021 年起不再接受账号密码，需要用 **Personal Access Token**：

1. 打开 https://github.com/settings/tokens
2. **Generate new token** → **classic**
3. 勾选 **`repo`** 权限
4. 生成后复制 token（只显示一次）
5. 推送时：
   - 用户名：`HuaXiLF`
   - 密码：**粘贴 token**（不是账号密码）

或者让 git 记住：

```bash
git config --global credential.helper manager
```

---

## 四、推之前可以先自检

```bash
cd "D:\xiazai\aiwork\workbuddy\2026-09-14-20-35-15\shenlun-trainer"

# 看状态
git status

# 看提交历史
git log --oneline

# 看文件清单
git ls-files

# 确认没有敏感文件被误加
git ls-files | findstr /i "训练记录 pdf mp4"
# 应当无输出
```

---

## 五、推送后会看到什么

仓库首页会自动渲染 `README.md`，包含：
- 徽章（License / 格式 / 语料 / 版本）
- 四段式批改说明
- 评分标尺（v3 校准档）
- 8 类失分模式（E1—E8）
- 命令表、安装方式、结构树
- 答案库说明与准确性核验表

建议顺手补上仓库信息：

| 项 | 建议值 |
|:---|:---|
| Description | 申论训练营 · 面向国考/省考申论小题的 AI 批改训练 Skill |
| Topics | `gongkao` `shenlun` `civil-service-exam` `ai-skill` `claude-skill` `exam-prep` |
| Website | （可选） |

---

## 六、附：如果想让 GitHub 连接器能写

当前连接器的 token 是只读的。如果希望蛋蛋以后能直接帮你推：

1. 在 WorkBuddy 的连接器管理里，找到 GitHub 连接器
2. 断开后重新授权，**授权时勾选 `repo` 全权限**（Create repositories / Push 等）
3. 重新连接后告诉蛋蛋，蛋蛋就能直接推送了

> 注意：重新授权可能需要 GitHub 端 OAuth App 支持相应 scope，
> 如果连接器本身只申请了只读 scope，则需要联系连接器维护方。
