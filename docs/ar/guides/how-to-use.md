# كيفية استخدام الـ API

دليل شامل لاستخدام Islam Mate API من مختلف المنصات واللغات.

---

## الرابط الاساسي

```
http://your-server:8000
```

للتطوير المحلي:
```
http://localhost:8000
```

---

## دعم اللغات

جميع نقاط النهاية تدعم العربية والانجليزية:

```bash
# عربي
curl "http://localhost:8000/api/v1/ar/prayer-times?latitude=30.04&longitude=31.23"

# انجليزي
curl "http://localhost:8000/api/v1/en/prayer-times?latitude=30.04&longitude=31.23"

# عبر معامل الاستعلام
curl "http://localhost:8000/api/v1/prayer-times?latitude=30.04&longitude=31.23&lang=ar"
```

---

## المصادقة

في **وضع التطوير** — لا يلزم مفتاح.

في **وضع الانتاج** — ارسل مفتاح API في كل طلب:

```
Header:  X-API-Key: im_your_key_here
او
Header:  Authorization: Bearer im_your_key_here
او
Param:   ?api_key=im_your_key_here
```

---

## رموز الاستجابة

| الرمز | المعنى |
|---|---|
| 200 | ناجح |
| 400 | طلب خاطئ |
| 401 | مفتاح API مطلوب |
| 403 | مفتاح API غير صالح |
| 404 | غير موجود |
| 429 | تجاوزت الحد المسموح |

---

## cURL

```bash
# طلب اساسي
curl "http://localhost:8000/api/v1/ar/prayer-times?latitude=30.04&longitude=31.23&timezone=Africa/Cairo"

# مع مفتاح API
curl "http://localhost:8000/api/v1/ar/prayer-times?latitude=30.04&longitude=31.23" \
  -H "X-API-Key: im_your_key_here"

# طباعة منسقة
curl "http://localhost:8000/api/v1/ar/hadith/bukhari/1" | python3 -m json.tool
```

---

## Python

```python
import requests

BASE_URL = "http://localhost:8000"
API_KEY = "im_your_key_here"
headers = {"X-API-Key": API_KEY}

def get_prayer_times(latitude, longitude, timezone="UTC", lang="ar"):
    response = requests.get(
        f"{BASE_URL}/api/v1/{lang}/prayer-times",
        headers=headers,
        params={"latitude": latitude, "longitude": longitude, "timezone": timezone}
    )
    response.raise_for_status()
    return response.json()

# الاستخدام
times = get_prayer_times(30.04, 31.23, "Africa/Cairo")
for prayer in times["prayers"]:
    print(f"{prayer['name']}: {prayer['time']}")
```

---

## JavaScript

```javascript
const BASE_URL = "http://localhost:8000";
const API_KEY = "im_your_key_here";
const headers = { "X-API-Key": API_KEY };

async function getPrayerTimes(lat, lng, timezone = "UTC", lang = "ar") {
  const params = new URLSearchParams({ latitude: lat, longitude: lng, timezone });
  const response = await fetch(
    `${BASE_URL}/api/v1/${lang}/prayer-times?${params}`,
    { headers }
  );
  return response.json();
}

// الاستخدام
const times = await getPrayerTimes(30.04, 31.23, "Africa/Cairo");
times.prayers.forEach(p => console.log(`${p.name}: ${p.time}`));
```

---

## Flutter/Dart

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class IslamMateClient {
  final String baseUrl;
  final String apiKey;
  final String lang;

  IslamMateClient({
    this.baseUrl = 'http://localhost:8000',
    required this.apiKey,
    this.lang = 'ar',
  });

  Map<String, String> get headers => {'X-API-Key': apiKey};

  Future<Map<String, dynamic>> getPrayerTimes({
    required double latitude,
    required double longitude,
    String timezone = 'UTC',
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/$lang/prayer-times').replace(
      queryParameters: {
        'latitude': latitude.toString(),
        'longitude': longitude.toString(),
        'timezone': timezone,
      },
    );
    final response = await http.get(uri, headers: headers);
    return json.decode(response.body);
  }
}
```

---

## Android (Kotlin)

```kotlin
// build.gradle
implementation 'com.squareup.retrofit2:retrofit:2.9.0'
implementation 'com.squareup.retrofit2:converter-gson:2.9.0'

// IslamMateApi.kt
interface IslamMateApi {
  @GET("api/v1/{lang}/prayer-times")
  suspend fun getPrayerTimes(
    @Path("lang") lang: String = "ar",
    @Query("latitude") latitude: Double,
    @Query("longitude") longitude: Double,
    @Query("timezone") timezone: String = "UTC"
  ): Response<PrayerTimesResponse>
}
```

---

## نصائح

::: tip المنطقة الزمنية
دائماً ارسل المنطقة الزمنية للحصول على الاوقات المحلية الصحيحة.
```
timezone=Africa/Cairo       # مصر
timezone=Asia/Riyadh        # السعودية
timezone=Asia/Dubai         # الامارات
timezone=Asia/Karachi       # باكستان
```
:::

::: warning تحديد المعدل
اذا حصلت على **429** انتظر 60 ثانية قبل المحاولة مجدداً. احفظ النتائج محلياً عند الامكان.
:::
