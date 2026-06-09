# アーキテクチャ

## 概要

やりたいことリストをビジュアルに表示するシングルページアプリ。フレームワーク・ビルドツールなし、素の HTML/CSS/JS のみ。

## ファイル構成

```
want-to-do/
├── index.html          # メインページ（本番）
├── demo.html           # 表示モード比較デモ（横流れ・3Dカルーセル・球体・オービット）
├── やりたいこと.txt      # データの元ネタ。ここを編集 → index.html に手動反映
└── docs/
    ├── ARCHITECTURE.md # このファイル
    ├── CURRENT_TASK.md # 進行中タスク
    └── MEMO.md         # 実装ログ
```

## index.html の構成

### セクション構成

| セクション | 表示内容 | UI コンポーネント |
|---|---|---|
| Hero | タイトル・件数統計 | テキスト |
| やりたいこと | やりたいことリスト | 3D カルーセル |
| やってみたいこと | やってみたいことリスト | 3D カルーセル |
| 行きたいライブ | アーティストリスト | 3D スフィア |
| Footer | - | テキスト |

### データ

```js
// やりたいこと（現在 12 件）
const yariItems = [ {e:'絵文字', t:'テキスト'}, ... ];

// やってみたいこと（現在 33 件）
const items = [ {e:'絵文字', t:'テキスト'}, ... ];

// 行きたいライブ（現在 36 件）
const artists = [ 'アーティスト名', ... ];
```

### 3D カルーセル

- `initCarousel(wrapId, data)` を共通関数として定義し、やりたいこと・やってみたいことの両方に使用
- 半径 600px 固定（モバイル 260px）
- スロット数は `Math.ceil(24 / n) * n`（常に 24 以上、アイテムを複製して全周を埋める）
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
