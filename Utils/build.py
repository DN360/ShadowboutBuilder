import os
import shutil
import hashlib
import csv
import glob

def generate_file_hash(filepath):
    """指定されたファイルのSHA256ハッシュを生成する"""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest().lower()
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {filepath}")
        return None

def build_shadowbout():
    # フォルダ名とファイル名の定義
    shadowbout_dir = "Shadowbout"
    zip_filename = "Shadowbout.zip"
    
    # 1. クリーンアップ
    print("--- 1. クリーンアップ開始 ---")
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
        print(f"✅ {zip_filename} を削除しました。")
    if os.path.exists(shadowbout_dir):
        shutil.rmtree(shadowbout_dir)
        print(f"✅ {shadowbout_dir} ディレクトリを削除しました。")

    # 新しいディレクトリ作成
    os.makedirs(shadowbout_dir, exist_ok=True)
    print(f"✅ {shadowbout_dir} ディレクトリを作成しました。")

    # 2. 基本アセットのコピー
    print("\n--- 2. 基本アセットのコピー開始 ---")
    copy_paths = [
        "Placeholder/*.webp",
        "Card/*.webp",
        "Background/playmat.webp",
        "XML/roomExportFlag.xml",
        "XML/summary.xml"
    ]
    
    for pattern in copy_paths:
        # ワイルドカード展開
        for src_path in glob.glob(pattern):
            filename = os.path.basename(src_path)
            shutil.copy(src_path, os.path.join(shadowbout_dir, filename))
            print(f"  ↳ コピー: {filename}")

    # 3. XMLデータの準備（カード情報）
    print("\n--- 3. XMLデータ生成と置換開始 ---")
    
    try:
        with open("XML/data.xml", 'r', encoding='utf-8') as f:
            data_xml_str = f.read()
    except FileNotFoundError:
        print("エラー: XML/data.xml が見つかりません。")
        return

    # デッキAのXML生成
    card_xml_a_concat = []
    try:
        with open("XML/card.xml", 'r', encoding='utf-8') as f:
            card_template = f.read()
    except FileNotFoundError:
        print("エラー: XML/card.xml が見つかりません。")
        return
    
    for i in range(1, 53):
        card_xml = card_template.replace("CARDDECK", "A")
        card_xml = card_xml.replace("CARDINDEX", str(i))
        card_xml_a_concat.append(card_xml)
    
    data_xml_str = data_xml_str.replace("__REPLACE_A_card_xml__", "\n".join(card_xml_a_concat))
    print("✅ デッキAのカードXMLを生成し、data.xmlに挿入しました。")

    # デッキBのXML生成
    card_xml_b_concat = []
    for i in range(1, 53):
        card_xml = card_template.replace("CARDDECK", "B")
        card_xml = card_xml.replace("CARDINDEX", str(i))
        card_xml_b_concat.append(card_xml)
        
    data_xml_str = data_xml_str.replace("__REPLACE_B_card_xml__", "\n".join(card_xml_b_concat))
    print("✅ デッキBのカードXMLを生成し、data.xmlに挿入しました。")

    # 4. データの上書き（ファイルハッシュとCSVからの情報差し替え）
    print("\n--- 4. ハッシュ値とカードデータ差し替え開始 ---")
    
    # CSVの読み込み
    card_data_csv = []
    try:
        with open("CSV/card.csv", 'r', encoding='utf-8') as csvfile:
            # ヘッダがないので、readerを使い、ヘッダを定義してからデータを辞書に変換するアプローチに戻すよ
            reader = csv.reader(csvfile)
            header = ['index', 'idol', 'hand', 'point', 'item', 'profile', 'effect', 'school']
            for row in reader:
                if row: # 空行はスキップ
                    card_data_csv.append(dict(zip(header, row)))
    except FileNotFoundError:
        print("エラー: CSV/card.csv が見つかりません。")
        return

    # カードごとのループ処理
    for i in range(1, 53):
        hash_name = f"card_{i}"
        webp_path = os.path.join(shadowbout_dir, f"{hash_name}.webp")
        
        # ハッシュ生成
        hash_val = generate_file_hash(webp_path)
        if hash_val is None: continue
        
        data_xml_str = data_xml_str.replace(f"__REPLACE__{hash_name}__", hash_val)

        # CSVからデータ取得 (Pythonではリストのインデックスは0始まりなので、i-1を使う)
        card = next((c for c in card_data_csv if c.get('index') == str(i)), None)
        if not card:
            print(f"警告: index {i} のデータがCSVに見つかりませんでした。スキップします。")
            continue

        # データ置換
        data_xml_str = data_xml_str.replace(f"__REPLACE__{hash_name}_idol__", card.get('idol', ''))
        data_xml_str = data_xml_str.replace(f"__REPLACE__{hash_name}_hand__", card.get('hand', ''))
        data_xml_str = data_xml_str.replace(f"__REPLACE__{hash_name}_point__", card.get('point', ''))
        data_xml_str = data_xml_str.replace(f"__REPLACE__{hash_name}_item__", card.get('item', ''))
        data_xml_str = data_xml_str.replace(f"__REPLACE__{hash_name}_profile__", card.get('profile', ''))
        data_xml_str = data_xml_str.replace(f"__REPLACE__{hash_name}_effect__", card.get('effect', ''))
        data_xml_str = data_xml_str.replace(f"__REPLACE__{hash_name}_school__", card.get('school', ''))
        
    # その他のアセットの置換
    assets_to_replace = {
        "card_back": "card_back.webp",
        "playmat": "playmat.webp",
        "simple": "simple.webp"
    }
    
    for hash_name, filename in assets_to_replace.items():
        webp_path = os.path.join(shadowbout_dir, filename)
        hash_val = generate_file_hash(webp_path)
        if hash_val:
            data_xml_str = data_xml_str.replace(f"__REPLACE__{hash_name}__", hash_val)
    
    # 5. 保存と圧縮
    print("\n--- 5. 保存と圧縮開始 ---")
    
    # data.xml の保存
    with open(os.path.join(shadowbout_dir, "data.xml"), 'w', encoding='utf-8') as f:
        f.write(data_xml_str)
    print("✅ data.xml を保存しました。")

    # ExportLock の作成
    lock_filepath = os.path.join(shadowbout_dir, "ExportLock")
    with open(lock_filepath, 'w') as f:
        pass
    print(f"✅ {lock_filepath} を作成しました。")

    # ZIP圧縮
    # shutil.make_archiveは、第一引数に基本名、第二引数に形式('zip')、第三引数にアーカイブするディレクトリを指定する
    shutil.make_archive("Shadowbout", 'zip', shadowbout_dir)
    print(f"🎉 全ての処理が完了！{zip_filename} が作成されました！")

# メイン実行
if __name__ == "__main__":
    build_shadowbout()