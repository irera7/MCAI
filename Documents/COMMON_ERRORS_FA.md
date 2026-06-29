# ⚠️ خطای رایج: Cannot open DLL for writing

## مشکل
```
CSC : error CS2012: Cannot open 'ModelCreator.UI.dll' for writing
-- 'The process cannot access the file because it is being used by another process.'
```

## علت
برنامه قبلی هنوز در حال اجرا است و فایل DLL را قفل کرده.

## ✅ راه‌حل‌ها:

### 1️⃣ بستن برنامه (ساده‌ترین)
1. پنجره برنامه WPF را پیدا کنید
2. آن را ببندید (کلیک روی X)
3. دوباره `dotnet run` کنید

### 2️⃣ بستن از Task Manager
```
1. Ctrl + Shift + Esc (باز کردن Task Manager)
2. به تب "Details" بروید
3. "ModelCreator.UI.exe" را پیدا کنید
4. Right-click → End Task
5. دوباره build کنید
```

### 3️⃣ بستن با PowerShell
```powershell
# کشتن تمام process های ModelCreator
Get-Process | Where-Object {$_.ProcessName -like "*ModelCreator*"} | Stop-Process -Force

# سپس build کنید
dotnet build
dotnet run --project ModelCreator.UI
```

### 4️⃣ Clean و Rebuild (اگر بالایی‌ها کار نکرد)
```powershell
# پاک کردن فایل‌های build قبلی
dotnet clean

# منتظر بمانید چند ثانیه
Start-Sleep -Seconds 3

# Build مجدد
dotnet build
dotnet run --project ModelCreator.UI
```

### 5️⃣ Restart کامل (آخرین راه)
```powershell
# بستن تمام process ها
Get-Process | Where-Object {$_.Path -like "*ModelCreator*"} | Stop-Process -Force

# حذف فولدر obj و bin
Remove-Item -Recurse -Force .\ModelCreator.UI\obj, .\ModelCreator.UI\bin

# Build از نو
dotnet restore
dotnet build
dotnet run --project ModelCreator.UI
```

## 🎯 دستور سریع (کپی-پیست):
```powershell
# این همه کار را انجام می‌دهد:
Get-Process | Where-Object {$_.ProcessName -like "*ModelCreator*"} | Stop-Process -Force -ErrorAction SilentlyContinue; Start-Sleep -Seconds 2; dotnet clean; Start-Sleep -Seconds 2; dotnet run --project ModelCreator.UI
```

## 💡 نکته مهم:
این خطا **نشان‌دهنده مشکل در کد نیست**! 
فقط یعنی برنامه قبلی هنوز باز است.

## 🔍 چک کردن Process ها:
```powershell
# لیست تمام process های در حال اجرا
Get-Process | Where-Object {$_.ProcessName -like "*ModelCreator*"}

# اگر خروجی داشت، یعنی برنامه هنوز در حال اجرا است
```

## ⚙️ جلوگیری از این مشکل:
1. همیشه برنامه را به درستی ببندید (از منوی File یا دکمه X)
2. قبل از build جدید، مطمئن شوید برنامه بسته است
3. از Task Manager برای چک کردن استفاده کنید

---

**در 99% موارد راه‌حل 1 یا 3 کافی است!** ✅

