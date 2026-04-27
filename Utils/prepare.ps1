# 成果物保存フォルダをつくる
New-Item -ErrorAction Ignore -ItemType Directory Card, Convert, Crop, Background

# プレイマットの作成
magick .\million_Shadowbout_playmat_print.pdf -colorspace sRGB Background\playmat_norot.jpg
magick Background\playmat_norot.jpg -rotate +180 Background\playmat_rot.jpg
magick Background\playmat_rot.jpg Background\playmat_norot.jpg -append Background\playmat.webp

# カード裏面作成
magick -colorspace sRGB .\million_Shadowbout52_cmyk.pdf[1] "Convert/card_back.jpg"
magick "Convert/card_back.jpg" -crop 744x1040+2174+973 "Crop/card_back.jpg"
magick "Crop/card_back.jpg" '(' +clone -threshold 101% -fill white -draw "roundRectangle 0,0 %[fx:int(w)],%[fx:int(h)] 45,45" ')' -channel-fx "| gray=>alpha" -colorspace sRGB "Card/card_back.webp"

# カード作成
for ($i = 1; $i -lt 53; $i++) {
    magick -colorspace sRGB .\million_Shadowbout52_cmyk.pdf[$i] "Convert/card_${i}.jpg"
    magick "Convert/card_${i}.jpg" -crop 744x1040+598+973 "Crop/card_${i}.jpg"
    magick "Crop/card_${i}.jpg" '(' +clone -threshold 101% -fill white -draw "roundRectangle 0,0 %[fx:int(w)],%[fx:int(h)] 45,45" ')' -channel-fx "| gray=>alpha" -colorspace sRGB "Card/card_${i}.webp"
}

# 必要なくなったフォルダを削除
Remove-Item -Recurse Convert, Crop