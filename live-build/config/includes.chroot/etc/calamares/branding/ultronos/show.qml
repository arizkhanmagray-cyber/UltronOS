// Shown while files are being copied.
import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation {
    id: presentation

    Timer {
        interval: 9000
        running: presentation.activatedInCalamares
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    component Card : Slide {
        property string headline
        property string blurb
        Rectangle { anchors.fill: parent; color: "#141615" }
        Image {
            anchors.fill: parent
            source: "slide.jpg"
            fillMode: Image.PreserveAspectCrop
            opacity: 0.55
        }
        Column {
            anchors.centerIn: parent
            width: Math.min(parent.width * 0.78, 640)
            spacing: 14
            Image {
                source: "ultron-mark.png"
                width: 54; height: 54
                anchors.horizontalCenter: parent.horizontalCenter
            }
            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: headline
                color: "#ffffff"
                font.pixelSize: 26
                font.weight: Font.DemiBold
                wrapMode: Text.WordWrap
            }
            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: blurb
                color: "#cfd5d2"
                font.pixelSize: 15
                lineHeight: 1.3
                wrapMode: Text.WordWrap
            }
        }
    }

    Card {
        headline: qsTr("Installing Ultron OS")
        blurb: qsTr("Sit back. This takes about ten minutes on most computers, and you will not be asked anything else.")
    }
    Card {
        headline: qsTr("Everything in its place")
        blurb: qsTr("The bar at the top shows your workspaces, network, sound and battery. The dock at the bottom holds your apps. Click the U for everything else.")
    }
    Card {
        headline: qsTr("Thousands of apps")
        blurb: qsTr("Open Discover to install apps such as LibreOffice, Spotify, VS Code or Steam with one click. Updates for the system and your apps arrive in the same place.")
    }
    Card {
        headline: qsTr("Light on your hardware")
        blurb: qsTr("Tuned for everyday laptops with 8 GB of memory and four cores: compressed memory, no background indexing, nothing running that you did not ask for.")
    }

    function onActivate() { presentation.currentSlide = 0; }
    function onLeave() { }
}
