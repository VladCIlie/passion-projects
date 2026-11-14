#Requires -Version 5.1
<#
.SYNOPSIS
    Menu-driven wizard that automates a recurring bulk XML import workflow.

.DESCRIPTION
    The workflow replaces a manual checklist that had to be executed the same
    way for every batch:

      1. Validate that exactly one correctly named .zip archive exists.
      2. Extract the XML payload files from the archive.
      3. Empty the import folder.
      4. Empty the results folder.
      5. Copy the extracted XML files into the import folder.
      6. Trigger the downstream processing jobs in order.

    Every step can be run individually (with confirmation prompts) or fully
    automated in sequence (menu option 'a').

.NOTES
    Placeholder paths live in the $Config block at the top - adjust them
    to your environment.
#>

$Config = @{
    # Folder in which the input .zip archive is expected to appear.
    ArchiveFolder = $env:USERPROFILE

    # Target folder consumed by the downstream import job.
    ImportFolder  = 'C:\BulkImport\Import\incoming'

    # Folder filled by the downstream import job; emptied before each batch.
    ResultsFolder = 'C:\BulkImport\Import\results'

    # External .cmd jobs executed in order by step 6.
    JobCommands   = @(
        'C:\BulkImport\jobs\reset-database.cmd'
        'C:\BulkImport\jobs\convert.cmd'
        'C:\BulkImport\jobs\export.cmd'
    )
}

$script:XmlFilesToCopy = @()
$script:AutoMode   = $false
$script:Step1Done  = $false
$script:Step2Done  = $false
$script:Step3Done  = $false
$script:Step4Done  = $false
$script:Step5Done  = $false

function Invoke-NextStep {
    Write-Host 'Continuing...'
    Start-Sleep -Seconds 1
}

function Complete-AndExit {
    Write-Host 'Done. You can move on to the next machine. Press any key to exit.'
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit
}

function Confirm-OrMenu {
    if ($script:AutoMode) {
        Invoke-NextStep
        return $true
    }

    $confirmation = Read-Host 'Choose y or n'

    if ($confirmation -eq 'y') {
        Invoke-NextStep
        return $true
    }

    if ($confirmation -eq 'n') {
        Write-Host 'Returning to the menu...'
        Pause
        return $false
    }

    Write-Host 'Invalid choice. Returning to the menu.'
    Pause
    return $false
}

function Get-SingleArchive {
    $zipFiles = Get-ChildItem -Path $Config.ArchiveFolder -Filter '*.zip' -File

    if ($zipFiles.Count -eq 0) {
        Write-Host 'No .zip file found in the expected folder. Please check.'
        Pause
        return $null
    }

    if ($zipFiles.Count -gt 1) {
        Write-Host 'More than one .zip file found. Leave exactly one for the workflow to proceed.'
        Pause
        return $null
    }

    if ($zipFiles[0].BaseName -notmatch '^\d+$') {
        Write-Host 'Invalid archive name - a numeric batch identifier is expected.'
        Pause
        return $null
    }

    return $zipFiles[0]
}

function Step1-ValidateArchive {
    Clear-Host

    $zipFile = Get-SingleArchive
    if ($null -eq $zipFile) {
        return $false
    }

    if ($script:AutoMode) {
        Write-Host "Found archive: $($zipFile.Name)."
        $script:Step1Done = $true
        Invoke-NextStep
        return $true
    }

    Write-Host "Found archive: $($zipFile.Name). Is this correct?"
    Write-Host '(y - continue / n - back to menu)'

    $result = Confirm-OrMenu
    if ($result) {
        $script:Step1Done = $true
    }
    return $result
}

function Step2-ExtractXml {
    Clear-Host

    $zipFile = Get-SingleArchive
    if ($null -eq $zipFile) {
        return $false
    }

    $extractFolder = Join-Path $env:TEMP ('BulkImport_' + $zipFile.BaseName)

    if (Test-Path $extractFolder) {
        Remove-Item -Path $extractFolder -Recurse -Force
    }

    Expand-Archive -LiteralPath $zipFile.FullName -DestinationPath $extractFolder -Force

    $xmlFiles = Get-ChildItem -Path $extractFolder -Filter '*.xml' -File -Recurse

    if ($xmlFiles.Count -eq 0) {
        Write-Host 'No XML files found inside the archive.'
        Pause
        return $false
    }

    $invalidXml = $xmlFiles | Where-Object { $_.BaseName -notmatch '^\d+$' }

    if ($invalidXml.Count -gt 0) {
        Write-Host 'At least one XML file does not match the expected naming convention. Please verify.'
        Pause
        return $false
    }

    $script:XmlFilesToCopy = $xmlFiles
    $xmlFiles | Set-Clipboard

    if ($script:AutoMode) {
        Write-Host "Copied $($xmlFiles.Count) XML files."
        $script:Step2Done = $true
        Invoke-NextStep
        return $true
    }

    Write-Host "Copied $($xmlFiles.Count) XML files. Is this correct?"
    Write-Host '(y - continue / n - back to menu)'

    $result = Confirm-OrMenu
    if ($result) {
        $script:Step2Done = $true
    }
    return $result
}

