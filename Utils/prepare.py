import os
import sys
from PIL import Image, ImageOps, ImageDraw
import PIL.ImageOps
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_pdf_images import extract_images_from_pdf

def main():
    # PDF ファイルのパス
    input_pdf = "million_Shadowbout_playmat_print.pdf"
    cmyk_pdf = "million_Shadowbout52_cmyk.pdf"
    
    # 一時的に抽出するフォルダ
    temp_output_folder = "temp_extracted_images"
    
    # 最終的な出力フォルダ
    final_output_folder = "Background"
    card_output_folder = "Card"
    
    # 抽出する PDF をページ1のみに限定して抽出
    extract_images_from_pdf(input_pdf, temp_output_folder, start_page=0, end_page=1)
    
    # temp_extracted_images/million_Shadowbout_playmat_print_page1.png の背景画像として Background/playmat_norot.jpg に移動
    temp_image_path = os.path.join(temp_output_folder, "million_Shadowbout_playmat_print_page1.png")
    final_image_path = os.path.join(final_output_folder, "playmat_norot.jpg")
    
    # 上下反転させた画像のパス
    final_image_rotated_path = os.path.join(final_output_folder, "playmat_rot.jpg")
    
    # カード画像抽出とクロップ処理
    print("\n--- カード画像（52枚）の抽出とクロップを開始します... ---")
    # 2ページ目 (インデックス 1) から 53ページ目 (インデックス 52) までを抽出
    extract_images_from_pdf(cmyk_pdf, temp_output_folder, start_page=1, end_page=53)

    # ファイルが実際に存在する場合は処理
    if os.path.exists(temp_image_path):
        # 出力フォルダが存在しない場合は作成
        os.makedirs(final_output_folder, exist_ok=True)
        os.makedirs(card_output_folder, exist_ok=True)
        
        # --- プレイマットの処理 ---
        # 画像を読み込み
        img = Image.open(temp_image_path)
        
        # 標準的な非反転画像としてコピー
        shutil.copy(temp_image_path, final_image_path)
        print(f"\nコピー成功: {temp_image_path} -> {final_image_path}")
        
        # 180度回転してコピー
        img_rotated = img.rotate(180)
        img_rotated.save(final_image_rotated_path)
        print(f"180度回転コピー成功: {final_image_rotated_path}")
        
        # 必要に応じて temp ファイル削除
        os.remove(temp_image_path)
        print(f"tmp: {temp_image_path} を削除しました。")

        # 上下結合用の処理

        # 画像の読み込み（念のため再度読み込み、サイズを確認）
        img_norot = Image.open(os.path.join(final_output_folder, "playmat_norot.jpg"))
        img_rot = Image.open(os.path.join(final_output_folder, "playmat_rot.jpg"))

        # 結合先のサイズ設定
        combined_width = img_norot.width
        combined_height = img_norot.height + img_rot.height

        # 結合用の新画像を作成
        combined = Image.new('RGB', (combined_width, combined_height))

        # 上半分（playmat_rot.jpg、180 度回転分）を配置
        combined.paste(img_rot, (0, 0))

        # 下半分（playmat_norot.jpg、標準分）を配置
        combined.paste(img_norot, (0, img_rot.height))

        # 結合画像を WebP 形式で保存
        final_combined_path = os.path.join(final_output_folder, "playmat.webp")
        combined.save(final_combined_path, format='WEBP')
        print(f"上下結合成功: {final_combined_path}")

        # 結合後の playmat.jpg は不要なので削除（必要に応じて）
        os.remove(os.path.join(final_output_folder, "playmat_norot.jpg"))
        os.remove(os.path.join(final_output_folder, "playmat_rot.jpg"))
    else:
        print(f"\nエラー: 画像ファイルが見つかりません - {temp_image_path}")

    # --- カード画像のクロップ処理 ---
    # 2ページ目から53ページ目までの画像ファイル名を想定 (page2.png から page53.png)
    # ページ番号 i は 2から53までループし、カード番号は i-1 を使用する
    for i in range(2, 54): # i は 2から53まで (ファイル名が page2 から page53 のため)
        card_number = i - 1 # カード番号は 1 から 52
        # 抽出されたファイル名 (例: million_Shadowbout52_cmyk_page2.png)
        extracted_filename = f"million_Shadowbout52_cmyk_page{i}.png"
        temp_image_path_card = os.path.join(temp_output_folder, extracted_filename)

        do_back_crop = card_number == 1

        if os.path.exists(temp_image_path_card):
            try:
                # 画像を読み込み
                img_card = Image.open(temp_image_path_card)
                
                # 指定座標 (598, 973) から 指定サイズ (744, 1040) で切り出し (left, top, right, bottom)
                # right = left + width, bottom = top + height
                left = 598
                top = 973
                right = left + 744
                bottom = top + 1040

                if do_back_crop:
                    back_left = 2174
                    back_right = back_left + 744

                cropped_img = img_card.crop((left, top, right, bottom))

                if do_back_crop:
                    back_cropped_img = img_card.crop((back_left, top, back_right, bottom))
                
                # 角丸化とWebP出力の追加
                width, height = cropped_img.size
                radius = 45
                
                # RGBAに変換してからマスクを作成
                converted_img = cropped_img.convert("RGBA")
                if do_back_crop:
                    back_converted_img = back_cropped_img.convert("RGBA")
                mask = Image.new('L', (width, height), 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
                
                # マスクを適用
                converted_img.putalpha(mask)
                if do_back_crop:
                    back_converted_img.putalpha(mask)

                # WebP形式で保存
                final_cropped_path_webp = os.path.join(card_output_folder, f"card_{card_number}.webp")
                converted_img.save(final_cropped_path_webp, 'WEBP')
                print(f"クロップ＆角丸＆WebP保存成功: {extracted_filename} -> card_{card_number}.webp")
                
                if do_back_crop:
                    final_cropped_path_webp = os.path.join(card_output_folder, f"card_back.webp")
                    back_converted_img.save(final_cropped_path_webp, 'WEBP')
                    print(f"カード裏面のクロップ＆角丸＆WebP保存成功: {extracted_filename} -> card_back.webp")                    
                # 一時ファイルを削除
                os.remove(temp_image_path_card)
                    
            except Exception as e:
                print(f"警告: カード画像 {i-1} の処理中にエラーが発生しました: {e}")
        else:
            print(f"警告: 抽出されたファイルが見つかりません - {extracted_filename} (ページ {i})")
    # --- 処理完了後、一時フォルダとカード出力フォルダを削除（オプション）---
    try:
        shutil.rmtree(temp_output_folder)
        print(f"一時フォルダ '{temp_output_folder}' を削除しました。")
    except OSError as e:
        print(f"警告: 一時フォルダ '{temp_output_folder}' の削除に失敗しました (中身がある可能性があります): {e}")

if __name__ == "__main__":
    main()