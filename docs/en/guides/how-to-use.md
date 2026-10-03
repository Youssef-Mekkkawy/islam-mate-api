# How to Use the API

This guide shows you how to call Islam Mate API from every major platform and language.

---

## Base URL

```
http://your-server:8000
```

For local development:
```
http://localhost:8000
```

---

## Language Routing

All endpoints support Arabic and English via URL prefix:

```
# English response
GET /api/v1/en/prayer-times?latitude=30.04&longitude=31.23

# Arabic response
GET /api/v1/ar/prayer-times?latitude=30.04&longitude=31.23

# Default (English)
GET /api/v1/prayer-times?latitude=30.04&longitude=31.23

# Via query param
GET /api/v1/prayer-times?latitude=30.04&longitude=31.23&lang=ar
```

---

## Authentication

In **development mode** — no key needed.

In **production mode** — pass your API key in every request:

```
Header:    X-API-Key: im_your_key_here
           or
Header:    Authorization: Bearer im_your_key_here
           or
Param:     ?api_key=im_your_key_here
```

---

## Response Format

All responses are JSON:

```json
{
  "date": "2026-10-03",
  "prayers": [
    {"name": "Fajr", "time": "04:38"},
    {"name": "Dhuhr", "time": "11:51"},
    {"name": "Asr", "time": "15:14"},
    {"name": "Maghrib", "time": "17:40"},
    {"name": "Isha", "time": "19:02"}
  ]
}
```

---

## Error Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad request — check your parameters |
| 401 | API key required |
| 403 | Invalid API key |
| 404 | Resource not found |
| 422 | Validation error — wrong parameter type |
| 429 | Rate limit exceeded — wait 60 seconds |
| 500 | Server error |

---

## cURL

### Basic request

```bash
curl "http://localhost:8000/api/v1/prayer-times?latitude=30.04&longitude=31.23&timezone=Africa/Cairo"
```

### With API key

```bash
curl "http://localhost:8000/api/v1/prayer-times?latitude=30.04&longitude=31.23" \
  -H "X-API-Key: im_your_key_here"
```

### Arabic response

```bash
curl "http://localhost:8000/api/v1/ar/prayer-times?latitude=30.04&longitude=31.23"
```

### Pretty print JSON

```bash
curl "http://localhost:8000/api/v1/hadith/bukhari/1" | python3 -m json.tool
```

### Register for API key

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "My App", "email": "dev@example.com"}'
```

---

## Postman

### Download Collection

Download the ready-made Postman collection with all endpoints pre-configured:

[**Download Collection JSON**](https://raw.githubusercontent.com/Youssef-Mekkkawy/islam-mate-api/main/postman/islamic-api.postman_collection.json)

### Import Steps

1. Open Postman
2. Click **Import** (top left)
3. Select the downloaded JSON file
4. Click **Import**

### Set Up Environment

1. Click **Environments** → **Add**
2. Name it: `Islam Mate Local`
3. Add these variables:

| Variable | Value |
|---|---|
| `base_url` | `http://localhost:8000` |
| `api_key` | `im_your_key_here` |
| `lang` | `en` |

4. Click **Save**
5. Select the environment from the top-right dropdown

### Using the Collection

Every request in the collection uses `{{base_url}}` and `{{api_key}}` automatically. You only set them once in the environment.

---

## Python

### Install

```bash
pip install requests
```

### Prayer Times

```python
import requests

BASE_URL = "http://localhost:8000"
API_KEY = "im_your_key_here"

headers = {
    "X-API-Key": API_KEY
}

def get_prayer_times(latitude, longitude, timezone="UTC", lang="en"):
    response = requests.get(
        f"{BASE_URL}/api/v1/{lang}/prayer-times",
        headers=headers,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone
        }
    )
    response.raise_for_status()
    return response.json()


def get_random_hadith(collection="bukhari", lang="en"):
    response = requests.get(
        f"{BASE_URL}/api/v1/{lang}/hadith/random",
        headers=headers,
        params={"collection": collection}
    )
    response.raise_for_status()
    return response.json()


def get_allah_names(lang="en"):
    response = requests.get(
        f"{BASE_URL}/api/v1/{lang}/allah-names",
        headers=headers
    )
    response.raise_for_status()
    return response.json()


# Usage
if __name__ == "__main__":
    # Prayer times for Cairo
    times = get_prayer_times(30.04, 31.23, "Africa/Cairo", "en")
    for prayer in times["prayers"]:
        print(f"{prayer['name']}: {prayer['time']}")

    # Random hadith
    hadith = get_random_hadith("nawawi40")
    print(hadith["hadith"]["text"])

    # 99 Names
    names = get_allah_names("ar")
    print(names["names"][0]["arabic"])
```