function Clear-BatchFolder {
    param (
        [string]$FolderPath,
        [string]$FolderName
    )

    Clear-Host

    if (-not (Test-Path $FolderPath)) {
        Write-Host "Folder $FolderName does not exist or cannot be accessed."
        Pause
        return $false
    }

    Get-ChildItem -Path $FolderPath -Force | Remove-Item -Recurse -Force

    Write-Host "Emptied folder $FolderName."

    if ($script:AutoMode) {
        Invoke-NextStep
        return $true
    }

    Write-Host '(y - continue / n - back to menu)'
    return (Confirm-OrMenu)
}

function Step3-ClearImportFolder {
    $result = Clear-BatchFolder `
        -FolderPath $Config.ImportFolder `
        -FolderName 'Import'

    if ($result) {
        $script:Step3Done = $true
    }
    return $result
}

function Step4-ClearResultsFolder {
    $result = Clear-BatchFolder `
        -FolderPath $Config.ResultsFolder `
        -FolderName 'Results'

    if ($result) {
        $script:Step4Done = $true
    }
    return $result
}

function Step5-CopyXmlFiles {
    Clear-Host

    if ($script:XmlFilesToCopy.Count -eq 0) {
        Write-Host 'No XML files staged for copying. Run step 2 first.'
        Pause
        return $false
    }

    if (-not (Test-Path $Config.ImportFolder)) {
        Write-Host 'Import folder does not exist or cannot be accessed.'
        Pause
        return $false
    }

    Copy-Item -LiteralPath $script:XmlFilesToCopy.FullName -Destination $Config.ImportFolder -Force
    $script:Step5Done = $true

    Invoke-NextStep
    return $true
}

function Invoke-CmdFile {
    param (
        [string]$CmdPath
    )

    if (-not (Test-Path $CmdPath)) {
        return $false
    }

    $proc = Start-Process -FilePath 'cmd.exe' -ArgumentList "/c `"$CmdPath`"" -PassThru -Wait

    return ($proc.ExitCode -eq 0)
}

function Step6-RunJobs {
    Clear-Host

    $anyStepDone = ($script:Step1Done -or $script:Step2Done -or $script:Step3Done -or
                    $script:Step4Done -or $script:Step5Done)

    if (-not $script:AutoMode -and -not $anyStepDone) {
        Write-Host 'Are you sure you want to jump straight to step 6? Have you completed the earlier steps?'
        Write-Host '(y - continue / n - back to menu)'

        $confirmation = Read-Host 'Choose y or n'

        if ($confirmation -eq 'n') {
            Write-Host 'Returning to the menu...'
            Pause
            return $false
        }

        if ($confirmation -ne 'y') {
            Write-Host 'Invalid choice. Returning to the menu.'
            Pause
            return $false
        }

        Invoke-NextStep
    }

    foreach ($cmdFile in $Config.JobCommands) {
        $result = Invoke-CmdFile -CmdPath $cmdFile

        if (-not $result) {
            Write-Host 'A job did not exit cleanly. Please retry.'
            Pause
            return $false
        }
    }

    Complete-AndExit
    return $true
}

function Invoke-AllSteps {
    $script:AutoMode = $true

    if (-not (Step1-ValidateArchive))  { $script:AutoMode = $false; return }
    if (-not (Step2-ExtractXml))       { $script:AutoMode = $false; return }
    if (-not (Step3-ClearImportFolder)){ $script:AutoMode = $false; return }
    if (-not (Step4-ClearResultsFolder)){ $script:AutoMode = $false; return }
    if (-not (Step5-CopyXmlFiles))     { $script:AutoMode = $false; return }

    Step6-RunJobs | Out-Null
    $script:AutoMode = $false
}

do {
    $script:AutoMode = $false
    Clear-Host

    Write-Host 'Bulk Import Wizard - part 1'
    Write-Host '1) Validate .zip archive'
    Write-Host '2) Extract XML files'
    Write-Host '3) Empty the import folder'
    Write-Host '4) Empty the results folder'
    Write-Host '5) Copy new XML files into the import folder'
    Write-Host '6) Run the processing jobs'
    Write-Host ''
    Write-Host 'a) Run all steps automatically, without confirmation'
    Write-Host ''
    Write-Host '0) Exit'

    $option = Read-Host 'Choose an option'

    switch ($option.ToLower()) {
        '1' { Step1-ValidateArchive   | Out-Null }
        '2' { Step2-ExtractXml        | Out-Null }
        '3' { Step3-ClearImportFolder | Out-Null }
        '4' { Step4-ClearResultsFolder| Out-Null }
        '5' { Step5-CopyXmlFiles      | Out-Null }
        '6' { Step6-RunJobs           | Out-Null }
        'a' { Invoke-AllSteps }
        '0' { Write-Host 'Closing...' }
        default {
            Write-Host 'Invalid option. Try again.'
            Pause
        }
    }

} while ($option -ne '0')
