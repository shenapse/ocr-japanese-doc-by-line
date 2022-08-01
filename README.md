# Google Cloud Vision API で本の目次をOCR

## 目次

- [Google Cloud Vision API で本の目次をOCR](#google-cloud-vision-api-で本の目次をocr)
    - [目次](#目次)
    - [概要](#概要)
        - [出力イメージ](#出力イメージ)
        - [対応フォーマット](#対応フォーマット)
    - [環境 & インストール](#環境--インストール)
        - [インストール](#インストール)
        - [Google Cloud Vision API key の有効化](#google-cloud-vision-api-key-の有効化)
    - [使い方](#使い方)
        - [概要](#概要-1)
            - [出力テキストファイル数](#出力テキストファイル数)
            - [出力テキストファイルの名前](#出力テキストファイルの名前)
        - [サンプルコード](#サンプルコード)
            - [単一の jpeg, png を読み込む](#単一の-jpeg-png-を読み込む)
            - [複数画像を綴じた pdf や zip を読み込む](#複数画像を綴じた-pdf-や-zip-を読み込む)
            - [【要注意】 ディレクトリ内の jpeg や png をまとめて読み込む](#要注意-ディレクトリ内の-jpeg-や-png-をまとめて読み込む)
            - [読み込むファイルのプレビュー](#読み込むファイルのプレビュー)
    - [背景と関連ツール(おまけ)](#背景と関連ツールおまけ)

## 概要

横書き一段組の文章を含む画像/pdfファイルからテキストを抽出する python スクリプト.
OCR は Google Cloud Vision API を使い, そのレスポンス内の文字の順序と位置を整えることで, 目次らしい出力を得る.
API のリクエスト消費量 = 処理したページ数.
API 依存なので GPU は不要.

### 出力イメージ

[/sample/la_003.png](/sample/la_003.png) (東大出版「線形代数の世界」の目次の最初のページ)を読む場合.
![sample_png](/sample/la_003.png)

main.py の最下部に以下を書いて実行.

```python
# main.py
if __name__ == "__main__":
    file = "./sample/la_003.png"
    dir_out: Path = Path("./out") # optional
    # ocr and save text file
    ocr_by_cloud_vision_api(file_or_dir=file, dir_out=dir_out)

    # get ./out/la_003.txt
```

```bash
# run main.py
poetry run python ./scr/main.py
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

zip や pdf を与えた場合の入出力サンプルは sample と out ディレクトリを参照. テキストファイルの行数が増えるだけで, 出力形式に違いはないことを確認されたい.

### 対応フォーマット

png, jpeg, それらの zip, または pdf.
ただし, pdf だと他のフォーマットに比べて著しく遅くなる. これは, pdf を png 等の画像形式へ変換する処理がボトルネックとなるため.

## 環境 & インストール

- Windows 10 + WSL2 + Ubuntu 20.04.3
- python 3.10.5 (pyenv 2.3.2) + poetry (1.1.11)

### インストール

このレポジトリをローカルに落としてプロジェクトトップに移動.

```bash
git clone https://github.com/Shena4746/ocr-japanese-toc.git
cd ./ocr-japanese-toc
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

このまま `poetry install` としたいところだが, 記載バージョンの poetry だと pyenv で指定したインタープリタを `.venv` に置いてくれない場合があるらしい(!!). そこで, 念のため先に 3.10.5 インタープリタを `.venv` に置いておく.

```bash
python3 -m venv .venv
```

準備が整ったので poetry を使ってパッケージのインストール.

```bash
poetry install
```

依存パッケージの詳細は, poetry.lock または poetry.toml を参照.

### Google Cloud Vision API key の有効化

[クイックスタート: Vision API を設定する](https://cloud.google.com/vision/docs/setup) に従って, Google Cloud Vision API のサービスアカウントキーを環境にセット. done!

## 使い方

### 概要

main.py の `ocr_by_cloud_vision_api(file_or_dir=)` にパスを与えて main.py を実行すると, OCR されたテキストファイルが出力される.

- `ocr_by_cloud_vision_api()` 引数一覧
  - `file_or_dir: Path | str` : 必須. ファイルまたディレクトリのパス.
  - `ext: str` : `file_or_dir` 引数でディレクトリパスを指定したときのみ利用される. ファイルパスを指定した場合は, この引数は無視される. デフォルトは `"zip"` ディレクトリを指定した際, 読み込むファイルの種類を指定する.
  - `dir_out: Path | None` : テキストファイルの出力フォルダ. デフォルトでは `file_or_dir` と同じディレクトリ.
  - `name_out: str | None` : 出力されるテキストファイルの名前. デフォルトでは読み込み対象ファイル達の最初のファイル名.

- `ocr_by_cloud_vision_api(file_or_dir=)` が受け取れるパスの種類一覧
  - png, jpeg, pdf, zip (中身は png のみか jpeg のみ) のファイルパス
  - png または jpeg を含むディレクトリのパス

#### 出力テキストファイル数

`ocr_by_cloud_vision_api()` は常に1つのテキストファイルを保存する.

[受け取れるパス](#受け取れるパス) に書いたいずれの場合でも, 与えられたパスが含む(多くの場合複数の)画像を1つのまとまりと解釈して, 1つのテキストファイルを出力する.
たとえば, 1つの png ファイルが含む画像は1枚で, 3ページから成る pdf が含む画像は3枚だが, このどちらの場合でも出力されるテキストファイルは1つのみ.

#### 出力テキストファイルの名前

`hey.png`, `hiya.jpeg`, `hi.pdf`, `hello.zip` など単一ファイルを読ませた場合は, それぞれの stemname を取って, `hey.txt`, `hiya.txt`, ... と出力される.

この例外に当たるのが, ディレクトリを指定してファイルを読み込む場合. このケースでは, ディレクトリ内の読み込み対象のファイル群のうちの, 最初のファイルの名前が出力テキストファイル名に採用される. 具体例はサンプルコードを参照.

### サンプルコード

#### 単一の jpeg, png を読み込む

main.py で以下を実行すればよい.

```python
# for single image file such as jpeg or png
file = "./sample/la_003.png"
# output directory for text file
# default uses the directory of the input file,
# e.g., sample directory in this case
dir_out: Path = Path("./out") # Path is an alias for pathlib.Path
ocr_by_cloud_vision_api(file_or_dir=file, dir_out=dir_out)

# get ./out/la_003.txt
```

#### 複数画像を綴じた pdf や zip を読み込む

```python
# for single but potentially multi page file such as zip or pdf
file = "./sample/kernel.zip"
dir_out: Path = Path("./out")
ocr_by_cloud_vision_api(file_or_dir=file, dir_out=dir_out)

# get ./out/kernel.txt
```

#### 【要注意】 ディレクトリ内の jpeg や png をまとめて読み込む

この場合も OCR 結果はひとつのテキストファイルとして出力される.
この場合, `name_out=` 引数を与えないと `006.txt` と出力される. このような識別性の低い名前を使うと, 出力テキストファイルが上書きされるリスクが高くなることに注意.
以下の例では, `name_out=directory_name` とした.

```python
# for all png files in sample_files directory
dir = "./sample/algebra" # ['006.png', '007.png', '008.png']
dir_out: Path = Path("./out")
name_out:str = Path(dir).name # algebra
ocr_by_cloud_vision_api(
    file_or_dir=dir, ext="png", dir_out=dir_out, name_out=name_out
)

# get ./out/algebra.txt
```

ディレクトリ内の複数の pdf や zip をまとめて読み込むことはできない.

```python
# trying to read pdfs by specifying directory causes an error
dir = "./sample"
preview_files(file_or_dir=dir, ext="pdf")

# ValueError: Can't read non-image files by specifying directory.
# dir=/absolute/path/sample
# ext=pdf
```

#### 読み込むファイルのプレビュー

パスを指定した際に処理されるファイル情報を確認したいときに使う.

```python
# preview files to read
file = "./sample/kernel.zip"
preview_files(file_or_dir=file)
# 'root:/absolute/path/sample'
# 'extension:zip'
# kernel.zip contains: ['006.png', '007.png', '008.png', '009.png', '010.png']
# named temporary? False
```

## 背景と関連ツール(おまけ)

紙の本を pdf 化したお手製電子書籍への目次付与作業では目次のテキストが必要になる. ネット上に転がっていることもあるが, 本に記載されているレベルの詳細な目次を拾うことは一般には期待できない. そこで, 本の目次を OCR で抽出するツールを作ることにした.

Google Cloud Vision の選択理由は, 精度とコストと軽さのバランスが良かったから. 特に, PyTorch などの GPU を要求するツールと同等以上の精度を持ちながら, ユーザー側にはそのマシンスペックを要求しない点が, ライトユーザーにもちょうど良いと判断した. 同 API は月間1000リクエストまで無料で使えるので, 目次抽出(1冊あたりせいぜい5ページ)用途であればコストは無視できるだろう.

なお, 目次テキストが入手済という前提に立った pdf への目次付与ツールとして, 以下のようなものがある. OCR して得たテキストファイルの活用例として参考にされたい.

- pdf への目次付与ツール
  - [linux の gs コマンド](https://refspecs.linuxfoundation.org/LSB_5.0.0/LSB-Imaging/LSB-Imaging/gs.html#:~:text=The%20gs%20command%20invokes%20Ghostscript,executes%20them%20as%20Ghostscript%20programs.)
  - [pdf_as](http://uchijyu.s601.xrea.com/wordpress/pdf_as/)
  - [PDFtk](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/)
- これらのツールへの入力補助ツール
  - [目次のないPDFに目次を追加する - gs](https://freak-da.hatenablog.com/entry/2019/09/17/113838)
  - [PDFに目次を追加する - PDFtk](https://osanshouo.github.io/blog/2021/05/04-pdf-toc/)
  - [booky - PDFtk](https://github.com/SiddharthPant/booky)
