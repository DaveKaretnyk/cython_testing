#requires -Version 5.0
# Copyright (c) 2021 by FEI Company
# All rights reserved. This file includes confidential & proprietary information of FEI Company.

<#
    .SYNOPSIS
    Run Python mypy check.
    .DESCRIPTION
    Run Python mypy check.
    * Initial tryout of mypy: needs looked at more closely and options refined.
    * The Python environment to use is passed is passed as an arg.

    .INPUTS
    None. You cannot pipe objects to this script.
    .OUTPUTS
    None. Script does not generate any output.
    Calls 'Exit 0' if successful. Else Exit with non-zero value and message to terminal: check
    $LASTEXITCODE and $Error.
#>
if ($args.Length -ne 1) {
    Out-Host -InputObject 'Invoke-LintingMypy: Python env must be supplied as arg'
    Exit 1
}
$envName = $args

# Assumption: using an EDM env located in the standard location.
$activateScript = "C:\FEI\Python\EDM\envs\$envName\Scripts\Activate.ps1"
if (-not (Test-Path -Path $activateScript -PathType Leaf)) {
    Out-Host -InputObject ('Invoke-LintingMypy: no such env: {0}' -f $envName)
    Exit 3
}

$exitCode = 0
$sourceDir = Resolve-Path -Path  "$PSScriptRoot\..\tfs_cythonize.py"

Out-Host -InputObject 'Invoke-LintingMypy: Running mypy check'
Out-Host -InputObject 'Invoke-LintingMypy: ******************'

$resultsDir = Join-Path -Path $PSScriptRoot -ChildPath '..\build\TestResults\mypy'
if (Test-Path $resultsDir -PathType Container) {
    Remove-Item -Path $resultsDir -Recurse
    Out-Host -InputObject ('Invoke-LintingMypy: remove last results dir: {0}' -f $resultsDir)
}
New-Item -ItemType Directory -Force -Path $resultsDir
Out-Host -InputObject ('Invoke-LintingMypy: created dir for results: {0}' -f $resultsDir)

Out-Host -InputObject ('Invoke-LintingMypy: checking directory: {0}' -f $sourceDir)

& $activateScript
Out-Host -InputObject ('Invoke-LintingMypy: activate env: {0}' -f $envName)

$myArgs = @(
    $sourceDir,
    '--config-file', "$PSScriptRoot\tox.ini",
    # options need looked into, e.g. Jenkins build results look different to local run?
    '--any-exprs-report', $resultsDir
    # '--html-report', $resultsDir, needs configured properly? output not navigable?
    # '--lineprecision-report', $resultsDir,
    # '--txt-report', $resultsDir  needs lxml ...
)
& mypy.exe $myArgs

deactivate
Out-Host -InputObject ('Invoke-LintingMypy: deactivate env: {0}' -f $envName)

$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Out-Host -InputObject ('Invoke-LintingMypy: VIOLATIONS PRESENT: {0}' -f $exitCode)
}
else {
    Out-Host -InputObject ('Invoke-LintingMypy: no violations {0}' -f $exitCode)
}

Out-Host -InputObject ('Invoke-LintingMypy: exit code: {0}' -f $exitCode)
Out-Host -InputObject 'Invoke-LintingMypy: **************************'
Exit $exitCode
