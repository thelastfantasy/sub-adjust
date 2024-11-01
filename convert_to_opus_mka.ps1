# 获取当前活动目录中所有 .mka 文件
$mkaFiles = Get-ChildItem -Path . -Filter *.mka

# 检查目录中是否存在 .mka 文件
if ($mkaFiles.Count -eq 0) {
    Write-Host "当前目录中没有找到任何 .mka 文件。"
    exit
}

foreach ($file in $mkaFiles) {
    # 获取当前文件路径和文件名
    $inputFile = $file.FullName
    # 如果文件名已经包含 "_128k"，则不再追加
    $outputFile = if ($inputFile -notmatch "_128k\.mka$") {
        [System.IO.Path]::ChangeExtension($inputFile, "_128k.mka")
    }
    else {
        $inputFile
    }

    # 使用 ffmpeg 获取音频流信息并匹配声道数
    $ffmpegOutput = & ffmpeg -i $inputFile -hide_banner 2>&1
    $channels = 0

    # 匹配包含 Stream 和 Audio 的行，提取声道数，如 "5.1(side)"
    foreach ($line in $ffmpegOutput) {
        if ($line -match "Stream.*Audio:.*?(\d+)\.(\d)") {
            # 提取小数点前后的数字
            $mainChannels = [int]$matches[1]
            $subChannels = [int]$matches[2]
            # 声道数为小数点前后数字的和
            $channels = $mainChannels + $subChannels
            break
        }
    }

    # 检查声道数是否获取成功
    if ($channels -eq 0) {
        Write-Host "无法获取声道数：$inputFile，跳过该文件。"
        continue
    }

    Write-Host "正在处理文件 $($file.Name)，识别到声道数: $channels"

    # 使用 ffmpeg 进行 VBR 转换
    & ffmpeg -i $inputFile -c:a libopus -b:a 128k -vbr on -ac $channels -f matroska $outputFile *> $null 2>&1

    # 检查文件大小确认转换是否成功
    if ((Test-Path $outputFile) -and ((Get-Item $outputFile).length -gt 0)) {
        Write-Host "转换完成！文件已保存为 $outputFile"
    }
    else {
        Write-Host "转换失败：$inputFile"
    }
}
