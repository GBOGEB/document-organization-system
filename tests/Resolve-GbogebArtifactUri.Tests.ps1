#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'Pester'; ModuleVersion = '5.0.0' }
<#
    Pester 5 gate for contracts/uri_ssot/Resolve-GbogebArtifactUri.ps1.
    Uses the same hand-written vectors as tests/test_uri_ssot.py, so the
    PowerShell port and the Python reference must agree field for field.
#>

BeforeDiscovery {
    $root = Split-Path -Parent $PSScriptRoot
    $script:Vectors = Get-Content -Raw -Path (Join-Path $root 'contracts/uri_ssot/vectors.json') | ConvertFrom-Json -AsHashtable
    $script:ResolveCases = @($script:Vectors['resolve'] | ForEach-Object { @{ Case = $_ } })
    $script:RelativeCases = @($script:Vectors['to_relative_reference'] | ForEach-Object { @{ Case = $_ } })
}

BeforeAll {
    $root = Split-Path -Parent $PSScriptRoot
    . (Join-Path $root 'contracts/uri_ssot/Resolve-GbogebArtifactUri.ps1')
    # Discovery-time variables are not visible at run time in Pester 5; reload.
    $script:RunVectors = Get-Content -Raw -Path (Join-Path $root 'contracts/uri_ssot/vectors.json') | ConvertFrom-Json -AsHashtable
    # snake_case vector keys -> PascalCase contract properties
    $script:KeyMap = @{
        schema_version = 'SchemaVersion'; original = 'Original'; kind = 'Kind'; is_absolute = 'IsAbsolute'
        scheme = 'Scheme'; has_authority = 'HasAuthority'; authority = 'Authority'; path = 'Path'
        query = 'Query'; fragment = 'Fragment'; fragment_oid = 'FragmentOid'
        executable_scheme = 'ExecutableScheme'; canonical = 'Canonical'
    }
}

Describe 'gbogeb.uri-ssot/1 vectors' {
    It 'has a non-empty vector set (a gate that checks nothing must not pass)' {
        @($script:RunVectors['resolve']).Count | Should -BeGreaterOrEqual 20
        @($script:RunVectors['to_relative_reference']).Count | Should -BeGreaterOrEqual 3
    }

    It 'resolves <Case.id>' -ForEach $script:ResolveCases {
        $got = Resolve-GbogebArtifactUri -InputUri $Case['input']
        if ($Case.ContainsKey('expect_null') -and $Case['expect_null']) {
            $got | Should -BeNullOrEmpty
            return
        }
        $got | Should -Not -BeNullOrEmpty
        foreach ($key in $Case['expect'].Keys) {
            $want = $Case['expect'][$key]
            $actual = $got.($script:KeyMap[$key])
            if ($null -eq $want) {
                $actual | Should -BeNullOrEmpty -Because "$key must be null"
                ($null -eq $actual) | Should -BeTrue -Because "$key must be null, not empty"
            }
            else {
                $actual | Should -BeExactly $want -Because $key
            }
        }
    }

    It 'writes relative reference <Case.id>' -ForEach $script:RelativeCases {
        ConvertTo-GbogebRelativeReference $Case['input'] | Should -BeExactly $Case['expect']
    }
}

Describe 'contract invariants' {
    It 'keeps HasAuthority consistent with Authority and IsAbsolute with Scheme' -ForEach $script:ResolveCases {
        $got = Resolve-GbogebArtifactUri -InputUri $Case['input']
        if ($null -ne $got) {
            $got.HasAuthority | Should -Be ($null -ne $got.Authority)
            $got.IsAbsolute | Should -Be ($null -ne $got.Scheme)
            (Resolve-GbogebArtifactUri -InputUri $got.Canonical).Canonical | Should -BeExactly $got.Canonical
        }
    }

    It 'round-trips a written colon path as a relative reference' {
        $r = Resolve-GbogebArtifactUri -InputUri (ConvertTo-GbogebRelativeReference 'foo:bar/baz')
        $r.Kind | Should -BeExactly 'relative_reference'
        $r.Path | Should -BeExactly './foo:bar/baz'
    }

    It 'rejects a blank path when writing a relative reference' {
        { ConvertTo-GbogebRelativeReference '  ' } | Should -Throw
    }
}
