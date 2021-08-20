#requires -Version 5.0
# Copyright (c) 2021 by FEI Company
# All rights reserved. This file includes confidential & proprietary information of FEI Company.

<#
    .SYNOPSIS
    Run Python mypy check on 'fei_autostar_build' directory.
    .DESCRIPTION
    Run Python mypy check on 'fei_autostar_build' directory.
    * Initial tryout of mypy: needs looked at more closely and options refined.
    * The Python environment does not need to be activated, but it does rely on the env. fetched
      from the build_definitions.yaml config file.

    .INPUTS
    None. You cannot pipe objects to this script.
    .OUTPUTS
    None. Script does not generate any output.
    Calls 'Exit 0' if successful. Else Exit with non-zero value and message to terminal: check
    $LASTEXITCODE and $Error.
#>
# Load dependent modules.
$buildModule = "$PSScriptRoot\..\build\Build.psm1"
Import-Module -Name $buildModule -Force

$exitCode = 0
$sourceDir = "$PSScriptRoot\.." # scan recursively from the root dir for all Python files

Out-Host -InputObject 'Invoke-LintingMypy: Running mypy check'
Out-Host -InputObject 'Invoke-LintingMypy: ******************'

$resultsDir = Join-Path -Path $PSScriptRoot -ChildPath '..\build\TestResults\mypy'
if (Test-Path $resultsDir -PathType Container) {
    Build\Remove-FileSystemItem -Path $resultsDir -Recurse
    Out-Host -InputObject ('Invoke-LintingMypy: remove last results dir: {0}' -f $resultsDir)
}
New-Item -ItemType Directory -Force -Path $resultsDir
Out-Host -InputObject ('Invoke-LintingMypy: created dir for results: {0}' -f $resultsDir)

Out-Host -InputObject ('Invoke-LintingMypy: checking directory: {0}' -f $sourceDir)

$pythonEnvName = Build\Get-EnvName
Build\Enable-PythonEnv -envName $pythonEnvName

$myArgs = @(
    $sourceDir,
    '--config-file', "$PSScriptRoot\tox.ini",
    # options need looked into, e.g. Jenkins build results look different to local run?
    '--any-exprs-report', $resultsDir,
    # '--html-report', $resultsDir, needs configured properly? output not navigable?
    '--lineprecision-report', $resultsDir,
    '--txt-report', $resultsDir
)
& mypy.exe $myArgs

Build\Disable-PythonEnv -envName $pythonEnvName

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
