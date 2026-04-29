# 前に作っていたら削除しておく
Remove-Item -ErrorAction Ignore -Force .\Shadowbout.zip
Remove-Item -ErrorAction Ignore -Force -Recurse Shadowbout

New-Item -ErrorAction Ignore -ItemType Directory Shadowbout

# まず先んじてPlaceholderからカードや背景を全部コピーしておく
Copy-Item -ErrorAction Stop -Path .\Placeholder\*.webp -Destination .\Shadowbout

# 切り出したカード画像などをコピー
Copy-Item -ErrorAction Ignore -Path .\Card\*.webp -Destination .\Shadowbout
Copy-Item -ErrorAction Ignore -Path .\Background\playmat.webp -Destination .\Shadowbout
Copy-Item -ErrorAction Ignore -Path .\XML\roomExportFlag.xml -Destination .\Shadowbout
Copy-Item -ErrorAction Ignore -Path .\XML\summary.xml -Destination .\Shadowbout

$data_xml = Get-Content -Path .\XML\data.xml -Encoding UTF8

# カードを52枚、まず準備する
$card_xml_concat = ""
# デッキA
for ($i = 1; $i -lt 53; $i++) {
    $card_xml = Get-Content -Path .\XML\card.xml -Encoding UTF8
    $card_xml = $card_xml.Replace("CARDDECK", "A")
    $card_xml = $card_xml.Replace("CARDINDEX", $i)
    $card_xml_concat = $card_xml_concat + $card_xml + "`n"
}

$data_xml = $data_xml.Replace("__REPLACE_A_card_xml__", $card_xml_concat)
$card_xml_concat = ""

# デッキB
for ($i = 1; $i -lt 53; $i++) {
    $card_xml = Get-Content -Path .\XML\card.xml -Encoding UTF8
    $card_xml = $card_xml.Replace("CARDDECK", "B")
    $card_xml = $card_xml.Replace("CARDINDEX", $i)
    $card_xml_concat = $card_xml_concat + $card_xml + "`n"
}

$data_xml = $data_xml.Replace("__REPLACE_B_card_xml__", $card_xml_concat)

$data_csv = Import-Csv -Path .\CSV\card.csv -Header "index", "idol", "hand", "point", "item", "profile", "effect", "school"
# カードの差し替え
for ($i = 1; $i -lt 53; $i++) {
    $hash_name = "card_${i}"
    $hash_set = Get-FileHash -Algorithm SHA256 -Path "Shadowbout/${hash_name}.webp"
    $hash = $hash_set.Hash.ToLower()
    $data_xml = $data_xml.Replace("__REPLACE__${hash_name}__", $hash)

    $card = $data_csv | Where-Object -Property index -EQ $i
    $card_idol = $card[0].idol
    $card_hand = $card[0].hand
    $card_point = $card[0].point
    $card_item = $card[0].item
    $card_profile = $card[0].profile
    $card_effect = $card[0].effect
    $card_school = $card[0].school

    $data_xml = $data_xml.Replace("__REPLACE__${hash_name}_idol__", $card_idol)
    $data_xml = $data_xml.Replace("__REPLACE__${hash_name}_hand__", $card_hand)
    $data_xml = $data_xml.Replace("__REPLACE__${hash_name}_point__", $card_point)
    $data_xml = $data_xml.Replace("__REPLACE__${hash_name}_item__", $card_item)
    $data_xml = $data_xml.Replace("__REPLACE__${hash_name}_profile__", $card_profile)
    $data_xml = $data_xml.Replace("__REPLACE__${hash_name}_effect__", $card_effect)
    $data_xml = $data_xml.Replace("__REPLACE__${hash_name}_school__", $card_school)
}

# カードの裏面差し替え
$hash_name = "card_back"
$hash_set = Get-FileHash -Algorithm SHA256 -Path "Shadowbout/${hash_name}.webp"
$hash = $hash_set.Hash.ToLower()
$data_xml = $data_xml.Replace("__REPLACE__${hash_name}__", $hash)

# プレイマットの差し替え
$hash_name = "playmat"
$hash_set = Get-FileHash -Algorithm SHA256 -Path "Shadowbout/${hash_name}.webp"
$hash = $hash_set.Hash.ToLower()
$data_xml = $data_xml.Replace("__REPLACE__${hash_name}__", $hash)

# シンプルテクスチャの差し替え
$hash_name = "simple"
$hash_set = Get-FileHash -Algorithm SHA256 -Path "Shadowbout/${hash_name}.webp"
$hash = $hash_set.Hash.ToLower()
$data_xml = $data_xml.Replace("__REPLACE__${hash_name}__", $hash)

# ハッシュを差し替えたものを保存
$data_xml | Out-File ".\Shadowbout\data.xml"

# ExportLock
#New-Item -ErrorAction Ignore -Path .\Shadowbout\ExportLock

Compress-Archive -Path .\Shadowbout\* -DestinationPath .\Shadowbout.zip