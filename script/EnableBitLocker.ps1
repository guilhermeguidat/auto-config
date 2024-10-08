# Verificar os pré-requisitos do BitLocker
$TPMNotEnabled = Get-WmiObject win32_tpm -Namespace root\cimv2\security\microsofttpm | where {$_.IsEnabled_InitialValue -eq $false} -ErrorAction SilentlyContinue
$TPMEnabled = Get-WmiObject win32_tpm -Namespace root\cimv2\security\microsofttpm | where {$_.IsEnabled_InitialValue -eq $true} -ErrorAction SilentlyContinue
$WindowsVer = Get-WmiObject -Query 'select * from Win32_OperatingSystem where (Version like "6.2%" or Version like "6.3%" or Version like "10.0%") and ProductType = "1"' -ErrorAction SilentlyContinue
$BitLockerReadyDrive = Get-BitLockerVolume -MountPoint $env:SystemDrive -ErrorAction SilentlyContinue
$BitLockerDecrypted = Get-BitLockerVolume -MountPoint $env:SystemDrive | where {$_.VolumeStatus -eq "FullyDecrypted"} -ErrorAction SilentlyContinue
$BLVS = Get-BitLockerVolume | Where-Object {$_.KeyProtector | Where-Object {$_.KeyProtectorType -eq 'RecoveryPassword'}} -ErrorAction SilentlyContinue

# Passo 1 - Verificar se o TPM está habilitado e inicializar se necessário
if ($WindowsVer -and !$TPMNotEnabled) 
{
    Initialize-Tpm -AllowClear -AllowPhysicalPresence -ErrorAction SilentlyContinue
}

# Passo 2 - Verificar se o volume BitLocker está provisionado e particionar o drive do sistema se necessário
if ($WindowsVer -and $TPMEnabled -and !$BitLockerReadyDrive) 
{
    Get-Service -Name defragsvc -ErrorAction SilentlyContinue | Set-Service -Status Running -ErrorAction SilentlyContinue
    BdeHdCfg -target $env:SystemDrive shrink -quiet
}

# Passo 3 - Verificar se as chaves de backup do AD BitLocker existem no Registro e criá-las se não existirem
$BitLockerRegLoc = 'HKLM:\SOFTWARE\Policies\Microsoft'
if (!(Test-Path "$BitLockerRegLoc\FVE"))
{
    New-Item -Path "$BitLockerRegLoc" -Name 'FVE'
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'ActiveDirectoryBackup' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'RequireActiveDirectoryBackup' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'ActiveDirectoryInfoToStore' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'EncryptionMethodNoDiffuser' -Value '00000003' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'EncryptionMethodWithXtsOs' -Value '00000006' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'EncryptionMethodWithXtsFdv' -Value '00000006' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'EncryptionMethodWithXtsRdv' -Value '00000003' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'EncryptionMethod' -Value '00000003' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'OSRecovery' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'OSManageDRA' -Value '00000000' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'OSRecoveryPassword' -Value '00000002' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'OSRecoveryKey' -Value '00000002' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'OSHideRecoveryPage' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'OSActiveDirectoryBackup' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'OSActiveDirectoryInfoToStore' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'OSRequireActiveDirectoryBackup' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'OSAllowSecureBootForIntegrity' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'OSEncryptionType' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'FDVRecovery' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'FDVManageDRA' -Value '00000000' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'FDVRecoveryPassword' -Value '00000002' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'FDVRecoveryKey' -Value '00000002' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'FDVHideRecoveryPage' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'FDVActiveDirectoryBackup' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'FDVActiveDirectoryInfoToStore' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'FDVRequireActiveDirectoryBackup' -Value '00000001' -PropertyType DWORD
    New-ItemProperty -Path "$BitLockerRegLoc\FVE" -Name 'FDVEncryptionType' -Value '00000001' -PropertyType DWORD
}

# Passo 4 - Se todos os pré-requisitos forem atendidos, habilitar o BitLocker
if ($WindowsVer -and $TPMEnabled -and $BitLockerReadyDrive -and $BitLockerDecrypted) 
{
    $Protector = Add-BitLockerKeyProtector -MountPoint $env:SystemDrive -TpmProtector
    Enable-BitLocker -MountPoint $env:SystemDrive -RecoveryPasswordProtector -ErrorAction SilentlyContinue

    # Salvar a chave BitLocker e o identificador em um arquivo no disco C:
    $BitLockerVolume = Get-BitLockerVolume -MountPoint $env:SystemDrive
    $KeyProtector = $BitLockerVolume.KeyProtector | Where-Object {$_.KeyProtectorType -eq 'RecoveryPassword'}
    $RecoveryPassword = $KeyProtector.RecoveryPassword
    $KeyProtectorId = $KeyProtector.KeyProtectorId

    $OutputFile = "C:\BitLockerRecoveryInfo.txt"
    $OutputContent = @"
Recovery Password: $RecoveryPassword
Key Protector ID: $KeyProtectorId
"@
    $OutputContent | Out-File -FilePath $OutputFile -Encoding utf8
}

# Passo 5 - Backup das senhas de recuperação do BitLocker para o AD
if ($BLVS) 
{
    ForEach ($BLV in $BLVS) 
    {
        $Key = $BLV | Select-Object -ExpandProperty KeyProtector | Where-Object {$_.KeyProtectorType -eq 'RecoveryPassword'}
        ForEach ($obj in $key)
        { 
            Backup-BitLockerKeyProtector -MountPoint $BLV.MountPoint -KeyProtectorID $obj.KeyProtectorId
        }
    }
}
