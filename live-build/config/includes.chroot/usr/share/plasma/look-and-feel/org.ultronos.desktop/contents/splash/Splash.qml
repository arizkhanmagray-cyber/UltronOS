// Ultron OS login splash: the mark, breathing, on black.
import QtQuick

Rectangle {
    id: root
    color: "#0c0d0d"
    property int stage

    onStageChanged: {
        if (stage === 1) {
            intro.running = true;
        }
    }

    Image {
        id: mark
        anchors.centerIn: parent
        readonly property int side: Math.round(Math.min(root.width, root.height) * 0.12)
        source: "images/ultron-mark.svg"
        width: side
        height: side
        sourceSize: Qt.size(side, side)
        opacity: 0
    }

    Rectangle {
        id: track
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: mark.bottom
        anchors.topMargin: mark.height * 0.45
        width: mark.width * 1.3
        height: 3
        radius: 1.5
        color: "#2a2d2c"
        opacity: mark.opacity

        Rectangle {
            height: parent.height
            radius: parent.radius
            color: "#86b39c"
            width: parent.width * Math.min(1, root.stage / 6)
            Behavior on width { NumberAnimation { duration: 350; easing.type: Easing.OutCubic } }
        }
    }

    OpacityAnimator {
        id: intro
        running: false
        target: mark
        from: 0
        to: 1
        duration: 600
        easing.type: Easing.OutCubic
    }
}
