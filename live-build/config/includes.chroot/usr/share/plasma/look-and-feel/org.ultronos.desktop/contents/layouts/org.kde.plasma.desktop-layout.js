// Ultron OS default desktop layout (Plasma 6).
// Runs once, the first time a user logs in. Everything here can be changed
// afterwards with right-click > "Enter Edit Mode".

const WALLPAPER = "file:///usr/share/wallpapers/Ultron/contents/images/3840x2160.jpg";

function launcher(panel, desktopFile) {
    if (!applicationExists(desktopFile)) {
        return null;
    }
    const icon = panel.addWidget("org.kde.plasma.icon");
    icon.currentConfigGroup = ["General"];
    icon.writeConfig("url", "file:///usr/share/applications/" + desktopFile);
    return icon;
}

// ---- top bar ---------------------------------------------------------------
const bar = new Panel;
bar.location = "top";
bar.height = Math.round(gridUnit * 1.7);
bar.lengthMode = "fill";
bar.floating = false;
bar.hiding = "none";
bar.opacity = "translucent";

const menu = bar.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "ultron-logo");
menu.writeConfig("favorites", [
    "applications:firefox-esr.desktop",
    "applications:org.kde.dolphin.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:org.kde.discover.desktop",
    "applications:systemsettings.desktop"
]);

const pager = bar.addWidget("org.kde.plasma.pager");
pager.currentConfigGroup = ["General"];
pager.writeConfig("displayedText", "Number");
pager.writeConfig("showWindowOutlines", false);
pager.writeConfig("showWindowIcons", false);

bar.addWidget("org.kde.plasma.panelspacer");
bar.addWidget("org.kde.plasma.systemtray");

const clock = bar.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", true);
clock.writeConfig("dateDisplayFormat", "BesideTime");
clock.writeConfig("dateFormat", "custom");
clock.writeConfig("customDateFormat", "ddd, MMM d");
clock.writeConfig("use24hFormat", 2);
clock.writeConfig("autoFontAndSize", false);
clock.writeConfig("fontFamily", "Inter");
clock.writeConfig("fontSize", 10);
clock.writeConfig("fontWeight", 500);

const power = bar.addWidget("org.kde.plasma.lock_logout");
power.currentConfigGroup = ["General"];
power.writeConfig("show_lockScreen", false);
power.writeConfig("show_requestLogout", false);
power.writeConfig("show_requestReboot", false);
power.writeConfig("show_requestShutDown", false);
power.writeConfig("show_switchUser", false);
power.writeConfig("show_suspendToRam", false);
power.writeConfig("show_suspendToDisk", false);
power.writeConfig("show_requestLogoutScreen", true);

// ---- dock (bottom, floating, hugs its content) -----------------------------
const dock = new Panel;
dock.location = "bottom";
dock.height = Math.round(gridUnit * 3.2);
dock.lengthMode = "fit";
dock.alignment = "center";
dock.floating = true;
dock.hiding = "dodgewindows";
dock.opacity = "translucent";

const pinned = [
    "applications:org.kde.konsole.desktop",
    "applications:org.kde.dolphin.desktop",
    "applications:firefox-esr.desktop",
    "applications:org.kde.elisa.desktop",
    "applications:org.kde.discover.desktop",
    "applications:systemsettings.desktop"
];
// The installer is only present on the live medium; it is removed from the
// installed system, so freshly created users never see it here.
if (applicationExists("ultron-installer.desktop")) {
    pinned.unshift("applications:ultron-installer.desktop");
}
const tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", pinned);
tasks.writeConfig("indicateAudioStreams", true);
tasks.writeConfig("fill", false);
tasks.writeConfig("iconSpacing", 2);
dock.addWidget("org.kde.plasma.marginsseparator");
dock.addWidget("org.kde.plasma.trash");

// ---- side rail (left, floating) --------------------------------------------
// Quick launchers only: running apps live in the dock, so nothing is listed
// twice. It slides away when a window needs the room.
const rail = new Panel;
rail.location = "left";
rail.height = Math.round(gridUnit * 2.9);
rail.lengthMode = "fit";
rail.alignment = "center";
rail.floating = true;
rail.hiding = "dodgewindows";
rail.opacity = "translucent";

launcher(rail, "org.kde.dolphin.desktop");
launcher(rail, "firefox-esr.desktop");
launcher(rail, "org.kde.konsole.desktop");
launcher(rail, "org.kde.elisa.desktop");
launcher(rail, "org.kde.haruna.desktop");
launcher(rail, "org.kde.plasma-systemmonitor.desktop");
launcher(rail, "systemsettings.desktop");
rail.addWidget("org.kde.plasma.marginsseparator");
const grid = rail.addWidget("org.kde.plasma.kickoff");
grid.currentConfigGroup = ["General"];
grid.writeConfig("icon", "view-app-grid-symbolic");

// ---- desktop -----------------------------------------------------------------
const desks = desktopsForActivity(currentActivity());
for (let i = 0; i < desks.length; i++) {
    desks[i].wallpaperPlugin = "org.kde.image";
    desks[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desks[i].writeConfig("Image", WALLPAPER);
    desks[i].writeConfig("PreviewImage", WALLPAPER);
    desks[i].writeConfig("FillMode", 2);
}
