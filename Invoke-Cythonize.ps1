#requires -Version 5.0
# Copyright (c) 2021 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

<#
    .SYNOPSIS
    Transpiles (cythonizes) all .pyx files in the directory given as input.
    .DESCRIPTION
    Transpiles (cythonizes) all .pyx files in the directory given as input.

    * See tfs_cythonize.py for explanation.
    * The caller must activate the Python env to use before calling this script. And the env
      must contain the Cython package.
    * Directory to be processed is a mandatory arg, all other args are optional, See
      tfs_cythonize.py for full information.
    * This is a PoSh wrapper around a Python script that does the real work.
    * The wrapper ensures that the required environment variables are set before starting the
      Cython build. See function Set-CythonEnv is this script.

    .INPUTS
    None. You cannot pipe objects to this script.
    .OUTPUTS
    None. Script does not generate any output.
    Calls 'Exit 0' if successful. Else Exit with non-zero value and message to terminal: check
    $LASTEXITCODE and $Error.

    .EXAMPLE
    .\Invoke-Cythonize.ps1 C:\github\AutoStar\AutoStar_Common\python\fei
    .EXAMPLE
    .\Invoke-Cythonize.ps1 AutoStar_test --help

#>

Function Set-CythonEnv {
<#
    .SYNOPSIS
    Set the VS2017 environment variables required for building from the command line.
    .DESCRIPTION
    Set the VS2017 environment variables required for building from the command line.
    * There is no supplied Microsoft script/function native to PoSh so the settings are
      derived from bat file equivalents.
    * Relies on file VCVARSALL.BAT. There were issues trying to use the alternative
      VsDevCmd.bat - resulted in incorrect Cython build via Jenkins.
    * Exit called if serious error that cannot be recovered from.
    * After setup list the environment variables to stdout (mainly for trouble shooting).
    * If the key C extension env vars ($ENV:DISTUTILS_USE_SDK and $ENV:PY_VCRUNTIME_REDIST) are
      already set as required then assume all env vars are properly set and do nothing.

    .INPUTS
    None. You cannot pipe objects to this function.
    .OUTPUTS
    None. Function does not generate any output.
#>
    if ($ENV:DISTUTILS_USE_SDK -eq 1 -and $ENV:PY_VCRUNTIME_REDIST -eq 'No thanks') {
        $msg = 'Invoke-Cythonize\Set-CythonEnv: env vars do not need set...'
        Write-Host $msg  -ForegroundColor Yellow
        Out-Host -InputObject '    basis: the key C extension env vars are already set:'
        Out-Host -InputObject ('      $ENV:DISTUTILS_USE_SDK   = {0}' -f $ENV:DISTUTILS_USE_SDK)
        Out-Host -InputObject ('      $ENV:PY_VCRUNTIME_REDIST = {0}' -f $ENV:PY_VCRUNTIME_REDIST)
        return
    }

    # Which script to use to setup the env? VCVARSALL.BAT is the suggestion by, e.g., Dower.
    # I.e. rather than VsDevCmd.bat.
    #     https://stevedower.id.au/blog/building-for-python-3-5-part-two
    $possibleDirs = @(
        # 'C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC', # Visual Studio 2015
        # 'C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build',
        # 'C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\Auxiliary\Build'
        'C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build',
        'C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Auxiliary\Build'
    )
    $targetScript = 'VCVARSALL.bat' # note: this needs a parameter (e.g. amd64)
        
    $targetDir = $NULL
    foreach ($dir in $possibleDirs) {
        $fullScript = Join-Path -Path $dir -ChildPath $targetScript
        if (Test-Path -Path $fullScript -PathType Leaf) {
            $targetDir = $dir
            break
        }
    }
    if ($targetDir) {
        $msg = 'Invoke-Cythonize\Set-CythonEnv: using {0} from: {1}'
        Out-Host -InputObject ($msg -f $targetScript, $targetDir)
    }
    else {
        Out-Host -InputObject ('Invoke-Cythonize\Set-CythonEnv: missing: {0}' -f $targetScript)
        Exit 666
    }

    # Run the bat file for setting up the build environment (part of Visual Studio) then list the
    # environment variables: use that list to create the env. vars in this PoSh instance. From:
    # https://stackoverflow.com/questions/2124753/how-can-i-use-powershell-with-the-visual-studio-command-prompt
    Push-Location -Path $targetDir
    & "$env:ComSpec" /c "$targetScript amd64 && set" |
    ForEach-Object {
        if ($_ -match "=") {
            $v = $_.split("=")
            Set-Item -Force -Path "ENV:\$($v[0])"  -Value "$($v[1])"
        }
    }
    Pop-Location

    # These settings are vital else transpiled Python source uses 'semi-static linking' for the
    # C runtime -> will compile and link OK but will fail (DLL initialization error) at runtime.
    # Explanation here:
    #     https://stevedower.id.au/blog/building-for-python-3-5-part-two/     
    $ENV:DISTUTILS_USE_SDK = 1
    $ENV:PY_VCRUNTIME_REDIST = 'No thanks'

    $envVars = Get-ChildItem Env: | Format-List # Format-List ensures value does not get chopped
    Out-Host -InputObject 'Invoke-Cythonize\Set-CythonEnv: env variables:'
    Out-Host -InputObject $envVars
   
    $msg = 'Invoke-Cythonize\Set-CythonEnv: Visual Studio Command Prompt variables set'
    Write-Host $msg  -ForegroundColor Yellow
}


# ------------------------------------------------------------------------------------------------
# Script code begins here.

$pythonExe = 'python.exe'
$myArgs = @("$PSScriptRoot\tfs_cythonize.py") + $args

if ($myArgs.Contains('--help') -or $myArgs.Contains('-h')) {
    Out-Host -InputObject 'Invoke-Cythonize: just display help...'
}
else {
    Set-CythonEnv # set environment to allow C compilation from command line
}

& $pythonExe $myArgs
$pythonResult = $LASTEXITCODE
if ($pythonResult -ne 0) {
    Out-Host -InputObject ('Invoke-Cythonize: ERROR exit: {0}' -f $pythonResult)
}

Exit $pythonResult
