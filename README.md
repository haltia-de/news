# Новости

Новости (`haltia-news`): лента из RSS и Atom, статья читается внутри
программы.

- По умолчанию три петербургские ленты: Интерфакс, Фонтанка, Деловой
  Петербург.
- Текст статьи берётся из ленты, если она несёт его целиком, иначе со
  страницы статьи (JSON-LD `articleBody`, абзацы `itemprop="articleBody"`),
  иначе — краткое содержание из ленты. Кнопка под статьёй открывает полную
  версию в браузере.
- Свои источники: шестерёнка в заголовке — список, удаление и добавление
  ленты или сайта (лента находится через `<link rel="alternate">`, поиск по
  названию и теме — через Feedly и feedsearch.dev). Хранятся в
  `~/.config/haltia/news.conf`.

## Установка

**Ubuntu 24.04, Debian 13** (и elementary OS 8, Linux Mint 22) — из
репозитория apt Haltia:

```
sudo curl -fsSLo /usr/share/keyrings/haltia-archive-keyring.gpg https://haltia-de.github.io/packages/apt/haltia-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/haltia-archive-keyring.gpg] https://haltia-de.github.io/packages/apt $(. /etc/os-release; echo $VERSION_CODENAME) main" | sudo tee /etc/apt/sources.list.d/haltia.list
sudo apt update && sudo apt install haltia-news
```

**Flatpak** (любой дистрибутив; среда GNOME — с Flathub):

```
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak remote-add --if-not-exists haltia https://haltia-de.github.io/packages/flatpak/haltia.flatpakrepo
flatpak install haltia io.github.haltia_de.News
```

В Flatpak настройки лежат в `~/.var/app/io.github.haltia_de.News/config/haltia/news.conf`.

**Alpine и postmarketOS** — пакет `haltia-news` из
[репозитория apk Haltia](https://github.com/haltia-de/packages).

**Из исходников:** нужны Python 3, GTK 3 и PyGObject, feedparser.

```
sh install.sh            # в / (нужен root)
sh install.sh /mnt/root  # в другой корень, например при сборке образа
```

`install.sh` кладёт программу модулем в `/usr/local/lib/haltia-news/haltia_news_main.py`
(так Python берёт её уже скомпилированной), в `/usr/local/bin/haltia-news` — короткий
запускающий её файл (пакет — в `/usr`), её `.desktop`, значок и описание AppStream. Сборка пакетов:
`debian/` и `packaging/flatpak/`, выпуск по тегу — `haltia-de/ci`.

## Haltia

Программа — часть среды [Haltia](https://github.com/haltia-de): образы
Pertin Haltia ставят её пакетом `haltia-news`, оболочка показывает её на
домашнем экране. На любом другом рабочем столе с GTK 3 она работает так же:
вне оболочки у окна обычные кнопки, в том числе «Закрыть».

## Лицензия

GPL-2.0 (`LICENSE`).
