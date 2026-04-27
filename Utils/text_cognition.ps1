New-Item -ErrorAction Ignore -ItemType Directory Artifacts

# 特定箇所をmagickで切り出す
$csv = ""
for ($i = 1; $i -lt 53; $i++) {
    $target = ".\Card\card_${i}.webp"
    # 名前, ポイント, 説明をなんとかして切り出す
    magick $target -crop 360x100+163+44 '.\Artifacts\name.png'
    $result_name_ocr = .\Utils\Get-Win10OcrTextFromImage.ps1 -Path '.\Artifacts\name.png'
    $result_name = $result_name_ocr.Text.Replace(' ', '')
    magick $target -crop 135x194+34+28 '.\Artifacts\point.png'
    $result_point_ocr = .\Utils\Get-Win10OcrTextFromImage.ps1 -Path '.\Artifacts\point.png'
    $result_point = $result_point_ocr.Text.Replace(' ', '')
    magick $target -crop 744x531+0+477 '.\Artifacts\description.png'
    $result_description_ocr = .\Utils\Get-Win10OcrTextFromImage.ps1 -Path '.\Artifacts\description.png'
    $result_description = $result_description_ocr.Text.Replace(' ', '')
    $line = "${result_name}, ${result_point}, ${result_description}`n"
    $csv = $csv + $line
    Remove-Item -ErrorAction Ignore -Path .\Artifacts\name.png
    Remove-Item -ErrorAction Ignore -Path .\Artifacts\point.png
    Remove-Item -ErrorAction Ignore -Path .\Artifacts\description.png
}

$csv | Out-File -FilePath .\card.csv
# いらなくなったフォルダを消す
Remove-Item -Recurse -ErrorAction Ignore -Path .\Artifacts