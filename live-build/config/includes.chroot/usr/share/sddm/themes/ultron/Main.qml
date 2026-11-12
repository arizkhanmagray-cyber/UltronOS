// Ultron OS login screen.
//
// Opening sequence: a dot appears, draws itself into a "U", the U writes out
// "ltron", the wordmark lifts and the password field for the selected account
// fades in. Any key or click skips straight to the password field.
//
// Plain QtQuick + SDDM's own context objects only (userModel, sessionModel,
// sddm, keyboard, config) so it starts fast and cannot break on a Plasma update.

import QtQuick

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#0c0d0d"

    // ---- theme ----------------------------------------------------------------
    readonly property color ink: "#f2f3f2"
    readonly property color inkDim: "#a9b0ad"
    readonly property color accent: config.accent ? config.accent : "#86b39c"
    readonly property string face: config.font ? config.font : "Inter"
    readonly property real u: Math.max(0.62, Math.min(width / 1920, height / 1080))  // layout unit

    // ---- state ----------------------------------------------------------------
    property var users: []                 // [{name, realName}]
    property int userIndex: 0
    property var sessions: []              // [{name, file}]
    property int sessionIndex: 0
    property bool busy: false
    property string notice: ""

    readonly property bool askName: users.length === 0
    readonly property string userName: askName ? nameInput.text : users[userIndex].name
    readonly property string displayName: askName ? "" : (users[userIndex].realName || users[userIndex].name)

    // animation drivers
    property real dotOpacity: 0            // dot fades in
    property real dotGrow: 2.1             // dot radius, in stroke half-widths
    property real draw: 0                  // 0..1 how much of the U is drawn
    property real reveal: 0                // 0..1 how much of "ltron" is written
    property real lift: 0                  // 0..1 wordmark moves up
    property real formOpacity: 0

    function pickDefaults() {
        // Last user if SDDM remembers one, otherwise the first.
        var last = userModel.lastUser;
        for (var i = 0; i < users.length; i++) {
            if (users[i].name === last) { userIndex = i; break; }
        }
        // Remembered session for returning users; Wayland for a first login.
        var idx = sessionModel.lastIndex;
        if (!last || idx < 0 || idx >= sessions.length) {
            idx = 0;
            for (var j = 0; j < sessions.length; j++) {
                if (/wayland/i.test(sessions[j].name) || /wayland-sessions/.test(sessions[j].file)) { idx = j; break; }
            }
        }
        sessionIndex = idx;
    }

    function finishIntro() {
        intro.stop();
        dotOpacity = 1; dotGrow = 1; draw = 1; reveal = 1; lift = 1; formOpacity = 1;
        focusField();
    }

    function focusField() {
        if (askName && nameInput.text.length === 0) nameInput.forceActiveFocus();
        else passInput.forceActiveFocus();
    }

    function submit() {
        if (busy || userName.length === 0) return;
        busy = true;
        notice = "";
        sddm.login(userName, passInput.text, sessionIndex);
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            root.busy = false;
            root.notice = qsTr("That password is not right. Try again.");
            passInput.text = "";
            shake.restart();
            passInput.forceActiveFocus();
        }
        function onLoginSucceeded() {
            leave.start();
        }
    }

    // Collect the models into plain arrays (keeps the rest of the file simple).
    Repeater {
        model: userModel
        Item {
            Component.onCompleted: {
                root.users.push({ name: model.name, realName: model.realName });
                root.usersChanged();
            }
        }
    }
    Repeater {
        model: sessionModel
        Item {
            Component.onCompleted: {
                root.sessions.push({ name: model.name, file: model.file });
                root.sessionsChanged();
            }
        }
    }

    // ---- background -------------------------------------------------------------
    Image {
        id: backdrop
        anchors.fill: parent
        source: config.background ? Qt.resolvedUrl(config.background) : ""
        fillMode: Image.PreserveAspectCrop
        asynchronous: false
        opacity: 0.25 + 0.75 * root.lift       // stays dim until the wordmark settles
    }
    Rectangle {                                 // darkens toward the edges
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#99000000" }
            GradientStop { position: 0.45; color: "#33000000" }
            GradientStop { position: 1.0; color: "#b3000000" }
        }
    }

    // ---- measurements taken from the font, so the drawn U matches the letters --
    TextMetrics {
        id: capProbe
        font: word.font
        text: "H"
    }
    TextMetrics {
        id: stemProbe
        font: word.font
        text: "l"
    }

    // ---- wordmark ----------------------------------------------------------------
    Item {
        id: brand
        readonly property real cap: Math.max(8, capProbe.tightBoundingRect.height)      // cap height
        readonly property real stroke: Math.max(3, stemProbe.tightBoundingRect.width)   // stem thickness
        readonly property real uWidth: Math.round(cap * 0.80)
        readonly property real gap: Math.round(word.font.pixelSize * 0.075)
        readonly property real pad: Math.ceil(stroke * 1.4)                             // room for the big dot

        width: uWidth + (gap + word.implicitWidth) * root.reveal
        height: cap
        x: Math.round((root.width - width) / 2)
        y: Math.round(root.height * 0.5 - cap / 2 - root.lift * root.height * 0.17)
        scale: 1 - 0.18 * root.lift
        transformOrigin: Item.Center

        Canvas {
            id: mark
            x: -brand.pad
            y: -brand.pad
            width: brand.uWidth + 2 * brand.pad
            height: brand.cap + 2 * brand.pad
            opacity: root.dotOpacity
            antialiasing: true

            property real t: root.draw
            property real grow: root.dotGrow
            onTChanged: requestPaint()
            onGrowChanged: requestPaint()
            onWidthChanged: requestPaint()
            onHeightChanged: requestPaint()

            onPaint: {
                var ctx = getContext("2d");
                ctx.reset();
                var sw = brand.stroke;
                var r = (brand.uWidth - sw) / 2;                 // radius of the bowl (centre line)
                var xl = brand.pad + sw / 2;                     // left stem
                var xr = xl + 2 * r;                             // right stem
                var y0 = brand.pad + sw / 2;                     // where the pen starts
                var cy = brand.pad + brand.cap - sw / 2 - r;     // centre of the bowl
                var stem = Math.max(0, cy - y0);
                var arc = Math.PI * r;
                var d = t * (2 * stem + arc);

                ctx.strokeStyle = root.ink;
                ctx.fillStyle = root.ink;
                ctx.lineWidth = sw;
                ctx.lineCap = "round";
                ctx.lineJoin = "round";

                // the dot the whole thing grows from
                if (grow > 1.001 || d <= 0.01) {
                    ctx.beginPath();
                    ctx.arc(xl, y0, sw / 2 * grow, 0, 2 * Math.PI, false);
                    ctx.fill();
                }
                if (d <= 0.01) return;

                ctx.beginPath();
                ctx.moveTo(xl, y0);
                ctx.lineTo(xl, y0 + Math.min(d, stem));
                if (d > stem) {
                    var a = Math.min(d - stem, arc) / r;
                    ctx.arc(xl + r, cy, r, Math.PI, Math.PI - a, true);
                }
                if (d > stem + arc) {
                    ctx.lineTo(xr, cy - (d - stem - arc));
                }
                ctx.stroke();
            }
        }

        Item {                                  // "ltron" is wiped in from the U
            x: brand.uWidth + brand.gap
            y: -brand.cap                       // head-room for ascenders
            width: Math.ceil(word.implicitWidth * root.reveal) + 2
            height: brand.cap * 3
            clip: true
            Text {
                id: word
                text: "ltron"
                color: root.ink
                font.family: root.face
                font.pixelSize: Math.round(96 * root.u)
                font.weight: Font.Medium
                font.kerning: true
                renderType: Text.QtRendering
                x: -(1 - root.reveal) * font.pixelSize * 0.35
                // sit on the same baseline as the bottom of the U
                y: 2 * brand.cap - baselineOffset
                opacity: Math.min(1, root.reveal * 1.6)
            }
        }
    }

    SequentialAnimation {
        id: intro
        running: false
        PauseAnimation { duration: 350 }
        NumberAnimation { target: root; property: "dotOpacity"; from: 0; to: 1; duration: 420; easing.type: Easing.OutCubic }
        NumberAnimation { target: root; property: "dotGrow"; to: 2.7; duration: 260; easing.type: Easing.OutQuad }
        NumberAnimation { target: root; property: "dotGrow"; to: 1.0; duration: 320; easing.type: Easing.InOutQuad }
        NumberAnimation { target: root; property: "draw"; from: 0; to: 1; duration: 950; easing.type: Easing.InOutCubic }
        PauseAnimation { duration: 140 }
        NumberAnimation { target: root; property: "reveal"; from: 0; to: 1; duration: 850; easing.type: Easing.OutCubic }
        PauseAnimation { duration: 420 }
        ParallelAnimation {
            NumberAnimation { target: root; property: "lift"; from: 0; to: 1; duration: 650; easing.type: Easing.InOutCubic }
            SequentialAnimation {
                PauseAnimation { duration: 260 }
                NumberAnimation { target: root; property: "formOpacity"; from: 0; to: 1; duration: 520; easing.type: Easing.OutCubic }
            }
        }
        ScriptAction { script: root.focusField() }
    }

    // ---- sign-in form -----------------------------------------------------------
    Item {
        id: form
        width: Math.round(340 * root.u)
        height: column.height
        x: Math.round((root.width - width) / 2)
        y: Math.round(root.height * 0.5 - 6 * root.u + (1 - root.formOpacity) * 14 * root.u)
        opacity: root.formOpacity
        enabled: root.formOpacity > 0.9

        Column {
            id: column
            width: parent.width
            spacing: Math.round(14 * root.u)

            // who is signing in
            Item {
                width: parent.width
                height: who.height
                visible: !root.askName
                Row {
                    id: who
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: Math.round(10 * root.u)
                    Text {
                        visible: root.users.length > 1
                        text: "‹"
                        color: root.inkDim
                        font.family: root.face
                        font.pixelSize: Math.round(22 * root.u)
                    }
                    Text {
                        text: root.displayName
                        color: root.ink
                        font.family: root.face
                        font.pixelSize: Math.round(21 * root.u)
                        font.weight: Font.Medium
                    }
                    Text {
                        visible: root.users.length > 1
                        text: "›"
                        color: root.inkDim
                        font.family: root.face
                        font.pixelSize: Math.round(22 * root.u)
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    enabled: root.users.length > 1
                    cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                    onClicked: function (mouse) {
                        var n = root.users.length;
                        root.userIndex = (root.userIndex + (mouse.x < width / 2 ? n - 1 : 1)) % n;
                        root.notice = "";
                        passInput.text = "";
                        passInput.forceActiveFocus();
                    }
                }
            }

            // only when the system has no listed accounts
            Rectangle {
                visible: root.askName
                width: parent.width
                height: Math.round(42 * root.u)
                radius: height / 2
                color: "#1fffffff"
                border.color: nameInput.activeFocus ? root.accent : "#33ffffff"
                border.width: 1
                TextInput {
                    id: nameInput
                    anchors.fill: parent
                    anchors.leftMargin: parent.height * 0.48
                    anchors.rightMargin: parent.height * 0.48
                    verticalAlignment: TextInput.AlignVCenter
                    color: root.ink
                    font.family: root.face
                    font.pixelSize: Math.round(15 * root.u)
                    clip: true
                    selectByMouse: true
                    selectionColor: root.accent
                    KeyNavigation.tab: passInput
                    onAccepted: passInput.forceActiveFocus()
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        visible: parent.text.length === 0
                        text: qsTr("User name")
                        color: "#80ffffff"
                        font: parent.font
                    }
                }
            }

            // password pill
            Rectangle {
                id: pill
                width: parent.width
                height: Math.round(42 * root.u)
                radius: height / 2
                color: "#1fffffff"
                border.color: passInput.activeFocus ? root.accent : "#33ffffff"
                border.width: 1

                property real nudge: 0
                transform: Translate { x: pill.nudge }
                SequentialAnimation {
                    id: shake
                    NumberAnimation { target: pill; property: "nudge"; to: -12; duration: 50 }
                    NumberAnimation { target: pill; property: "nudge"; to: 12; duration: 90 }
                    NumberAnimation { target: pill; property: "nudge"; to: -7; duration: 80 }
                    NumberAnimation { target: pill; property: "nudge"; to: 7; duration: 70 }
                    NumberAnimation { target: pill; property: "nudge"; to: 0; duration: 60 }
                }

                TextInput {
                    id: passInput
                    anchors.fill: parent
                    anchors.leftMargin: parent.height * 0.48
                    anchors.rightMargin: parent.height * 1.05
                    verticalAlignment: TextInput.AlignVCenter
                    echoMode: TextInput.Password
                    passwordCharacter: "•"
                    color: root.ink
                    font.family: root.face
                    font.pixelSize: Math.round(15 * root.u)
                    clip: true
                    enabled: !root.busy
                    selectByMouse: false
                    selectionColor: root.accent
                    onAccepted: root.submit()
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        visible: parent.text.length === 0
                        text: qsTr("Password")
                        color: "#80ffffff"
                        font.family: root.face
                        font.pixelSize: Math.round(15 * root.u)
                    }
                }

                // round "go" button
                Rectangle {
                    id: go
                    width: parent.height - 10
                    height: width
                    radius: width / 2
                    anchors.right: parent.right
                    anchors.rightMargin: 5
                    anchors.verticalCenter: parent.verticalCenter
                    color: goArea.containsMouse ? Qt.lighter(root.accent, 1.12) : root.accent
                    opacity: passInput.text.length > 0 || root.busy ? 1 : 0.35
                    Behavior on opacity { NumberAnimation { duration: 150 } }
                    Canvas {
                        anchors.fill: parent
                        onPaint: {
                            var c = getContext("2d");
                            c.reset();
                            var s = width;
                            c.strokeStyle = "#0f1a15";
                            c.lineWidth = Math.max(1.6, s * 0.075);
                            c.lineCap = "round";
                            c.lineJoin = "round";
                            c.beginPath();
                            c.moveTo(s * 0.30, s * 0.5); c.lineTo(s * 0.70, s * 0.5);
                            c.moveTo(s * 0.53, s * 0.33); c.lineTo(s * 0.70, s * 0.5); c.lineTo(s * 0.53, s * 0.67);
                            c.stroke();
                        }
                    }
                    MouseArea {
                        id: goArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.submit()
                    }
                }
            }

            // one line of feedback: wrong password, or Caps Lock
            Text {
                width: parent.width
                height: Math.round(18 * root.u)
                horizontalAlignment: Text.AlignHCenter
                text: root.notice.length > 0 ? root.notice : (keyboard.capsLock ? qsTr("Caps Lock is on") : "")
                color: root.notice.length > 0 ? "#f0a09a" : root.inkDim
                font.family: root.face
                font.pixelSize: Math.round(13 * root.u)
            }
        }
    }

    // ---- quiet corners -------------------------------------------------------------
    component Link: Text {
        id: link
        signal activated()
        property bool hovered: area.containsMouse
        color: hovered ? root.ink : root.inkDim
        font.family: root.face
        font.pixelSize: Math.round(13 * root.u)
        MouseArea {
            id: area
            anchors.fill: parent
            anchors.margins: -8
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: link.activated()
        }
    }

    Text {                                  // clock, top centre
        id: clock
        anchors.horizontalCenter: parent.horizontalCenter
        y: Math.round(34 * root.u)
        opacity: root.formOpacity * 0.9
        color: root.ink
        font.family: root.face
        font.pixelSize: Math.round(15 * root.u)
        font.weight: Font.Medium
        function tick() { text = Qt.formatDateTime(new Date(), "ddd, MMM d   HH:mm"); }
        Timer { interval: 15000; running: true; repeat: true; triggeredOnStart: true; onTriggered: clock.tick() }
    }

    Link {                                  // session, bottom left
        x: Math.round(40 * root.u)
        anchors.bottom: parent.bottom
        anchors.bottomMargin: Math.round(32 * root.u)
        opacity: root.formOpacity
        visible: root.sessions.length > 1
        text: root.sessions.length > root.sessionIndex ? root.sessions[root.sessionIndex].name : ""
        onActivated: root.sessionIndex = (root.sessionIndex + 1) % root.sessions.length
    }

    Row {                                   // power, bottom right
        anchors.right: parent.right
        anchors.rightMargin: Math.round(40 * root.u)
        anchors.bottom: parent.bottom
        anchors.bottomMargin: Math.round(32 * root.u)
        spacing: Math.round(28 * root.u)
        opacity: root.formOpacity
        Link { text: qsTr("Sleep"); visible: sddm.canSuspend; onActivated: sddm.suspend() }
        Link { text: qsTr("Restart"); visible: sddm.canReboot; onActivated: sddm.reboot() }
        Link { text: qsTr("Shut Down"); visible: sddm.canPowerOff; onActivated: sddm.powerOff() }
    }

    // fade to black on the way into the session
    Rectangle {
        id: curtain
        anchors.fill: parent
        color: "#0c0d0d"
        opacity: 0
        NumberAnimation { id: leave; target: curtain; property: "opacity"; to: 1; duration: 260 }
    }

    // any key or click skips the opening
    MouseArea {
        anchors.fill: parent
        enabled: intro.running
        onClicked: root.finishIntro()
    }
    Keys.onPressed: function (event) {
        if (intro.running) {
            root.finishIntro();
            // Someone who starts typing early should not lose the first character.
            if (event.text.length === 1 && event.text.charCodeAt(0) > 32 && !root.askName) {
                passInput.text += event.text;
            }
            event.accepted = true;
        }
    }
    focus: true

    Component.onCompleted: {
        Qt.callLater(pickDefaults);
        if (config.intro === "false") finishIntro();
        else intro.start();
    }
}