### Error Handling

```python
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout

def safe_request(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except HTTPError as e:
        status = e.response.status_code
        if status == 401:
            print("Error: API key required")
        elif status == 429:
            print("Error: Rate limit exceeded. Wait 60 seconds.")
        elif status == 404:
            print("Error: Resource not found")
        else:
            print(f"HTTP Error: {status}")

    except ConnectionError:
        print("Error: Cannot connect to server")

    except Timeout:
        print("Error: Request timed out")

    return None
```

---

## JavaScript

### Browser (Fetch API)

```javascript
const BASE_URL = "http://localhost:8000";
const API_KEY = "im_your_key_here";

const headers = {
  "X-API-Key": API_KEY,
  "Content-Type": "application/json"
};

// Prayer times
async function getPrayerTimes(latitude, longitude, timezone = "UTC", lang = "en") {
  const params = new URLSearchParams({ latitude, longitude, timezone });
  const response = await fetch(
    `${BASE_URL}/api/v1/${lang}/prayer-times?${params}`,
    { headers }
  );

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json();
}

// Random hadith
async function getRandomHadith(collection = "bukhari", lang = "en") {
  const response = await fetch(
    `${BASE_URL}/api/v1/${lang}/hadith/random?collection=${collection}`,
    { headers }
  );
  return response.json();
}

// 99 Names of Allah
async function getAllahNames(lang = "en") {
  const response = await fetch(
    `${BASE_URL}/api/v1/${lang}/allah-names`,
    { headers }
  );
  return response.json();
}

// Usage
async function main() {
  try {
    const times = await getPrayerTimes(30.04, 31.23, "Africa/Cairo", "en");
    times.prayers.forEach(p => console.log(`${p.name}: ${p.time}`));

    const hadith = await getRandomHadith("nawawi40");
    console.log(hadith.hadith.text);

  } catch (error) {
    console.error("Error:", error.message);
  }
}

main();
```

### Node.js (Axios)

```bash
npm install axios
```

```javascript
const axios = require("axios");

const client = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "X-API-Key": "im_your_key_here" },
  timeout: 10000
});

// Prayer times
async function getPrayerTimes(lat, lng, timezone = "UTC", lang = "en") {
  const { data } = await client.get(`/api/v1/${lang}/prayer-times`, {
    params: { latitude: lat, longitude: lng, timezone }
  });
  return data;
}

// Azkar by category
async function getAzkar(categoryId, lang = "en") {
  const { data } = await client.get(`/api/v1/${lang}/azkar/${categoryId}`);
  return data;
}

// Error handling with axios
async function safeRequest(fn) {
  try {
    return await fn();
  } catch (error) {
    if (error.response) {
      const { status } = error.response;
      if (status === 429) console.error("Rate limit exceeded");
      else if (status === 401) console.error("API key required");
      else console.error(`Error: ${status}`);
    } else {
      console.error("Network error:", error.message);
    }
    return null;
  }
}

// Usage
(async () => {
  const times = await safeRequest(() =>
    getPrayerTimes(30.04, 31.23, "Africa/Cairo")
  );
  if (times) {
    times.prayers.forEach(p => console.log(`${p.name}: ${p.time}`));
  }
})();
```

---

## PHP

### cURL

