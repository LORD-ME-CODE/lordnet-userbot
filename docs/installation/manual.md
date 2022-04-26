---
title: Ручная установка
layout: default
parent: Установка
nav_order: 4
---

# {{ page.title }}

Тут собраны все способы установки для разных OS

## Debian-like Linux

1. Обновляем список пакетов
```
sudo apt update
```

2. Устанавливаем python и git
```
sudo apt install python3 python3-pip git
```

3. Устанавливаем другие пакеты для некоторых модулей (*необязательно*)
#### Pillow для стикеров и прочего
```
sudo apt install python3-dev libwebp-dev libz-dev libjpeg-dev libopenjp2-7 libtiff5
```
#### Python opencv для видео-стикеров и прочего
```
sudo apt install python3-opencv
```

4. Копируем сурсы
```
cd
git clone https://github.com/LORD-ME-CODE/lordnet-userbot
cd lordnet-userbot
```

5. Устанавливаем зависимости
```
python3 -m pip install -r requirements.txt
```

6. Прочитайте [инструкцию](https://core.telegram.org/api/obtaining_api_id "here") чтобы получить API key/hash и ID

7. Запустите установщик с аргументом "3" (то есть ручная установка)
```
python3 install.py 3
```

8. В открытом меню введите ваши API_ID и API_HASH и нажмите "Продолжить"

9. Launch the bot:
```
cd ~/lordnet-userbot
python3 run.py
```

## Termux

```
pkg install git python3 libjpeg-turbo zlib libwebp libffi
git clone https://github.com/LORD-ME-CODE/lordnet-userbot
cd lordnet-userbot
pip3 install -r requirements.txt
```
#### Для преднастроек
```
python3 install.py 3
```
#### Для запуска
```
python3 run.py
```

## Windows

1. Скачайте Git из [сайта](https://git-scm.com/download/win "из сайта"). **Проверь добавлен ли git в PATH**

2. Скачайте python из [сайта](https://www.python.org/downloads/windows "из сайта"). **Проверь добавлен ли Python в PATH**

3. Откройте Windows Powershell [инструкция](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=3&cad=rja&uact=8&ved=2ahUKEwijicaXspvkAhVDaFAKHT26DHgQFjACegQIChAG&url=https%3A%2F%2Fwww.isunshare.com%2Fwindows-10%2F5-ways-to-open-windows-powershell-in-windows-10.html "инструкция"). 

4. Прочитайте [инструкцию](https://core.telegram.org/api/obtaining_api_id "инструкцию") чтобы получить API key/hash и ID

5. Напишите:
```
git clone https://github.com/LORD-ME-CODE/lordnet-userbot
cd lordnet-userbot
python3 -m pip install -r requirements.txt
python3 install.py 3
```

6. Запустите бота:
```
python3 run.py
```

## Mac OS X

1. Установите Homebrew
```
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

2. Установите зависимости
```
brew install python3  git
```

3. Установите вручную эти библиотеки (нужно только для модулей с стикерами):
 - libwebp -> https://github.com/webmproject/libwebp
 - libjpeg -> https://github.com/LuaDist/libjpeg

4. Прочитайте инструкцию [тут](https://core.telegram.org/api/obtaining_api_id "here") чтобы получить ваш API_ID и API_HASH/KEY

5. Напишите:
```
git clone https://github.com/LORD-ME-CODE/lordnet-userbot
cd lordnet-userbot
python -m pip install -r requirements.txt
python install.py 3
```

7. Запустите бота
```
python run.py
```
