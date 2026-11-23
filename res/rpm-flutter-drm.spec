Name:       rustdesk-unattended-wayland
Version:    %{drm_version}
Release:    0
Summary:    RustDesk with unattended Wayland support
License:    GPL-3.0
URL:        https://rustdesk.com
Vendor:     rustdesk <info@rustdesk.com>
ExclusiveArch: x86_64
Conflicts:  rustdesk
Requires:   gtk3 libxcb libXfixes alsa-lib libva gstreamer1-plugins-base
Requires:   libdrm >= 2.4.101
Requires:   libglvnd-egl libglvnd-gles systemd desktop-file-utils
Recommends: libayatana-appindicator-gtk3 libxdo

%description
RustDesk remote desktop client with support for unattended sessions on Wayland.

%install
set -- "$HBB"/third_party/libdrmtap/build-pkg/libdrmtap.so.0.*
if [ "$#" -ne 1 ] || [ ! -f "$1" ] || [ -L "$1" ]; then
    echo 'Expected one versioned libdrmtap shared library' >&2
    exit 1
fi

mkdir -p "%{buildroot}/usr/share/rustdesk"
cp -r "$HBB"/flutter/build/linux/x64/release/bundle/. "%{buildroot}/usr/share/rustdesk"
install -Dm 644 "$HBB/res/rustdesk.service" -t "%{buildroot}/usr/share/rustdesk/files"
install -Dm 644 "$HBB/res/rustdesk.desktop" -t "%{buildroot}/usr/share/rustdesk/files"
install -Dm 644 "$HBB/res/rustdesk-link.desktop" -t "%{buildroot}/usr/share/rustdesk/files"
install -Dm 644 "$HBB/res/128x128@2x.png" "%{buildroot}/usr/share/icons/hicolor/256x256/apps/rustdesk.png"
install -Dm 644 "$HBB/res/scalable.svg" "%{buildroot}/usr/share/icons/hicolor/scalable/apps/rustdesk.svg"

# RustDesk loads libdrmtap by absolute path, including on x86_64.
install -Dm 755 "$1" -t "%{buildroot}/usr/lib/rustdesk"
ln -s "${1##*/}" "%{buildroot}/usr/lib/rustdesk/libdrmtap.so.0"

%check
librustdesk="%{buildroot}/usr/share/rustdesk/lib/librustdesk.so"
if ! grep -qF '/usr/lib/rustdesk/libdrmtap.so.0' "$librustdesk" ||
   ! grep -qF 'enable-drm-display-wake' "$librustdesk"; then
    echo 'Expected a RustDesk build with drm and drm-wake enabled' >&2
    exit 1
fi

%files
/usr/lib/rustdesk/
/usr/share/rustdesk/
/usr/share/icons/hicolor/256x256/apps/rustdesk.png
/usr/share/icons/hicolor/scalable/apps/rustdesk.svg

%pre
if [ "$1" -gt 1 ]; then
    systemctl stop rustdesk || true
fi

%post
cp /usr/share/rustdesk/files/rustdesk.service /etc/systemd/system/rustdesk.service
cp /usr/share/rustdesk/files/rustdesk.desktop /usr/share/applications/
cp /usr/share/rustdesk/files/rustdesk-link.desktop /usr/share/applications/
ln -sf /usr/share/rustdesk/rustdesk /usr/bin/rustdesk
systemctl daemon-reload
systemctl enable rustdesk
systemctl start rustdesk
update-desktop-database

%preun
if [ "$1" -eq 0 ]; then
    systemctl stop rustdesk || true
    systemctl disable rustdesk || true
    rm -f /etc/systemd/system/rustdesk.service
fi

%postun
if [ "$1" -eq 0 ]; then
    rm -f /usr/bin/rustdesk /usr/share/applications/rustdesk.desktop /usr/share/applications/rustdesk-link.desktop
    systemctl daemon-reload
    update-desktop-database
fi