```php
<?php

define('BASE_URL', 'http://localhost:8000');
define('API_KEY', 'im_your_key_here');

function islamRequest($endpoint, $params = [], $lang = 'en') {
    $url = BASE_URL . '/api/v1/' . $lang . $endpoint;

    if (!empty($params)) {
        $url .= '?' . http_build_query($params);
    }

    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_HTTPHEADER => [
            'X-API-Key: ' . API_KEY,
            'Accept: application/json'
        ]
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($httpCode !== 200) {
        throw new Exception("HTTP Error: $httpCode");
    }

    return json_decode($response, true);
}

// Prayer times
$times = islamRequest('/prayer-times', [
    'latitude' => 30.04,
    'longitude' => 31.23,
    'timezone' => 'Africa/Cairo'
], 'en');

foreach ($times['prayers'] as $prayer) {
    echo $prayer['name'] . ': ' . $prayer['time'] . PHP_EOL;
}

// Random hadith
$hadith = islamRequest('/hadith/random', ['collection' => 'bukhari']);
echo $hadith['hadith']['text'] . PHP_EOL;

// 99 Names
$names = islamRequest('/allah-names', [], 'ar');
echo $names['names'][0]['arabic'] . PHP_EOL;
```

### Guzzle

```bash
composer require guzzlehttp/guzzle
```

```php
<?php

require 'vendor/autoload.php';

use GuzzleHttp\Client;
use GuzzleHttp\Exception\RequestException;

class IslamMateClient {
    private Client $client;
    private string $lang;

    public function __construct(string $baseUrl, string $apiKey, string $lang = 'en') {
        $this->lang = $lang;
        $this->client = new Client([
            'base_uri' => $baseUrl,
            'timeout' => 10,
            'headers' => [
                'X-API-Key' => $apiKey,
                'Accept' => 'application/json'
            ]
        ]);
    }

    public function getPrayerTimes(float $lat, float $lng, string $timezone = 'UTC'): array {
        $response = $this->client->get("/api/v1/{$this->lang}/prayer-times", [
            'query' => [
                'latitude' => $lat,
                'longitude' => $lng,
                'timezone' => $timezone
            ]
        ]);
        return json_decode($response->getBody(), true);
    }

    public function getRandomHadith(string $collection = 'bukhari'): array {
        $response = $this->client->get("/api/v1/{$this->lang}/hadith/random", [
            'query' => ['collection' => $collection]
        ]);
        return json_decode($response->getBody(), true);
    }

    public function getAllahNames(): array {
        $response = $this->client->get("/api/v1/{$this->lang}/allah-names");
        return json_decode($response->getBody(), true);
    }
}

// Usage
try {
    $islam = new IslamMateClient('http://localhost:8000', 'im_your_key_here', 'en');

    $times = $islam->getPrayerTimes(30.04, 31.23, 'Africa/Cairo');
    foreach ($times['prayers'] as $prayer) {
        echo $prayer['name'] . ': ' . $prayer['time'] . PHP_EOL;
    }

    $hadith = $islam->getRandomHadith('nawawi40');
    echo $hadith['hadith']['text'] . PHP_EOL;

} catch (RequestException $e) {
    echo "Error: " . $e->getMessage() . PHP_EOL;
}
```

---

## Android — Kotlin

### Add Dependencies

In `build.gradle (app)`:

```gradle
dependencies {
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.12.0'
}
```

Don't forget internet permission in `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET"/>
```

### Data Models

```kotlin
// Prayer.kt
data class Prayer(
    val name: String,
    val time: String
)

// PrayerTimesResponse.kt
data class PrayerTimesResponse(
    val date: String,
    val prayers: List<Prayer>,
    val sunrise: String,
    val method: String,
    val timezone: String
)

// Hadith.kt
data class HadithText(
    val en: String,
    val ar: String
)

data class HadithItem(
    val number: Int,
    val grade: String,
    val text: HadithText
)

data class HadithResponse(
    val collection: String,
    val hadith: HadithItem
)

// AllahName.kt
data class AllahName(
    val number: Int,
    val arabic: String,
    val transliteration: String,
    val name: String,
    val meaning: String
)

data class AllahNamesResponse(
    val total: Int,
    val names: List<AllahName>
)
```

### API Interface

```kotlin
// IslamMateApi.kt
import retrofit2.Response
import retrofit2.http.*

interface IslamMateApi {

    @GET("api/v1/{lang}/prayer-times")
    suspend fun getPrayerTimes(
        @Path("lang") lang: String = "en",
        @Query("latitude") latitude: Double,
        @Query("longitude") longitude: Double,
        @Query("timezone") timezone: String = "UTC",
        @Query("method") method: String = "EGYPT"
    ): Response<PrayerTimesResponse>

