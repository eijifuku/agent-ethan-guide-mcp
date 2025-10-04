# Agent-Ethan2 Guide MCP Server

[English](./README.md)

agent-ethan2フレームワークのドキュメントとソースコードをコーディングエージェントに提供し、フレームワークを利用した実装を補助するMCPサーバーです。

## 特徴

- 🚀 **簡単セットアップ**: uvx経由でインストール不要、設定だけで利用開始
- 📦 **自動ダウンロード**: GitHubから指定バージョンのagent-ethan2を自動取得
- 📝 **自動設定**: AGENTS.mdにドキュメント・ソースコードの場所を自動記載
- 🔄 **バージョン管理**: 簡単にバージョンを切り替え可能

## クイックスタート

### 1. MCPクライアント設定

MCPクライアント（Cursor、Claude Desktop、Clineなど）の設定ファイルに以下を追加：

**Cursorの場合** (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "agent-ethan-guide": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/eijifuku/agent-ethan-guide-mcp",
        "agent-ethan-guide-mcp"
      ],
      "env": {
        "SETUP_RULEFILE": "AGENTS.md",
        "SETUP_TMP_DIR": "./tmp"
      }
    }
  }
}
```

**Claude Desktopの場合** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

同様のJSON形式で設定します。

**注意**: 
- `SETUP_RULEFILE`と`SETUP_TMP_DIR`には**絶対パス**を指定することを推奨します
- `SETUP_TMP_DIR`にはリポジトリ外のディレクトリ、または`.gitignore`に登録されたディレクトリを指定してください

```json
"env": {
  "SETUP_RULEFILE": "/path/to/your/project/AGENTS.md",
  "SETUP_TMP_DIR": "/path/to/your/project/tmp"  // .gitignoreに追加
}
```

`.gitignore`の例：
```
tmp/
AGENTS.md
```

### 2. クライアントを再起動

設定を反映させるため、MCPクライアントを再起動します。

### 3. setupツールを実行

MCPクライアント経由でsetupツールを実行：

```
setup(version="v0.1.1")
```

これにより：
- GitHubからagent-ethan2 v0.1.1をダウンロード
- 指定ディレクトリに解凍
- AGENTS.mdに場所を記載

### 4. 完了！

agent-ethan2のドキュメントとソースコードが利用可能になります。エージェントに質問すると、自動的にAGENTS.mdを参照してagent-ethan2の情報を活用します。

## setupツール

### パラメータ

- `version` (必須): agent-ethan2のGitHubタグ (例: "v0.1.1", "v0.1.0")

### 環境変数

| 変数名 | デフォルト | 説明 |
|--------|-----------|------|
| `SETUP_RULEFILE` | `AGENTS.md` | ルールファイルのパス |
| `SETUP_TMP_DIR` | `./tmp` | ダウンロード先ディレクトリ |

**重要**: 相対パスを使用する場合、MCPクライアントの起動ディレクトリからの相対パスとして解釈されます。プロジェクトごとに異なる場所に作成したい場合は、絶対パスを指定してください。

### 利用可能なバージョン

agent-ethan2の利用可能なバージョンは[GitHubのリリースページ](https://github.com/eijifuku/agent-ethan2/tags)で確認できます。

### 使用例

```
# 最新版をセットアップ
setup(version="v0.1.1")

# 特定バージョンをセットアップ
setup(version="v0.1.0")
```

### バージョン変更

新しいバージョンに切り替える場合：

1. 古いディレクトリを削除（または放置）
2. 新しいバージョンでsetupを実行

```bash
# 古いバージョンを削除（任意）
rm -rf ./tmp/agent-ethan2-0.1.0

# 新しいバージョンをセットアップ
setup(version="v0.1.1")
```

AGENTS.mdは自動的に更新されます。

## 開発者向け

### ローカルでの開発・テスト

#### 前提条件

- Python 3.10以上
- Docker & Docker Compose（Docker方式の場合）
- uv（uvx方式の場合）

#### uvx方式（推奨）

```bash
# リポジトリをクローン
git clone https://github.com/eijifuku/agent-ethan-guide-mcp.git
cd agent-ethan-guide-mcp

# ローカルから実行
uvx --from . agent-ethan-guide-mcp
```

#### Docker方式

HTTPモードでテストする場合：

```bash
# configs/server.yamlをHTTPモードに変更
# run_options:
#   transport: http
#   host: 0.0.0.0
#   port: 8009
#   path: /mcp

# コンテナ起動
docker-compose up -d

# ログ確認
docker-compose logs -f
```

#### テスト実行

```bash
# 依存関係インストール
pip install -e .[dev]

# テスト実行
pytest tests/
```

### プロジェクト構成

```
agent-ethan-guide-mcp/
├── mcp_app/
│   └── tools/
│       └── agent_ethan_setup.py  # setupツール実装
├── mcp_server.py                 # MCPサーバーエントリーポイント
├── configs/
│   └── server.yaml              # サーバー設定
├── tests/                       # テストコード
├── pyproject.toml              # パッケージ設定
└── README.ja.md                # このファイル
```

## トラブルシューティング

### setupツールが見つからない

MCPクライアントを再起動して、MCPサーバーの接続状態を確認してください。

### ファイルが期待した場所に作成されない

環境変数に絶対パスを指定してください：

```json
"env": {
  "SETUP_RULEFILE": "/home/user/projects/myproject/AGENTS.md",
  "SETUP_TMP_DIR": "/home/user/projects/myproject/tmp"
}
```

### バージョンが見つからない (HTTP 404)

指定したバージョンタグがagent-ethan2リポジトリに存在するか確認してください。

利用可能なバージョン: https://github.com/eijifuku/agent-ethan2/tags

## ライセンス

このプロジェクトのライセンスについては、LICENSEファイルを参照してください。

## 関連リンク

- [agent-ethan2](https://github.com/eijifuku/agent-ethan2) - AIエージェントフレームワーク
- [FastMCP](https://github.com/jlowin/fastmcp) - MCPサーバーフレームワーク
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP仕様
