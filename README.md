# Google Cloud Vision で日本語文章を行ごとに OCR

## 目次

- [Google Cloud Vision で日本語文章を行ごとに OCR](#google-cloud-vision-で日本語文章を行ごとに-ocr)
    - [目次](#目次)
    - [概要](#概要)
        - [サンプル](#サンプル)
        - [対応フォーマット](#対応フォーマット)
    - [インストール](#インストール)
        - [Google Cloud Vision API key の有効化](#google-cloud-vision-api-key-の有効化)
    - [使い方](#使い方)

## 概要

横書き一段組の日本語文章を含む画像/pdf ファイルから各行の文章を抽出し, それらを改行で繋いだ 1 つのテキストファイルを出力する python スクリプト.
OCR は Google Cloud Vision API を利用している.

API のリクエスト消費量 = 処理したページ数.
API 依存なので GPU は不要.

対象言語が英語等のアルファベットのような文字ならば, [tesseract](https://github.com/tesseract-ocr/tesseract) で十分な精度が出るので, このレポジトリのスクリプトを使う実益はない.

### サンプル

[/sample/la_003.png](/sample/la_003.png) (東大出版「線形代数の世界」の目次の最初のページ)を読んで [out](./out/) ディレクトリにテキストファイルとして保存する場合.
![sample_png](/sample/la_003.png)

```bash
# ocr-gcv is an alias for '/abs-path/to/.venv/bin/python3 /abs-path/to/ocr-gcv.py'
ocr-gcv ./sample/la_003.png -d ./out/
# save la_003.txt
```

以下の出力 [/out/la_003.txt](/out/la_003.txt) が得られる.

```text
V
目次
はじめに
この本の使い方・ viii
第1章 線形空間 1
1.1 体 1
1.2 線形空間の定義 6
1.3 線形空間の例 12
1.4 部分空間 17
1.5 次元 25
1.6 無限次元空間* 32
第2章 線形写像 38
2.1 線形写像の定義 38
2.2 線形写像の例 47
2.3 行列表示 56
2.4 核と像 64
2.5 完全系列と直和分解* 69
第3章 自己準同形 76
3.1 最小多項式 77
3.2 固有値と対角化 85
3.3 一般固有空間と三角化 92
3.4 巾雰自己準同形とジョルダン標準形 97
3.5 行列式 105
3.6 固有多項式 112
```

zip や pdf を与えた場合の入出力サンプルは [sample](/sample/) と [out](/out/) ディレクトリを参照. テキストファイルの行数が増えるだけで, 出力形式に違いはないことを確認されたい. なお, このレポジトリは, 元々は本の目次を OCR することを目的としていたため, 今のところ, サンプルは目次に偏っている.

### 対応フォーマット

png, jpeg, それらの zip, または pdf.
ただし, pdf だと他のフォーマットに比べて著しく遅くなる. これは, pdf を png 等の画像形式へ変換する処理がボトルネックとなるため.

## インストール

- テスト環境
  - Windows 10 + WSL2 + Ubuntu 20.04.3
  - python 3.10.5 (pyenv 2.3.2) + poetry (1.1.11)

```bash
git clone https://github.com/Shena4746/ocr-japanese-doc-by-line.git
cd ./ocr-japanese-doc-by-line
```

pyenv で python 3.10.5 をプロジェクト内で有効化する.
まだ 3.10.5 を pyenv に入れてなければ install する.

```bash
pyenv install 3.10.5
```

ローカルで有効化.

```bash
pyenv local 3.10.5
```

このまま `poetry install` としたいところだが, 記載バージョンの poetry だと pyenv で指定したインタープリタを `.venv` に置いてくれない場合があるらしい(!!). そこで, 念のため先に 3.10.5 インタープリタを先に `.venv` に置く操作を挟む.

```bash
python3 -m venv .venv
poetry install
```

### Google Cloud Vision API key の有効化

[クイックスタート: Vision API を設定する](https://cloud.google.com/vision/docs/setup) に従って, Google Cloud Vision API のサービスアカウントキーを環境にセット. done!

## 使い方

```bash
ocr-gcv ocr --help
```

[tesseract-zip-pdf-dir](https://github.com/Shena4746/tesseract-zip-pdf-dir).

先に書いたサンプルコードのように,

```bash
ocr-gcv your-file.zip
```

のように呼びたいなら, たとえば, 以下のようなエイリアスを ~/.bashrc に加えておく.

```bash
alias ocr-gcv='/abs-path/to/.venv/bin/python3 /abs-path/to/ocr-gcv.py'
```
