param(
    [Parameter(Mandatory=$true)][string]$ImagePath,
    [string]$Lang = "auto"
)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Foundation.IAsyncOperation`1, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics, ContentType = WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
})[0]

Function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

Function ExtractLinesFromResult($ocrRes) {
    $list = @()
    if (-not $ocrRes -or -not $ocrRes.Lines) { return $list }
    foreach ($line in $ocrRes.Lines) {
        $minX = 999999; $minY = 999999; $maxR = 0; $maxB = 0
        $wordsList = @()
        foreach ($word in $line.Words) {
            $r = $word.BoundingRect
            $wx = [int]$r.X; $wy = [int]$r.Y; $ww = [int]$r.Width; $wh = [int]$r.Height
            if ($wx -lt $minX) { $minX = $wx }
            if ($wy -lt $minY) { $minY = $wy }
            if (($wx + $ww) -gt $maxR) { $maxR = ($wx + $ww) }
            if (($wy + $wh) -gt $maxB) { $maxB = ($wy + $wh) }
            $wordsList += @{ text = $word.Text; x = $wx; y = $wy; width = $ww; height = $wh }
        }
        if ($minX -eq 999999) { $minX = 10; $minY = 10; $maxR = 200; $maxB = 40 }
        $lw = [Math]::Max(24, ($maxR - $minX))
        $lh = [Math]::Max(18, ($maxB - $minY))
        $list += @{
            text = $line.Text
            x = $minX; y = $minY; width = $lw; height = $lh; w = $lw; h = $lh
            words = $wordsList
        }
    }
    return $list
}

try {
    $fullPath = [System.IO.Path]::GetFullPath($ImagePath)
    $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($fullPath)) ([Windows.Storage.StorageFile])
    $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])

    $avail = [Windows.Media.Ocr.OcrEngine]::AvailableRecognizerLanguages
    $arEngine = $null
    $enEngine = $null
    foreach ($l in $avail) {
        $tag = $l.LanguageTag.ToLower()
        if (-not $arEngine -and $tag.StartsWith("ar")) {
            $arEngine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($l)
        }
        if (-not $enEngine -and $tag.StartsWith("en")) {
            $enEngine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($l)
        }
    }

    $chosenLines = @()
    $fullText = ""

    if ($Lang -eq "ar" -or $Lang -eq "ara") {
        $eng = if ($arEngine) { $arEngine } else { [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages() }
        if ($eng) {
            $res = Await ($eng.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
            $chosenLines = ExtractLinesFromResult $res
            $fullText = $res.Text
        }
    } elseif ($Lang -eq "en" -or $Lang -eq "eng") {
        $eng = if ($enEngine) { $enEngine } else { [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages() }
        if ($eng) {
            $res = Await ($eng.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
            $chosenLines = ExtractLinesFromResult $res
            $fullText = $res.Text
        }
    } else {
        # Auto mode: run both Arabic and English if available, and pick or combine!
        $resAr = if ($arEngine) { Await ($arEngine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult]) } else { $null }
        $resEn = if ($enEngine) { Await ($enEngine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult]) } else { $null }

        $linesAr = ExtractLinesFromResult $resAr
        $linesEn = ExtractLinesFromResult $resEn

        $arCharCount = if ($resAr -and $resAr.Text) { ([regex]::Matches($resAr.Text, "[\u0600-\u06FF]")).Count } else { 0 }
        $enCharCount = if ($resEn -and $resEn.Text) { ([regex]::Matches($resEn.Text, "[A-Za-z]")).Count } else { 0 }

        if ($arCharCount -gt $enCharCount -and $linesAr.Count -gt 0) {
            $chosenLines = $linesAr
            $fullText = $resAr.Text
        } elseif ($linesEn.Count -gt 0) {
            $chosenLines = $linesEn
            $fullText = $resEn.Text
        } elseif ($linesAr.Count -gt 0) {
            $chosenLines = $linesAr
            $fullText = $resAr.Text
        } else {
            $fallbackEng = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
            if ($fallbackEng) {
                $resFb = Await ($fallbackEng.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
                $chosenLines = ExtractLinesFromResult $resFb
                $fullText = $resFb.Text
            }
        }
    }

    $outObj = @{
        ok = ($chosenLines.Count -gt 0)
        engine = "Windows.Media.Ocr.OcrEngine (WinRT Native Bilingual)"
        fullText = $fullText
        imgWidth = [int]$bitmap.PixelWidth
        imgHeight = [int]$bitmap.PixelHeight
        lines = $chosenLines
    }
    $outObj | ConvertTo-Json -Depth 6 -Compress
} catch {
    $errObj = @{
        ok = $false
        error = $_.Exception.Message
    }
    $errObj | ConvertTo-Json -Compress
}