    @GET("api/v1/{lang}/prayer/next")
    suspend fun getNextPrayer(
        @Path("lang") lang: String = "en",
        @Query("latitude") latitude: Double,
        @Query("longitude") longitude: Double,
        @Query("timezone") timezone: String = "UTC"
    ): Response<Map<String, String>>

    @GET("api/v1/{lang}/hadith/random")
    suspend fun getRandomHadith(
        @Path("lang") lang: String = "en",
        @Query("collection") collection: String = "bukhari"
    ): Response<HadithResponse>

    @GET("api/v1/{lang}/allah-names")
    suspend fun getAllahNames(
        @Path("lang") lang: String = "en"
    ): Response<AllahNamesResponse>

    @GET("api/v1/{lang}/azkar/{categoryId}")
    suspend fun getAzkar(
        @Path("lang") lang: String = "en",
        @Path("categoryId") categoryId: Int
    ): Response<Map<String, Any>>
}
```

### Retrofit Client

```kotlin
// IslamMateClient.kt
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object IslamMateClient {

    private const val BASE_URL = "http://10.0.2.2:8000/"  // localhost for emulator
    private const val API_KEY = "im_your_key_here"

    private val authInterceptor = Interceptor { chain ->
        val request = chain.request().newBuilder()
            .addHeader("X-API-Key", API_KEY)
            .build()
        chain.proceed(request)
    }

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .addInterceptor(loggingInterceptor)
        .build()

    val api: IslamMateApi = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(IslamMateApi::class.java)
}
```

### Usage in ViewModel

```kotlin
// PrayerViewModel.kt
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class PrayerViewModel : ViewModel() {

    private val _prayerTimes = MutableStateFlow<PrayerTimesResponse?>(null)
    val prayerTimes: StateFlow<PrayerTimesResponse?> = _prayerTimes

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error

    fun loadPrayerTimes(lat: Double, lng: Double, timezone: String) {
        viewModelScope.launch {
            try {
                val response = IslamMateClient.api.getPrayerTimes(
                    lang = "en",
                    latitude = lat,
                    longitude = lng,
                    timezone = timezone
                )

                if (response.isSuccessful) {
                    _prayerTimes.value = response.body()
                } else {
                    when (response.code()) {
                        429 -> _error.value = "Rate limit exceeded. Try again in 60 seconds."
                        401 -> _error.value = "API key required."
                        else -> _error.value = "Error: ${response.code()}"
                    }
                }
            } catch (e: Exception) {
                _error.value = "Network error: ${e.message}"
            }
        }
    }
}
```

---

## Flutter / Dart

### Add Dependencies

In `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0
  dio: ^5.4.0
```

Run:
```bash
flutter pub get
```

### Using http package

```dart
// islam_mate_client.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class IslamMateClient {
  final String baseUrl;
  final String apiKey;
  final String lang;

  IslamMateClient({
    this.baseUrl = 'http://localhost:8000',
    required this.apiKey,
    this.lang = 'en',
  });

  Map<String, String> get _headers => {
    'X-API-Key': apiKey,
    'Content-Type': 'application/json',
  };

  Future<Map<String, dynamic>> _get(String path, {Map<String, String>? params}) async {
    final uri = Uri.parse('$baseUrl$path').replace(queryParameters: params);
    final response = await http.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else if (response.statusCode == 429) {
      throw Exception('Rate limit exceeded. Wait 60 seconds.');
    } else if (response.statusCode == 401) {
      throw Exception('API key required.');
    } else {
      throw Exception('HTTP Error: ${response.statusCode}');
    }
  }

  // Prayer Times
  Future<Map<String, dynamic>> getPrayerTimes({
    required double latitude,
    required double longitude,
    String timezone = 'UTC',
    String method = 'EGYPT',
  }) async {
    return _get('/api/v1/$lang/prayer-times', params: {
      'latitude': latitude.toString(),
      'longitude': longitude.toString(),
      'timezone': timezone,
      'method': method,
    });
  }

  // Next Prayer
  Future<Map<String, dynamic>> getNextPrayer({
    required double latitude,
    required double longitude,
    String timezone = 'UTC',
  }) async {
    return _get('/api/v1/$lang/prayer/next', params: {
      'latitude': latitude.toString(),
      'longitude': longitude.toString(),
      'timezone': timezone,
    });
  }

  // Random Hadith
  Future<Map<String, dynamic>> getRandomHadith({
    String collection = 'bukhari',
  }) async {
    return _get('/api/v1/$lang/hadith/random', params: {
      'collection': collection,
    });
  }

  // 99 Names of Allah
  Future<Map<String, dynamic>> getAllahNames() async {
    return _get('/api/v1/$lang/allah-names');
  }

  // Azkar by category
  Future<Map<String, dynamic>> getAzkar(int categoryId) async {
    return _get('/api/v1/$lang/azkar/$categoryId');
  }

  // Random Azkar
  Future<Map<String, dynamic>> getRandomAzkar() async {
    return _get('/api/v1/$lang/azkar/random/item');
  }

  // Hijri date
  Future<Map<String, dynamic>> getHijriDate() async {
    return _get('/api/v1/$lang/hijri');
  }
}
```

### Usage in Flutter Widget

```dart
// main.dart
import 'package:flutter/material.dart';
import 'islam_mate_client.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(home: PrayerTimesScreen());
  }
}

