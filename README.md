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
    - [関連ツール(参考)](#関連ツール参考)

## 概要

横書き一段組の日本語文章を含む画像/pdf ファイルから各行の文章を抽出し, それらを改行で繋いだ 1 つのテキストファイルを出力する python スクリプト.
OCR は Google Cloud Vision API を利用している.

API のリクエスト消費量 = 処理したページ数.
API 依存なので GPU は不要.

対象言語が英語等のアルファベットのような文字ならば, [tesseract](https://github.com/tesseract-ocr/tesseract) で十分な精度が出るので, このレポジトリのスクリプトを使う実益はない.

行認識のアプローチは[ここ](/idea.md)にメモした.

### サンプル

[/sample/la_003.png](/sample/la_003.png) (東大出版「線形代数の世界」の目次の最初のページ)を読んで [out](./out/) ディレクトリにテキストファイルとして保存する場合.
![sample_png](/sample/la_003.png)

```bash
# ocr-gcv is an alias for '/abs-path/to/.venv/python3 /abs-path/to/ocr-gcv.py'
ocr-gcv ./sample/la_003.png -d ./out/
# save la_003.txt
```

以下の出力 [/out/la_003.txt](/out/la_003.txt) が得られる.

```text
V
目次
はじめに
この本の使い方・viii
第1章線形空間1
1.1体1
1.2線形空間の定義6
1.3線形空間の例12
1.4部分空間17
1.5次元25
1.6無限次元空間*32
第2章線形写像38
2.1線形写像の定義38
2.2線形写像の例47
2.3行列表示56
2.4核と像64
2.5完全系列と直和分解*69
第3章自己準同形76
3.1最小多項式77
3.2固有値と対角化85
3.3一般固有空間と三角化92
3.4巾雰自己準同形とジョルダン標準形97
3.5行列式105
3.6固有多項式112
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

[tesseract-zip-pdf-dir](https://github.com/Shena4746/tesseract-zip-pdf-dir) と同じなので, そちらを参照.

先に書いたサンプルコードのように,

```bash
ocr-gcv your-file.zip
```

のように呼びたいなら, たとえば, 以下のようなエイリアスを ~/.bashrc に加えておく.

```bash
alias ocr-gcv='/abs-path/to/.venv/bin/python3 /abs-path/to/ocr-gcv.py'
```

## 関連ツール(参考)

目次テキストファイルの活用先として pdf への目次付与がある.
それを行うツールのうち, 目次テキストが入手済という前提に立ったものには, 以下のようなものがある.

- pdf への目次付与ツール
  - [linux の gs コマンド](https://refspecs.linuxfoundation.org/LSB_5.0.0/LSB-Imaging/LSB-Imaging/gs.html#:~:text=The%20gs%20command%20invokes%20Ghostscript,executes%20them%20as%20Ghostscript%20programs.)
  - [pdf_as](http://uchijyu.s601.xrea.com/wordpress/pdf_as/)
  - [PDFtk](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/)
- これらのツールへの入力補助ツール
  - [目次のないPDFに目次を追加する - gs](https://freak-da.hatenablog.com/entry/2019/09/17/113838)
  - [PDFに目次を追加する - PDFtk](https://osanshouo.github.io/blog/2021/05/04-pdf-toc/)
  - [booky - PDFtk](https://github.com/SiddharthPant/booky)
- これらの入力補助ツールへの入力補助ツール
  - [tesseract-zip-pdf-dir - 英語版 ocr 補助ツール](https://github.com/Shena4746/tesseract-zip-pdf-dir)
