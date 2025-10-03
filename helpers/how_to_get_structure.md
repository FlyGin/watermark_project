Автоматически выводит структуру **относительно текущей папки**, то есть с корнем `.` и без абсолютных путей.
```powershell
```
tree /F /A > structure.txt
```

А далее отредактируем по паттерну
```powershell
Get-Content structure.txt | Select-String -Pattern "^\s*[|+\\-]" | Set-Content clean_structure.txt
```

