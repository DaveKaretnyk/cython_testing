#requires -Version 5.0
# Copyright (c) 2021 by FEI Company
# All rights reserved. This file includes confidential & proprietary information of FEI Company.

<#
    .SYNOPSIS
    Run Python mypy check on 'tfs_cythonize.py'.
    .DESCRIPTION
    Run Python mypy check on 'tfs_cythonize.py'.
    * Initial tryout of mypy: needs looked at more closely and options refined.
    * The Python env to be used must be supplied.

    .INPUTS
    None. You cannot pipe objects to this script.
    .OUTPUTS
    None. Script does not generate any output.
    Calls 'Exit 0' if successful. Else Exit with non-zero value and message to terminal: check
    $LASTEXITCODE and $Error.
#>
if ($args.Length -eq 0) {
    Out-Host -InputObject 'Invoke-LintingMypy: no EDM Python env supplied'
    Exit 3
}
$envName = $args[0]
$activateScript = "C:\FEI\Python\EDM\envs\$envName\Scripts\Activate.ps1"
if (-not (Test-Path -Path $activateScript -PathType Leaf)) {
    $msg = 'Invoke-LintingMypy: cannot find env activate script: {0}'
    Out-Host -InputObject ($msg -f $activateScript)
    Exit 5
}

$exitCode = 0
$sourceFile = Resolve-Path -Path  "$PSScriptRoot\..\tfs_cythonize.py"

Out-Host -InputObject 'Invoke-LintingMypy: Running mypy check'
Out-Host -InputObject 'Invoke-LintingMypy: ******************'

$resultsDir = Join-Path -Path $PSScriptRoot -ChildPath '..\build\TestResults\mypy'
$resultsDir = Resolve-Path -Path $resultsDir
if (Test-Path $resultsDir -PathType Container) {
    Remove-Item -Path $resultsDir -Recurse
    Out-Host -InputObject ('Invoke-LintingMypy: remove last results dir: {0}' -f $resultsDir)
}
New-Item -ItemType Directory -Force -Path $resultsDir
Out-Host -InputObject ('Invoke-LintingMypy: created dir for results: {0}' -f $resultsDir)

Out-Host -InputObject ('Invoke-LintingMypy: checking file: {0}' -f $sourceFile)

& $activateScript

$myArgs = @(
    $sourceFile,
    '--config-file',            "$PSScriptRoot\tox.ini",
    # options need looked into, e.g. Jenkins build results look different to local run?
    '--any-exprs-report',       $resultsDir
    #'--lineprecision-report',   $resultsDir
    # html & text reports need lxml package...
    # '--html-report', $resultsDir # needs configured properly? output not navigable?
    # '--txt-report',             $resultsDir
)
& mypy.exe $myArgs

deactivate

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
