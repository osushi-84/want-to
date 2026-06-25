# アーキテクチャ

## 概要

やりたいことリストをビジュアルに表示するシングルページアプリ。フレームワーク・ビルドツールなし、素の HTML/CSS/JS のみ。

## ファイル構成

```
want-to-do/
├── index.html          # メインページのHTML（本番）
├── style.css           # メインページのスタイル
├── script.js           # メインページの表示・操作ロジック
├── data.json           # 表示データ（やりたいこと・やってみたいこと・行きたいライブ）
├── demo.html           # 表示モード比較デモ（横流れ・3Dカルーセル・球体・オービット）
├── やりたいこと.txt      # データの元ネタ・メモ
├── tests/
│   └── test_static_assets.py # 静的ファイル構成のテスト
└── docs/
    ├── ARCHITECTURE.md # このファイル
    ├── CURRENT_TASK.md # 進行中タスク
    └── MEMO.md         # 実装ログ
```

## メインページの構成

- `index.html`: ページ構造と外部ファイルの読み込み
- `style.css`: レイアウト、装飾、レスポンシブ対応
- `script.js`: データ取得、件数表示、カルーセル、スフィアの制御

### セクション構成

| セクション | 表示内容 | UI コンポーネント |
|---|---|---|
| Hero | タイトル・件数統計 | テキスト |
| やりたいこと | やりたいことリスト | 3D カルーセル |
| やってみたいこと | やってみたいことリスト | 3D カルーセル |
| 行きたいライブ | アーティストリスト | 3D スフィア |
| Footer | - | テキスト |

### データ

- 表示データは `data.json` で管理する
- `script.js` は `fetch('./data.json')` で読み込み、件数表示・カルーセル・スフィアを初期化する
- `yariItems`: やりたいこと（現在 12 件）
- `tryItems`: やってみたいこと（現在 34 件）
- `artists`: 行きたいライブ（現在 36 件）

### 3D カルーセル

- `initCarousel(wrapId, data)` を共通関数として定義し、やりたいこと・やってみたいことの両方に使用
- 半径 600px 固定（モバイル 260px）
- スロット数は 24 固定
- angular step 固定 = 360 / slots
- ドラッグ＋慣性＋オート回転

### 3D スフィア

- フィボナッチ格子でアーティストを球面に均等配置
- ホバー: font-size 1.22 倍・白色・カラーグロー
- クリック: Google 検索（`[アーティスト名] ライブ チケット`）を別タブ
- 当たり判定は `transform: scale()` を使わず `font-size` のみで制御（hit area = 見た目）

## 技術スタック

- HTML / CSS / Vanilla JS
- Google Fonts（Noto Serif JP, Noto Sans JP, IBM Plex Mono）
- Web API: requestAnimationFrame, IntersectionObserver
