import sys
import gi
import objc  # PyObjC kütüphanesi
from PyObjCTools import AppHelper
from AppKit import NSApplication, NSApp, NSWindow, NSApplicationActivationPolicyRegular, NSBackingStoreBuffered, NSRect


# GStreamer modüllerini yükle
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# GStreamer başlatılır
Gst.init(None)
video_source_path = "/Users/sadikhanecioglu/Documents/Works/ImageProcess_Sl/prototip/models/video/input/fligran.mp4"  # Giriş videosunun yolu
output_stream_path = "/Users/sadikhanecioglu/Documents/Works/ImageProcess_Sl/prototip/models/video/output/filigran_removed.mp4"  # Çıkış videosunun yolu
# GStreamer ve NSApplication'ı entegre edecek sınıf
class GStreamerAppDelegate:
    def applicationDidFinishLaunching_(self, notification):
        # GStreamer pipeline'ını başlat
        self.pipeline = Gst.parse_launch(
            f'filesrc location={video_source_path} ! decodebin name=demuxer demuxer. ! queue ! videoconvert ! autovideosink '
            f'filesrc location={video_source_path} ! decodebin ! audioconvert ! autoaudiosink'
        )
        # Pipeline'ı çalıştır
        self.pipeline.set_state(Gst.State.PLAYING)

        # GStreamer bus mesajlarını kontrol et
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def on_message(self, bus, message):
        msg_type = message.type
        if msg_type == Gst.MessageType.EOS:
            print("End of stream")
            self.pipeline.set_state(Gst.State.NULL)
            NSApp.terminate_(self)
        elif msg_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err}, {debug}")
            self.pipeline.set_state(Gst.State.NULL)
            NSApp.terminate_(self)

# Ana uygulama başlatma fonksiyonu
def main():
    # NSApplication başlat
    app = NSApplication.sharedApplication()
    delegate = GStreamerAppDelegate()
    app.setDelegate_(delegate)
    
    # Pencere oluştur
    window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSRect(640, 480),
        15,  # styleMask (Resizable, Titled, etc.)
        NSBackingStoreBuffered,
        False
    )
    window.setTitle_("GStreamer macOS Application")
    window.makeKeyAndOrderFront_(None)
    app.setActivationPolicy_(NSApplicationActivationPolicyRegular)
    
    # Uygulamayı başlat
    AppHelper.runEventLoop()

# Uygulama başlatma
if __name__ == "__main__":
    main()