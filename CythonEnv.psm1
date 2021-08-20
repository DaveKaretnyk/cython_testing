#requires -Version 5.0
# Copyright (c) 2019-2021 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

Function Set-DevEnv {
<#
    .SYNOPSIS
    Set the VS2017 environment variables required for building from the command line.
    .DESCRIPTION
    Set the VS2017 environment variables required for building from the command line.
    * There is no supplied Microsoft script/function native to PoSh (needs VS2019) so the settings
      are derived from bat file equivalents.
    * Relies on file VCVARSALL.BAT. There were issues trying to use the alternative VsDevCmd.bat
      - resulted in incorrect Cython build via Jenkins.
    * Also sets the following key vars needed for Cython builds to work (i.e. these are not set
      via VCVARSALL.BAT):
            $ENV:DISTUTILS_USE_SDK = 1
            $ENV:PY_VCRUNTIME_REDIST='No thanks'
      Though these are not specific to Cython extensions, they should be used when building any
      C extension.
    * Exit called if serious error that cannot be recovered from.
    * After setup list the environment variables to stdout (mainly for trouble shooting).

    .INPUTS
    None. You cannot pipe objects to this function.
    .OUTPUTS
    None. Function does not generate any output.
#>
    # Which script to use to setup the env? VCVARSALL.BAT is the suggestion by, e.g., Dower.
    #     https://stevedower.id.au/blog/building-for-python-3-5-part-two
    # $possibleDirs = @(
    #    'C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\Common7\Tools',
    #    'C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\Common7\Tools'
    # )
    # $targetScript = 'VsDevCmd.bat' # needs no parameters
    $possibleDirs = @(
        # 'C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC', # Visual Studio 2015
        'C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build',
        'C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\Auxiliary\Build'
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
        $msg = 'CythonEnv\Set-DevEnv: using {0} from: {1}'
        Out-Host -InputObject ($msg -f $targetScript, $targetDir)
    }
    else {
        Out-Host -InputObject ('CythonEnv\Set-DevEnv: missing: {0}' -f $targetScript)
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
    #     https://stevedower.id.au/blog/building-for-python-3-5-part-two
    $ENV:DISTUTILS_USE_SDK = 1
    $ENV:PY_VCRUNTIME_REDIST='No thanks'

    $envVars = Get-ChildItem Env: | Format-List # Format-List ensures value does not get chopped
    Out-Host -InputObject 'CythonEnv\Set-DevEnv: env variables:'
    Out-Host -InputObject $envVars
   
    $msg = 'CythonEnv\Set-DevEnv: Visual Studio Command Prompt variables set'
    Write-Host $msg  -ForegroundColor Yellow
}

Function Set-DevEnvClean {
<#
    .SYNOPSIS
    Set the VS2017 environment variables required for building from the command line.
    .DESCRIPTION
    Set the VS2017 environment variables required for building from the command line.
    * There is no supplied Microsoft script/function native to PoSh (needs VS2019) so the settings
      are derived from bat file equivalents.
    * Relies on file VCVARSALL.BAT. There were issues trying to use the alternative VsDevCmd.bat
      - resulted in incorrect Cython build via Jenkins.
    * Also sets the following key vars needed for Cython builds to work (i.e. these are not set
      via VCVARSALL.BAT):
            $ENV:DISTUTILS_USE_SDK = 1
            $ENV:PY_VCRUNTIME_REDIST='No thanks'
      Though these are not specific to Cython extensions, they should be used when building any
      C extension.
    * Exit called if serious error that cannot be recovered from.
    * After setup list the environment variables to stdout (mainly for trouble shooting).
    * Difference compared to Set-DevEnv used previously in AutoStar?
        * Get the env vars via a temp file.
        * The vars of the current instance are cleared => the final set of vars are ONLY those
          supplied via VCVARSALL.BAT and whatever thd cmd shell creates when first instantiated.
        * Comes via John Robbins at Wintellect:
          https://github.com/Wintellect/WintellectPowerShell/blob/master/Code/Invoke-CmdScript.ps1

    .INPUTS
    None. You cannot pipe objects to this function.
    .OUTPUTS
    None. Function does not generate any output.
#>

    # Which script to use to setup the env? VCVARSALL.BAT is the suggestion by, e.g., Dower.
    #     https://stevedower.id.au/blog/building-for-python-3-5-part-two
    # $possibleDirs = @(
    #    'C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\Common7\Tools',
    #    'C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\Common7\Tools'
    # )
    # $targetScript = 'VsDevCmd.bat' # needs no parameters
    $possibleDirs = @(
        # 'C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC', # Visual Studio 2015
        'C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build',
        'C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\Auxiliary\Build'
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
        $msg = 'CythonEnv\Set-DevEnvClean: using {0} from: {1}'
        Out-Host -InputObject ($msg -f $targetScript, $targetDir)
    }
    else {
        Out-Host -InputObject ('CythonEnv\Set-DevEnvClean: missing: {0}' -f $targetScript)
        Exit 666
    }

    $envVars = Get-ChildItem Env: | Format-List # Format-List ensures value does not get chopped
    Out-Host -InputObject 'CythonEnv\Set-DevEnvClean: env variables (BEFORE):'
    Out-Host -InputObject $envVars

    $tempFile = [IO.Path]::GetTempFileName()  

    # Logic extracted from the following script:
    #   https://github.com/Wintellect/WintellectPowerShell/blob/master/Code/Invoke-CmdScript.ps1
    Push-Location -Path $targetDir
    & "$ENV:ComSpec" /c "$targetScript amd64 && set > $tempFile"
    if ($LASTEXITCODE -ne 0)
    {
        $msg = 'CythonEnv\Set-DevEnvClean: error executing {0} via cmd.exe: {1}'
        Out-Host -InputObject ($msg -f $targetScript, $LASTEXITCODE)
    }
    Pop-Location

    # Before we delete the environment variables get the output into a string
    # array.
    $vars = Get-Content -Path $tempFile
    Out-Host -InputObject ('CythonEnv\Set-DevEnvClean: temp file: {0}' -f $tempFile)

    # Clear out all current environment variables in PowerShell.
    Get-ChildItem -Path ENV:\ | Foreach-Object { 
                    set-item -force -path "ENV:\$($_.Name)" -value "" 
                }

    $envVars = Get-ChildItem Env: | Format-List # Format-List ensures value does not get chopped
    Out-Host -InputObject 'CythonEnv\Set-DevEnvClean: env variables (CLEARED):'
    Out-Host -InputObject $envVars
            
    ## Go through the environment variables in the temp file.  
    ## For each of them, set the variable in our local environment.  
    $vars | Foreach-Object {   
                        if($_ -match "^(.*?)=(.*)$")  
                        { 
                            Set-Content -Path "ENV:\$($matches[1])" -Value $matches[2]
                        } 
                    }

    # These settings are vital else transpiled Python source uses 'semi-static linking' for the
    # C runtime -> will compile and link OK but will fail (DLL initialization error) at runtime.
    # Explanation here:
    #     https://stevedower.id.au/blog/building-for-python-3-5-part-two
    $ENV:DISTUTILS_USE_SDK = 1
    $ENV:PY_VCRUNTIME_REDIST='No thanks'

    $envVars = Get-ChildItem Env: | Format-List # Format-List ensures value does not get chopped
    Out-Host -InputObject 'CythonEnv\Set-DevEnvClean: env variables (AFTER):'
    Out-Host -InputObject $envVars
    
    $msg = 'CythonEnv\Set-DevEnvClean: Visual Studio Command Prompt variables set'
    Write-Host $msg  -ForegroundColor Yellow
}
