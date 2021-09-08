#requires -Version 5.0
# Copyright (c) 2021 by FEI Company
# All rights reserved. This file includes confidential & proprietary information of FEI Company.

<#
    .SYNOPSIS
    Run Python flake8 checks.
    .DESCRIPTION
    Run Python flake8 checks.
    * The Python environment to use is passed is passed as an arg.

    .INPUTS
    None. You cannot pipe objects to this script.
    .OUTPUTS
    None. Script does not generate any output.
    Calls 'Exit 0' if successful. Else Exit with non-zero value and message to terminal: check
    $LASTEXITCODE and $Error.
#>
if ($args.Length -ne 1) {
    Out-Host -InputObject 'Invoke-LintingFlake8: Python env must be supplied as arg'
    Exit 1
}
$envName = $args

# Assumption: using an EDM env located in the standard location.
$activateScript = "C:\FEI\Python\EDM\envs\$envName\Scripts\Activate.ps1"
if (-not (Test-Path -Path $activateScript -PathType Leaf)) {
    Out-Host -InputObject ('Invoke-LintingFlake8: no such env: {0}' -f $envName)
    Exit 3
}

$exitCode = 0
$sourceDir = Resolve-Path -Path "$PSScriptRoot\.."

Out-Host -InputObject 'Invoke-LintingFlake8: Running flake8 check'
Out-Host -InputObject 'Invoke-LintingFlake8: ********************'

$resultsDir = Join-Path -Path $sourceDir -ChildPath 'build\TestResults'
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
Out-Host -InputObject ('Invoke-LintingFlake8: activate env: {0}' -f $envName)

flake8.exe $soureDir  --config "$PSScriptRoot\tox.ini"  --output=$codeOutputFile

deactivate # the Python env
Out-Host -InputObject ('Invoke-LintingFlake8: deactivate env: {0}' -f $envName)

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
