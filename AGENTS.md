# News

News (`haltia-news`) is a GTK 3 RSS and Atom reader for the Haltia desktop.
It combines selected feeds and displays article text inside the application.
It also runs on other GTK desktops. Its application ID is
`io.github.haltia_de.News`.

## Project rules

The project root repository is [haltia-de/haltia](https://github.com/haltia-de/haltia).
Follow its [shared conventions](https://github.com/haltia-de/haltia/blob/main/docs/conventions.md).
The root-repository and agent-instruction decision is
[ADR 0005](https://github.com/haltia-de/haltia/blob/main/docs/adr/0005-root-repo-and-agents.md).

## Repository layout

- `haltia-news`: Python application, feed discovery, article extraction and UI.
- `data/`: desktop entries, SVG icon and AppStream metainfo.
- `news-*.png`: newspaper logos, loaded from the checkout or installed data.
- `requirements.txt`: pinned feedparser and sgmllib3k dependencies.
- `install.sh`: installs the application, compatibility names and data files.
- `packaging/alpine/`: APKBUILD for Alpine and postmarketOS.
- `packaging/flatpak/`: Flatpak manifest using the GNOME runtime.
- `debian/`: Debian and Ubuntu package metadata and build rules.
- `.github/workflows/release.yml`: release workflow using `haltia-de/ci`.
- `README.md` and `NEWS.md`: user documentation and release notes.

## Run and install

With Python 3, GTK 3, PyGObject and feedparser available, run from the checkout:

```sh
python3 haltia-news
```

Install with `sh install.sh` (requires root for the default system destination).
The default prefix is `/usr/local`; `sh install.sh /mnt/root /usr` stages an
installation under another root with the package prefix `/usr`.
The installer copies files; dependencies must already be available.

## Releases

A release requires the user's explicit approval before tagging or publishing.
Prepare release notes in `NEWS.md` and keep the `vX.Y.Z` tag version aligned
with `pkgver` in `packaging/alpine/APKBUILD` and the AppStream release version
in `data/io.github.haltia_de.News.metainfo.xml`, following the shared conventions.
Pushing a `vX.Y.Z` tag triggers `.github/workflows/release.yml`, which calls
the reusable workflows in `haltia-de/ci` to build Alpine, Debian/Ubuntu and
Flatpak packages and attach them to the GitHub release.
