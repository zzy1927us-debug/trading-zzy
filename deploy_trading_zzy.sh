#!/usr/bin/env bash

# 一键部署 trading-zzy 项目到 macOS
# 作者：zzy1927us-debug

set -e  # 任一命令失败即退出脚本

REPO_URL="https://github.com/zzy1927us-debug/trading-zzy.git"
REPO_NAME="trading-zzy"
PY_VERSION="3.11"
VENV_DIR=".venv"

echo "==> 1. 检查并安装 Homebrew ..."
if ! command -v brew >/dev/null 2>&1; then
  echo "[Homebrew] 未安装，正在安装 Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "==> 2. 安装或更新 Python ${PY_VERSION} ..."
if ! brew ls --versions "python@${PY_VERSION}" >/dev/null 2>&1; then
  brew install "python@${PY_VERSION}"
else
  brew upgrade "python@${PY_VERSION}" || true
fi

PY_BIN="/opt/homebrew/opt/python@${PY_VERSION}/bin/python${PY_VERSION}"
if [ ! -x "$PY_BIN" ]; then
  PY_BIN="$(command -v python3)"
fi

echo "使用 Python 解采器: $PY_BIN"

echo "==> 3. 克隆或更新仓库 ..."
if [ -d "$REPO_NAME/.git" ]; then
  echo "仓库已存在，执行 git pull ..."
  cd "$REPO_NAME"
  git pull --ff-only
else
  git clone "$REPO_URL" "$REPO_NAME"
  cd "$REPO_NAME"
fi

echo "==> 4. 使用 Python ${PY_VERSION} 创建虚拟环境 ..."
# 删除旧虚拟环境（如存在）
if [ -d "$VENV_DIR" ]; then
  rm -rf "$VENV_DIR"
fi
"$PY_BIN" -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "==> 5. 升级 pip ..."
pip install --upgrade pip

echo "==> 6. 安装项目依赖 ..."
pip install -r requirements.txt

# DeepSeek API 需要 openai，如 requirements.txt 未列出则安装
if ! python -c "import openai" >/dev/null 2>&1; then
  echo "未检测到 openai 库，正在安装 ..."
  pip install openai
fi

echo "==> 7. 配置环境变量文件 (.env) ..."
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "首次部署：请按提示输入您的 API 密钥（可留空以保持占位符）"
  read -p "FINNHUB_API_KEY: " FH_KEY
  read -p "DEEPSEEK_API_KEY: " DS_KEY
  if [ -n "$FH_KEY" ]; then
    # 使用 BSD sed (macOS) 替换占位符
    sed -i '' "s/^FINNHUB_API_KEY=.*/FINNHUB_API_KEY=$FH_KEY/" .env
  fi
  if [ -n "$DS_KEY" ]; then
    sed -i '' "s/^DEEPSEEK_API_KEY=.*/DEEPSEEK_API_KEY=$DS_KEY/" .env
  fi
  echo ".env 文件已生成并配置。"
else
  echo ".env 文件已存在，将直接使用现有配置。"
fi

echo "==> 8. 测试运行 main.py ..."
python main.py || echo "[警告] main.py 执行出现错误，请自行排查日志。"

echo "==> 部署完成！"
echo "当前已激活虚拟环境 (.venv)。如果之后需要退出虚拟环境，请执行： deactivate"
