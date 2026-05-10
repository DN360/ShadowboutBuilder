import fitz  # PyMuPDF
import os

def extract_images_from_pdf(pdf_path, output_folder="extracted_images", start_page=0, end_page=None):
    """
    PDFファイルから画像を抽出し、指定されたフォルダに保存します。

    Args:
        pdf_path (str): 入力PDFファイルのパス。
        start_page (int): 処理を開始するページ番号 (0から始まる)。
        end_page (int, optional): 処理を終了するページ番号 (含まない)。Noneの場合は最後のページまで。
    """
    try:
        # 出力フォルダが存在しない場合は作成
        os.makedirs(output_folder, exist_ok=True)
        print(f"出力フォルダ '{output_folder}' を確認/作成しました。")

        # PDFを開く
        pdf_document = fitz.open(pdf_path)
        pdf_path_base = os.path.splitext(os.path.basename(pdf_path))[0]

        print(f"--- PDFファイル '{pdf_path}' から画像を抽出中... ---")

        # 処理するページ範囲を決定
        total_pages = len(pdf_document)
        actual_end_page = end_page if end_page is not None else total_pages

        if start_page < 0 or start_page >= total_pages:
            print(f"\nエラー: 開始ページ番号 {start_page} は範囲外です (0から{total_pages-1})。")
            pdf_document.close()
            return

        if actual_end_page > total_pages:
             print(f"\n注意: 終了ページ番号 {end_page if end_page is not None else '最終ページ'} は総ページ数 {total_pages} を超えています。最終ページまで処理します。")
             actual_end_page = total_pages

        # 各ページを処理
        for page_num in range(start_page, actual_end_page):
            page = pdf_document.load_page(page_num)

            # ページ全体を画像としてレンダリング（キャプチャ）する
            # dpiを上げて高解像度でキャプチャできます (例: dpi=300)
            mat = fitz.Matrix(1.0, 1.0) # ズームを1.0 (デフォルト) に設定
            pix = page.get_pixmap(matrix=mat)

            # ファイル名を生成 (ページ番号をベースにする)
            image_filename = f"{pdf_path_base}_page{page_num+1}.png"
            save_path = os.path.join(output_folder, image_filename)

            # 画像をPNG形式で保存
            pix.save(save_path)

            print(f"  ページ {page_num + 1} を画像として保存しました: {image_filename}")
        pdf_document.close()
        print("\n--- 全てのページのレンダリングと保存が完了しました！ ---")

    except FileNotFoundError:
        print(f"\nエラー: ファイルが見つかりません - {pdf_path}")
    except Exception as e:
        print(f"\n***処理中に致命的な例外が発生しました!\n例外タイプ: {type(e).__name__}\n詳細: {e}***")


if __name__ == "__main__":
    input_pdf = "million_Shadowbout_playmat_print.pdf"
    output_directory = "pdf_images"
    
    # テスト用に、実行前に 'sample.pdf' がカレントディレクトリにあることを確認してください。
    # 例: 3ページ目から5ページ目までを抽出する場合 (0から始まるので 2から 5)
    extract_images_from_pdf(input_pdf, output_directory, start_page=2, end_page=5)
