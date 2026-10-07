# ============================================================
#  Islam Mate API -- Full Endpoint Test Suite
#  Run: .\test_api.ps1
#  Server must be running at http://localhost:8000
# ============================================================

$BASE = "http://localhost:8000"
$PASS = 0
$FAIL = 0

function Test-Endpoint {
    param(
        [string]$Label,
        [string]$Url,
        [int]$ExpectStatus = 200,
        [string[]]$ExpectKeys = @(),
        [hashtable]$ExpectValues = @{}
    )

    try {
        $resp   = Invoke-WebRequest -Uri $Url -UseBasicParsing -ErrorAction Stop
        $status = $resp.StatusCode
        try { $body = $resp.Content | ConvertFrom-Json } catch { $body = $null }

        $ok = ($status -eq $ExpectStatus)

        $missingKeys = @()
        foreach ($key in $ExpectKeys) {
            $parts = $key -split "\."
            $node  = $body
            foreach ($p in $parts) {
                if ($node -and ($node | Get-Member -Name $p -ErrorAction SilentlyContinue)) {
                    $node = $node.$p
                } else {
                    $missingKeys += $key
                    $node = $null
                    break
                }
            }
        }

        $wrongValues = @()
        foreach ($kv in $ExpectValues.GetEnumerator()) {
            $parts = $kv.Key -split "\."
            $node  = $body
            foreach ($p in $parts) {
                if ($node -and ($node | Get-Member -Name $p -ErrorAction SilentlyContinue)) {
                    $node = $node.$p
                } else { $node = $null; break }
            }
            if ("$node" -ne "$($kv.Value)") {
                $wrongValues += "$($kv.Key)=$node (want $($kv.Value))"
            }
        }

        if ($ok -and $missingKeys.Count -eq 0 -and $wrongValues.Count -eq 0) {
            Write-Host "  [PASS] $Label" -ForegroundColor Green
            $script:PASS++
        } else {
            Write-Host "  [FAIL] $Label" -ForegroundColor Red
            if ($status -ne $ExpectStatus) {
                Write-Host "         Status: $status (want $ExpectStatus)" -ForegroundColor Yellow
            }
            foreach ($mk in $missingKeys) {
                Write-Host "         Missing key: $mk" -ForegroundColor Yellow
            }
            foreach ($wv in $wrongValues) {
                Write-Host "         Wrong value: $wv" -ForegroundColor Yellow
            }
            $script:FAIL++
        }
    }
    catch {
        $errStatus = $_.Exception.Response.StatusCode.value__
        if ($errStatus -and $errStatus -eq $ExpectStatus) {
            Write-Host "  [PASS] $Label (expected $ExpectStatus)" -ForegroundColor Green
            $script:PASS++
        } else {
            Write-Host "  [FAIL] $Label -- $($_.Exception.Message)" -ForegroundColor Red
            $script:FAIL++
        }
    }
}

function Test-Filter {
    param(
        [string]$Label,
        [string]$FilteredUrl,
        [string]$FullUrl,
        [string]$CountField = "total"
    )
    try {
        $full     = (Invoke-WebRequest -Uri $FullUrl     -UseBasicParsing).Content | ConvertFrom-Json
        $filtered = (Invoke-WebRequest -Uri $FilteredUrl -UseBasicParsing).Content | ConvertFrom-Json
        $fullCnt  = $full.$CountField
        $filtCnt  = $filtered.$CountField
        if ($null -ne $filtCnt -and $filtCnt -lt $fullCnt) {
            Write-Host "  [PASS] $Label  ($fullCnt -> $filtCnt)" -ForegroundColor Green
            $script:PASS++
        } else {
            Write-Host "  [FAIL] $Label  (filter did nothing: $fullCnt -> $filtCnt)" -ForegroundColor Red
            $script:FAIL++
        }
    } catch {
        Write-Host "  [FAIL] $Label -- $($_.Exception.Message)" -ForegroundColor Red
        $script:FAIL++
    }
}

function Section { param([string]$Title)
    Write-Host ""
    Write-Host "-- $Title" -ForegroundColor Cyan
}

# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor White
Write-Host "  Islam Mate API -- Test Suite" -ForegroundColor White
Write-Host "  $BASE" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor White


# -- 1. Core -------------------------------------------------
Section "1. Core"
Test-Endpoint "GET /"            "$BASE/"             -ExpectKeys @("name","version","status")
Test-Endpoint "GET /health"      "$BASE/health"       -ExpectValues @{"status"="ok"}
Test-Endpoint "GET /docs"        "$BASE/docs"
Test-Endpoint "GET /openapi.json" "$BASE/openapi.json" -ExpectKeys @("info","paths")


# -- 2. Prayer Times -----------------------------------------
Section "2. Prayer Times"
$LAT = "30.0444"
$LNG = "31.2357"

Test-Endpoint "GET /prayer-times (Cairo, EGYPT)" `
    "$BASE/api/v1/prayer-times?latitude=$LAT&longitude=$LNG&method=EGYPT" `
    -ExpectKeys @("prayers","date","sunrise")

Test-Endpoint "GET /prayer-times -- Arabic path" `
    "$BASE/api/v1/ar/prayer-times?latitude=$LAT&longitude=$LNG" `
    -ExpectKeys @("prayers")

Test-Endpoint "GET /prayer/next" `
    "$BASE/api/v1/prayer/next?latitude=$LAT&longitude=$LNG" `
    -ExpectKeys @("next_prayer","time","in_minutes")

Test-Endpoint "GET /prayer/month" `
    "$BASE/api/v1/prayer/month?latitude=$LAT&longitude=$LNG&month=10&year=2026" `
    -ExpectKeys @("days")

Test-Endpoint "GET /prayer/methods" `
    "$BASE/api/v1/prayer/methods" `
    -ExpectKeys @("methods")

Test-Endpoint "GET /prayer-times/auto (IP)" `
    "$BASE/api/v1/prayer-times/auto" `
    -ExpectKeys @("prayers")


# -- 3. Hijri Calendar ---------------------------------------
Section "3. Hijri Calendar"

Test-Endpoint "GET /hijri/today" `
    "$BASE/api/v1/hijri/today" `
    -ExpectKeys @("gregorian","hijri","day_name")

Test-Endpoint "GET /hijri/today -- Arabic" `
    "$BASE/api/v1/ar/hijri/today" `
    -ExpectKeys @("gregorian","hijri")

Test-Endpoint "GET /hijri/convert (2026-10-07)" `
    "$BASE/api/v1/hijri/convert?date=2026-10-07" `
    -ExpectKeys @("gregorian","hijri")

Test-Endpoint "GET /hijri/events (year=2026, all)" `
    "$BASE/api/v1/hijri/events?year=2026" `
    -ExpectKeys @("events","total")

Test-Filter `
    "GET /hijri/events -- event_type=holidays filter" `
    "$BASE/api/v1/hijri/events?year=2026&event_type=holidays" `
    "$BASE/api/v1/hijri/events?year=2026"

Test-Filter `
    "GET /hijri/events -- include_weekly=false filter" `
    "$BASE/api/v1/hijri/events?year=2026&include_weekly=false" `
    "$BASE/api/v1/hijri/events?year=2026"

try {
    $en = (Invoke-WebRequest -Uri "$BASE/api/v1/hijri/events?year=2026" -UseBasicParsing).Content | ConvertFrom-Json
    $ar = (Invoke-WebRequest -Uri "$BASE/api/v1/ar/hijri/events?year=2026" -UseBasicParsing).Content | ConvertFrom-Json
    if ($en.events[0].name -ne $ar.events[0].name) {
        Write-Host "  [PASS] GET /ar/hijri/events -- Arabic names applied" -ForegroundColor Green
        $script:PASS++
    } else {
        Write-Host "  [FAIL] GET /ar/hijri/events -- lang not applied (same as EN)" -ForegroundColor Red
        Write-Host "         EN: $($en.events[0].name)" -ForegroundColor Yellow
        Write-Host "         AR: $($ar.events[0].name)" -ForegroundColor Yellow
        $script:FAIL++
    }
} catch {
    Write-Host "  [FAIL] Arabic hijri events -- $($_.Exception.Message)" -ForegroundColor Red
    $script:FAIL++
}


