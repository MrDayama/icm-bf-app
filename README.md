# ICM & Bubble Factor アプリ

## アプリ概要（ICMとは）
ICM（Independent Chip Model）は、トーナメント残り賞金を参加者のチップ量に応じて公平に割り当てるための確率モデルです。本アプリはICMによる期待値（ICM値）と、勝利がどれだけ有利かを示すBubble Factor（BF）を計算します。

## できること
- 複数プレイヤーのチップ量からICM期待値を算出
- Bubble Factor（BF）の算出（First prize と ICM の比較）
- 入力バリデーション（プレイヤー数、配列長、負値、降順チェック等）
- スマホ対応のUI（PWAの基本対応あり）
- API（/api/calculate, /api/validate, /api/examples）

## スマホでの使い方
1. ブラウザでアプリを開く（例: https://your-app.example）
2. プレイヤー数を選択（2〜9）
3. 各プレイヤーのスタック（チップ）と配当を入力（配当は降順）
4. 「Calculate」ボタンを押すとICMとBFを表示
5. ホーム画面へ追加：ブラウザの「ホーム画面に追加」を選択するとPWAとして起動可能

## ローカル起動方法（初心者向け、コピペ可）
前提: Python 3.11 がインストールされていること

```bash
# レポジトリに移動
cd /mnt/c/Users/0pn32/OneDrive/Desktop/icm_bf_app

# 仮想環境作成（推奨）
python3 -m venv venv
source venv/bin/activate   # Windows PowerShell: venv\Scripts\Activate.ps1

# 依存関係インストール
pip install -r requirements.txt

# サーバー起動（開発）
python app.py
# または本番風に（gunicornを使う）
# PORT=5000 gunicorn app:app

# ブラウザで開く
http://localhost:5000
```

## Render デプロイ手順
1. 新しい Web Service を作成
2. Build Command に以下を指定：

```
pip install -r requirements.txt
```

3. Start Command に以下を指定：

```
gunicorn app:app
```

4. 環境変数 `PORT` は Render が自動設定するため特に指定不要
5. デプロイ後、公開URLにアクセスして動作確認

公開URL確認：Render のサービスページに表示されます。ブラウザで開き、トップページが見えれば成功です。

## 技術構成
- 言語: Python 3.11
- Web: Flask
- プロセスマネージャ: gunicorn（Procfile あり）
- PWA: manifest.json + service-worker.js（静的アセットのキャッシュ）
- テスト: unittest（tests/ にテストあり）

## ディレクトリ構成
```
icm_bf_app/
├── app.py              # Flask アプリ
├── icm.py              # ICM 計算ロジック
├── bf.py               # Bubble Factor 計算
├── models.py           # 入力モデルとバリデーション
├── utils.py            # ユーティリティ
├── requirements.txt    # 依存
├── Procfile            # Render / Heroku 用
├── runtime.txt         # Python ランタイム指定
├── templates/          # HTML テンプレート
├── static/             # CSS/JS/manifest/service-worker
└── tests/              # 単体テスト
```

## 今後の拡張案
- オフライン時の詳細な機能（ローカル計算フォールバック）
- マルチウェイディール（複数人での配当分配）
- CSV エクスポート / インポート
- UI のさらなるモバイル最適化（アクセシビリティ向上）
- 精度の向上と複数通貨対応

---

この README は日本語で初心者にもわかるように作成しています。問題があれば tests/ を参考に挙動を確認してください。
