param(
    [string]$docxPath,
    [string]$pdfPath
)

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docxPath)
    # Update fields before saving
    $doc.Fields.Update()
    if (Test-Path $pdfPath) {
        Remove-Item $pdfPath -Force
    }
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    $doc.Close([ref]0)
    Write-Host "[OK] Successfully converted to PDF:" $pdfPath
} catch {
    Write-Error $_.Exception.Message
    exit 1
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
