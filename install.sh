#!/bin/sh
# SPDX-License-Identifier: GPL-2.0
# Install b8k-news (Новости): sh install.sh [ROOT] [PREFIX]
# ROOT empty or / for this system; PREFIX /usr/local unless given (a
# package passes /usr). It needs Python 3 with PyGObject (GTK 3) only. The
# .desktop file
# shows it in any desktop's launcher; the b8k tablet shell puts it on its
# home screen (X-B8K-Home).
set -eu
root=${1:-}
root=${root%/}
prefix=${2:-/usr/local}
here=$(cd "$(dirname "$0")" && pwd)
share=$root$prefix/share
install -D -m 755 "$here/b8k-news" "$root$prefix/bin/b8k-news"
install -D -m 644 "$here/data/io.github.trudenboy.News.desktop" "$share/applications/io.github.trudenboy.News.desktop"
install -D -m 644 "$here/data/io.github.trudenboy.News.svg" "$share/icons/hicolor/scalable/apps/io.github.trudenboy.News.svg"
install -D -m 644 "$here/data/io.github.trudenboy.News.metainfo.xml" "$share/metainfo/io.github.trudenboy.News.metainfo.xml"
# The shell's old entry for this program, from before the .desktop file.
rm -f "$root/usr/local/share/b8k/apps.d/news.conf" "$root/usr/local/share/b8k/news.svg"
# The papers' logos (b8k-news finds them next to PREFIX/bin).
for f in news-dp.png news-fontanka.png news-interfax.png; do
	install -D -m 644 "$here/$f" "$share/b8k-news/$f"
	rm -f "$root/usr/local/share/b8k/$f"
done