class PrayerTimesScreen extends StatefulWidget {
  const PrayerTimesScreen({super.key});

  @override
  State<PrayerTimesScreen> createState() => _PrayerTimesScreenState();
}

class _PrayerTimesScreenState extends State<PrayerTimesScreen> {
  final client = IslamMateClient(
    baseUrl: 'http://localhost:8000',
    apiKey: 'im_your_key_here',
    lang: 'en',
  );

  Map<String, dynamic>? _data;
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadPrayerTimes();
  }

  Future<void> _loadPrayerTimes() async {
    try {
      final data = await client.getPrayerTimes(
        latitude: 30.04,
        longitude: 31.23,
        timezone: 'Africa/Cairo',
      );
      setState(() {
        _data = data;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (_error != null) return Scaffold(body: Center(child: Text(_error!)));

    final prayers = List<Map<String, dynamic>>.from(_data!['prayers']);

    return Scaffold(
      appBar: AppBar(title: Text('Prayer Times — ${_data!['date']}')),
      body: ListView.builder(
        itemCount: prayers.length,
        itemBuilder: (context, index) {
          final prayer = prayers[index];
          return ListTile(
            title: Text(prayer['name']),
            trailing: Text(prayer['time']),
          );
        },
      ),
    );
  }
}
```

### Using Dio (Advanced)

```dart
// islam_mate_dio.dart
import 'package:dio/dio.dart';

class IslamMateDio {
  late final Dio _dio;
  final String lang;

  IslamMateDio({
    String baseUrl = 'http://localhost:8000',
    required String apiKey,
    this.lang = 'en',
  }) {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {'X-API-Key': apiKey},
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onError: (DioException e, handler) {
        if (e.response?.statusCode == 429) {
          throw Exception('Rate limit exceeded. Wait 60 seconds.');
        } else if (e.response?.statusCode == 401) {
          throw Exception('API key required.');
        }
        handler.next(e);
      },
    ));
  }

  Future<Map<String, dynamic>> getPrayerTimes({
    required double latitude,
    required double longitude,
    String timezone = 'UTC',
  }) async {
    final response = await _dio.get(
      '/api/v1/$lang/prayer-times',
      queryParameters: {
        'latitude': latitude,
        'longitude': longitude,
        'timezone': timezone,
      },
    );
    return response.data;
  }

  Future<Map<String, dynamic>> getRandomHadith({String collection = 'bukhari'}) async {
    final response = await _dio.get(
      '/api/v1/$lang/hadith/random',
      queryParameters: {'collection': collection},
    );
    return response.data;
  }
}
```

---

## Tips

### Always Use Timezone

```
# Wrong — returns UTC times
GET /api/v1/prayer-times?latitude=30.04&longitude=31.23

# Correct — returns local times
GET /api/v1/prayer-times?latitude=30.04&longitude=31.23&timezone=Africa/Cairo
```

### Common Timezones

| Country | Timezone |
|---|---|
| Egypt | Africa/Cairo |
| Saudi Arabia | Asia/Riyadh |
| UAE | Asia/Dubai |
| Pakistan | Asia/Karachi |
| Indonesia | Asia/Jakarta |
| UK | Europe/London |
| USA Eastern | America/New_York |

### Rate Limiting

If you get **429**, wait 60 seconds before retrying. In production, cache responses locally — prayer times don't change within a day.
