Remove-Item -ErrorAction Ignore -Recurse -Path Background
Remove-Item -ErrorAction Ignore -Recurse -Path Card
Remove-Item -ErrorAction Ignore -Recurse -Path Shadowbout
Remove-Item -ErrorAction Ignore -Recurse .\Shadowbout
Remove-Item -ErrorAction Ignore .\Shadowbout.zip
Remove-Item -ErrorAction Ignore .\*.pdf

New-Item -ErrorAction Ignore -ItemType Directory -Path Card
Copy-Item .\Placeholder\card_*.webp .\Card
New-Item -ErrorAction Ignore -ItemType Directory -Path Background
Copy-Item .\Placeholder\playmat.webp .\Background