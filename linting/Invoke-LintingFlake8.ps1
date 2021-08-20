#requires -Version 5.0
# Copyright (c) 2021 by FEI Company
# All rights reserved. This file includes confidential & proprietary information of FEI Company.

<#
    .SYNOPSIS
    Run Python flake8 check on all Python code in repo.
    .DESCRIPTION
    Run Python flake8 check on all Python code in repo.
    * The Python env to be used must be supplied.

    .INPUTS
    None. You cannot pipe objects to this script.
    .OUTPUTS
    None. Script does not generate any output.
    Calls 'Exit 0' if successful. Else Exit with non-zero value and message to terminal: check
    $LASTEXITCODE and $Error.
#>
if ($args.Length -eq 0) {
    Out-Host -InputObject 'Invoke-LintingFlake8: no EDM Python env supplied'
    Exit 3
}
$envName = $args[0]
$activateScript = "C:\FEI\Python\EDM\envs\$envName\Scripts\Activate.ps1"
if (-not (Test-Path -Path $activateScript -PathType Leaf)) {
    $msg = 'Invoke-LintingFlake8: cannot find env activate script: {0}'
    Out-Host -InputObject ($msg -f $activateScript)
    Exit 5
}

$exitCode = 0
$sourceDir = "$PSScriptRoot\.."

Out-Host -InputObject 'Invoke-LintingFlake8: Running flake8 check'
Out-Host -InputObject 'Invoke-LintingFlake8: ********************'

$resultsDir = Join-Path -Path $sourceDir -ChildPath '\build\TestResults'
if (-not (Test-Path $resultsDir -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $resultsDir
    Out-Host -InputObject ('Invoke-LintingFlake8: created dir for results: {0}' -f $resultsDir)
}

$codeOutputFile = Join-Path $resultsDir -ChildPath 'flake8.txt'
if (Test-Path $codeOutputFile -PathType Leaf) {
    Remove-Item -Path $codeOutputFile -Force
    Out-Host -InputObject ('Invoke-LintingFlake8: removed last results: {0}' -f $codeOutputFile)
}

Out-Host -InputObject ('Invoke-LintingFlake8: checking directory: {0}' -f $sourceDir)

& $activateScript
flake8.exe $sourceDir  --config "$PSScriptRoot\tox.ini"  --output=$codeOutputFile
deactivate

$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Out-Host -InputObject ('Invoke-LintingFlake8: VIOLATIONS PRESENT: {0}' -f $exitCode)
}
else {
    Out-Host -InputObject ('Invoke-LintingFlake8: no violations {0}' -f $exitCode)
}

Out-Host -InputObject ('Invoke-LintingFlake8: exit code: {0}' -f $exitCode)
Out-Host -InputObject 'Invoke-LintingFlake8: **************************'
Exit $exitCode
