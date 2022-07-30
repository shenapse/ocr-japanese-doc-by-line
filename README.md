# Google Cloud Vision API で本の目次をOCR

## 概要

横書き一段組の文章を含む画像/pdfファイルからテキストを抽出する python スクリプト.
OCR は Google Cloud Vision API を使い, そのレスポンス内の文字の順序と位置を整えることで, 目次らしい出力を得る.
API のリクエスト消費量 = 処理したページ数.
API 依存なので GPU は不要.

## 出力イメージ
次の png 画像(東大出版「線形代数の世界」の目次の最初のページ)を与えたとする.
![sample_png](/sample_files/la_003.png)

以下の出力が得られる.

```
目次
はじめに111
この本の使い方..viii
第1章線形空間1
1.1体1
1.2線形空間の定義6
1.3線形空間の例12
1.4部分空間.17
1.5次元25
1.6無限次元空間*32
第2章線形写像38
2.1線形写像の定義38
2.2線形写像の例47
2.3行列表示56
2.4核と像64
2.5完全系列と直和分解69
第3章自己準同形76
3.1最小多項式77
3.2固有値と対角化85
3.3一般固有空間と三角化92
3.4巾零自己準同形とジョルダン標準形·97
3.5行列式♦105
3.6固有多項式・･112
```

zip や pdf を与えた場合のサンプルは sample_files と out ディレクトリを参照.

## 対応フォーマット

png, jepg, それらのzip, または pdf.
ただし, pdf だと他の形式に比べて著しく遅くなる. これは, pdf を png 等の画像形式へ変換する処理がボトルネックとなるため.

## サンプルコード

jpeg や png を単体で読ませるなら, main.py で以下を実行すればよい.

```python
# for single image file such as jpeg or png
file = "./sample_files/la_003.png"
# output directory for text file
# default uses the directory of the input file,
# e.g., sample_files directory in this case
dir_out: Path = Path("./out") # Path is the alias for pathlib.Path
ocr_by_cloud_vision_api(file_or_dir=file, dir_out=dir_out)
```

複数画像を綴じた pdf や zip を読ませる場合.

```python
# for single but potentially multi page file such as zip or pdf
file = "./sample_files/kernel.zip"
dir_out: Path = Path("./out")
ocr_by_cloud_vision_api(file_or_dir=file, dir_out=dir_out)
```

特定ディレクトリ内の jpeg や png をまとめて読み込む場合.
この場合もOCR結果はひとつのテキストファイルとして出力される.

```python
# for all png files in sample_files directory
file = "./sample_files"
dir_out: Path = Path("./out")
ocr_by_cloud_vision_api(file_or_dir=file, ext = "png", dir_out=dir_out)
```