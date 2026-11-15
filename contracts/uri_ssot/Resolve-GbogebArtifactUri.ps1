#Requires -Version 7.2
<#
.SYNOPSIS
    URI SSOT resolver (gbogeb.uri-ssot/1): RFC 3986 parse + section 6 normalization.
.DESCRIPTION
    PowerShell port of contracts/uri_ssot/resolver.py. Both implementations are
    checked against the same hand-written vectors in vectors.json.

    DOV-1  $null, empty or whitespace-only input returns $null.
    DOV-2  An empty authority (file:///C:/x -> '') is distinct from an absent
           one (urn:a:b -> $null); HasAuthority records which.
    DOV-3  'foo:bar/baz' is an absolute URI with scheme 'foo' (RFC 3986 3.1).
           The './' prefix belongs to *writing* a relative reference whose first
           segment contains a colon (RFC 3986 4.2): ConvertTo-GbogebRelativeReference.

    Windows drive and UNC paths are file-system paths, converted to file: URIs
    per RFC 8089 appendix E. javascript:, vbscript: and data: URIs are kept as
    parsed and flagged ExecutableScheme. A '#oid:<dotted>' fragment yields
    FragmentOid; no OID is ever invented.
#>
Set-StrictMode -Version Latest

$script:GbogebUriSchemaVersion = 'gbogeb.uri-ssot/1'
$script:GbogebExecutableSchemes = @('javascript', 'vbscript', 'data')
$script:GbogebUriRegex = [regex]::new(
    '^(?:(?<scheme>[A-Za-z][A-Za-z0-9+.\-]*):)?(?://(?<authority>[^/?#]*))?(?<path>[^?#]*)(?:\?(?<query>[^#]*))?(?:#(?<fragment>.*))?$',
    [System.Text.RegularExpressions.RegexOptions]::Singleline)
$script:GbogebDriveRegex = [regex]::new('^[A-Za-z]:[\\/]')
$script:GbogebUncRegex = [regex]::new('^\\\\[^\\/]+[\\/]')
$script:GbogebPctRegex = [regex]::new('%[0-9A-Fa-f]{2}')
$script:GbogebOidRegex = [regex]::new('^oid:(?<oid>[0-2](?:\.(?:0|[1-9][0-9]*))+)$')

function Remove-GbogebDotSegment {
    <# RFC 3986 section 5.2.4. #>
    [CmdletBinding()]
    [OutputType([string])]
    param([Parameter(Mandatory)] [AllowEmptyString()] [string]$Path)
    $out = [System.Collections.Generic.List[string]]::new()
    while ($Path.Length -gt 0) {
        if ($Path.StartsWith('../')) { $Path = $Path.Substring(3) }
        elseif ($Path.StartsWith('./')) { $Path = $Path.Substring(2) }
        elseif ($Path.StartsWith('/./')) { $Path = $Path.Substring(2) }
        elseif ($Path -ceq '/.') { $Path = '/' }
        elseif ($Path.StartsWith('/../')) {
            $Path = $Path.Substring(3)
            if ($out.Count -gt 0) { $out.RemoveAt($out.Count - 1) }
        }
        elseif ($Path -ceq '/..') {
            $Path = '/'
            if ($out.Count -gt 0) { $out.RemoveAt($out.Count - 1) }
        }
        elseif ($Path -ceq '.' -or $Path -ceq '..') { $Path = '' }
        else {
            $start = if ($Path.StartsWith('/')) { 1 } else { 0 }
            $cut = $Path.IndexOf('/', $start)
            if ($cut -eq -1) { $out.Add($Path); $Path = '' }
            else { $out.Add($Path.Substring(0, $cut)); $Path = $Path.Substring($cut) }
        }
    }
    return ($out -join '')
}

function ConvertTo-GbogebUpperPct {
    param([AllowNull()] [string]$Text)
    if ($null -eq $Text) { return $null }
    return $script:GbogebPctRegex.Replace($Text, { param($m) $m.Value.ToUpperInvariant() })
}

function ConvertTo-GbogebNormalizedAuthority {
    <# Lower-case the host only; userinfo and port are left as given. #>
    param([Parameter(Mandatory)] [AllowEmptyString()] [string]$Authority)
    $at = $Authority.LastIndexOf('@')
    $userinfo = if ($at -ge 0) { $Authority.Substring(0, $at + 1) } else { '' }
    $hostport = if ($at -ge 0) { $Authority.Substring($at + 1) } else { $Authority }
    if ($hostport.StartsWith('[')) {
        $end = $hostport.IndexOf(']')
        if ($end -ge 0) { $hostPart = $hostport.Substring(0, $end + 1); $rest = $hostport.Substring($end + 1) }
        else { $hostPart = $hostport; $rest = '' }
    }
    else {
        $colon = $hostport.IndexOf(':')
        if ($colon -ge 0) { $hostPart = $hostport.Substring(0, $colon); $rest = $hostport.Substring($colon) }
        else { $hostPart = $hostport; $rest = '' }
    }
    return $userinfo + (ConvertTo-GbogebUpperPct $hostPart.ToLowerInvariant()) + $rest
}

function ConvertTo-GbogebRelativeReference {
    <# Write a path as a relative reference (RFC 3986 4.2): 'foo:bar/baz' -> './foo:bar/baz'. #>
    [CmdletBinding()]
    [OutputType([string])]
    param([Parameter(Mandatory, Position = 0)] [AllowNull()] [AllowEmptyString()] [string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { throw [System.ArgumentException]::new('path must be a non-empty string') }
    $first = $Path.Split('/', 2)[0]
    if ($first.Contains(':')) { return './' + $Path }
    return $Path
}

function Resolve-GbogebArtifactUri {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Position = 0, ValueFromPipeline)]
        [AllowNull()] [AllowEmptyString()]
        [string]$InputUri
    )
    process {
        if ([string]::IsNullOrWhiteSpace($InputUri)) { return $null }  # DOV-1
        $original = $InputUri
        $trimmed = $InputUri.Trim()
        $kind = 'uri'
        if ($script:GbogebDriveRegex.IsMatch($trimmed)) {
            $kind = 'windows_drive_path'; $trimmed = 'file:///' + $trimmed.Replace('\', '/')
        }
        elseif ($script:GbogebUncRegex.IsMatch($trimmed)) {
            $kind = 'unc_path'; $trimmed = 'file:' + $trimmed.Replace('\', '/')
        }

        $m = $script:GbogebUriRegex.Match($trimmed)
        if (-not $m.Success) { throw "unparseable reference: '$original'" }
        $g = $m.Groups
        $scheme = if ($g['scheme'].Success) { $g['scheme'].Value } else { $null }
        $authority = if ($g['authority'].Success) { $g['authority'].Value } else { $null }
        $path = $g['path'].Value
        $query = if ($g['query'].Success) { $g['query'].Value } else { $null }
        $fragment = if ($g['fragment'].Success) { $g['fragment'].Value } else { $null }

        $isAbsolute = $null -ne $scheme
        if ($kind -eq 'uri') { $kind = if ($isAbsolute) { 'absolute_uri' } else { 'relative_reference' } }
        $schemeN = if ($isAbsolute) { $scheme.ToLowerInvariant() } else { $null }
        $authorityN = if ($null -ne $authority) { ConvertTo-GbogebNormalizedAuthority $authority } else { $null }
        $pathN = ConvertTo-GbogebUpperPct $path
        if ($isAbsolute -or $null -ne $authority) { $pathN = Remove-GbogebDotSegment $pathN }
        $queryN = ConvertTo-GbogebUpperPct $query
        $fragmentN = ConvertTo-GbogebUpperPct $fragment

        $canonical = ''
        if ($null -ne $schemeN) { $canonical += $schemeN + ':' }
        if ($null -ne $authorityN) { $canonical += '//' + $authorityN }
        $canonical += $pathN
        if ($null -ne $queryN) { $canonical += '?' + $queryN }
        if ($null -ne $fragmentN) { $canonical += '#' + $fragmentN }

        $oid = $null
        if ($null -ne $fragment) {
            $om = $script:GbogebOidRegex.Match($fragment)
            if ($om.Success) { $oid = $om.Groups['oid'].Value }
        }

        [pscustomobject][ordered]@{
            PSTypeName       = 'Gbogeb.Uri.SsotContract'
            SchemaVersion    = $script:GbogebUriSchemaVersion
            Original         = $original
            Kind             = $kind
            IsAbsolute       = $isAbsolute
            Scheme           = $schemeN
            HasAuthority     = $null -ne $authority
            Authority        = $authorityN
            Path             = $pathN
            Query            = $queryN
            Fragment         = $fragmentN
            FragmentOid      = $oid
            ExecutableScheme = $schemeN -in $script:GbogebExecutableSchemes
            Canonical        = $canonical
        }
    }
}
