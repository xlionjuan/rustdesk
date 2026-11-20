# Preserve the binaries and assets already staged by the DRM DEB build.
%global __os_install_post %{nil}

Name:       rustdesk-unattended-wayland
Version:    %{drm_version}
Release:    0
Summary:    RustDesk with unattended Wayland support
License:    GPL-3.0
URL:        https://rustdesk.com
ExclusiveArch: x86_64
Conflicts:  rustdesk

%description
RustDesk remote desktop client with support for unattended sessions on Wayland.

%install
dpkg-deb -x "%{drm_deb}" "%{buildroot}"
ln -s /usr/share/rustdesk/rustdesk "%{buildroot}/usr/bin/rustdesk"
install -Dm 644 "%{buildroot}/usr/share/rustdesk/files/systemd/rustdesk.service" \
    "%{buildroot}/usr/lib/systemd/system/rustdesk.service"

%files
/usr/bin/rustdesk
/usr/lib/rustdesk/
/usr/lib/systemd/system/rustdesk.service
/usr/share/applications/rustdesk.desktop
/usr/share/applications/rustdesk-link.desktop
/usr/share/icons/hicolor/256x256/apps/rustdesk.png
/usr/share/icons/hicolor/scalable/apps/rustdesk.svg
/usr/share/rustdesk/

%post
if [ -d /run/systemd/system ]; then
    systemctl daemon-reload
    if [ "$1" -eq 1 ]; then
        systemctl enable --now rustdesk.service
    else
        systemctl try-restart rustdesk.service
    fi
fi

%preun
if [ "$1" -eq 0 ] && [ -d /run/systemd/system ]; then
    systemctl disable --now rustdesk.service
fi

%postun
if [ "$1" -eq 0 ] && [ -d /run/systemd/system ]; then
    systemctl daemon-reload
fi