# -- 4. Location ---------------------------------------------
Section "4. Location"

Test-Endpoint "GET /location/detect" `
    "$BASE/api/v1/location/detect" `
    -ExpectKeys @("city","country","latitude","longitude")

Test-Endpoint "GET /location/search?q=Cairo" `
    "$BASE/api/v1/location/search?q=Cairo" `
    -ExpectKeys @("results")

Test-Endpoint "GET /location/search?q=Mecca" `
    "$BASE/api/v1/location/search?q=Mecca" `
    -ExpectKeys @("results")

Test-Endpoint "GET /location/auto" `
    "$BASE/api/v1/location/auto" `
    -ExpectKeys @("city","latitude","longitude","method")

Test-Endpoint "GET /location/config" `
    "$BASE/api/v1/location/config" `
    -ExpectKeys @("methods","platforms")


# -- 5. Zakat ------------------------------------------------
Section "5. Zakat Calculator"

Test-Endpoint "GET /zakat/nisab" `
    "$BASE/api/v1/zakat/nisab" `
    -ExpectKeys @("gold","silver","recommendation")

Test-Endpoint "GET /zakat/calculate -- no assets (no zakat due)" `
    "$BASE/api/v1/zakat/calculate" `
    -ExpectValues @{"zakat_due"="False"}

Test-Endpoint "GET /zakat/calculate -- 100g gold above nisab" `
    "$BASE/api/v1/zakat/calculate?gold_grams=100&gold_price_per_gram=90" `
    -ExpectValues @{"zakat_due"="True"}

Test-Endpoint "GET /zakat/calculate -- breakdown keys present" `
    "$BASE/api/v1/zakat/calculate?cash=50000&gold_price_per_gram=90&silver_price_per_gram=0.9" `
    -ExpectKeys @("monetary","nisab","livestock","summary")

Test-Endpoint "GET /zakat/calculate -- 40 sheep (zakat due)" `
    "$BASE/api/v1/zakat/calculate?sheep=40" `
    -ExpectValues @{"zakat_due"="True"}

Test-Endpoint "GET /zakat/calculate -- 3 sheep (no zakat)" `
    "$BASE/api/v1/zakat/calculate?sheep=3" `
    -ExpectValues @{"zakat_due"="False"}

Test-Endpoint "GET /zakat/calculate -- Arabic path" `
    "$BASE/api/v1/ar/zakat/calculate?gold_grams=100&gold_price_per_gram=90" `
    -ExpectKeys @("zakat_due","monetary","nisab")

Test-Endpoint "GET /zakat/calculate -- gold nisab standard" `
    "$BASE/api/v1/zakat/calculate?gold_grams=90&gold_price_per_gram=90&nisab_standard=gold" `
    -ExpectKeys @("zakat_due","nisab")

Test-Endpoint "GET /zakat/calculate -- camels (10 camels, zakat due)" `
    "$BASE/api/v1/zakat/calculate?camels=10" `
    -ExpectValues @{"zakat_due"="True"}


# -- 6. Docs -------------------------------------------------
Section "6. API Docs"
Test-Endpoint "Swagger UI"  "$BASE/docs"   -ExpectStatus 200
Test-Endpoint "ReDoc"       "$BASE/redoc"  -ExpectStatus 200


# ============================================================
$TOTAL = $PASS + $FAIL
Write-Host ""
Write-Host "============================================================" -ForegroundColor White
$color = if ($FAIL -eq 0) { "Green" } else { "Yellow" }
Write-Host "  Results: $PASS / $TOTAL passed" -ForegroundColor $color
if ($FAIL -gt 0) {
    Write-Host "  $FAIL test(s) FAILED -- fix before pushing to dev" -ForegroundColor Red
} else {
    Write-Host "  All tests passed -- safe to push to dev" -ForegroundColor Green
}
Write-Host "============================================================" -ForegroundColor White
Write-Host ""