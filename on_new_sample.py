import gi
import numpy as np
import cv2

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# GStreamer'ı başlat
Gst.init(None)

class VideoProcessing:
    def __init__(self, uri):
        self.uri = uri
        self.pipeline = Gst.Pipeline.new("video-pipeline")

        # Elemanları oluştur
        self.source = Gst.ElementFactory.make("souphttpsrc", "source")
        self.decodebin = Gst.ElementFactory.make("decodebin", "decoder")
        self.tee = Gst.ElementFactory.make("tee", "tee")
        self.appsink = Gst.ElementFactory.make("appsink", "sink")
        self.filesink = Gst.ElementFactory.make("filesink", "file_sink")

        # Queue elemanlarını oluştur
        self.queueCloud = Gst.ElementFactory.make("queue", "cloud")
        self.queueFile = Gst.ElementFactory.make("queue", "file")

        if not self.source or not self.decodebin or not self.tee or not self.appsink or not self.filesink or not self.queueCloud or not self.queueFile:
            print("Gerekli elemanlar oluşturulamadı.")
            return

        # URI'yi ayarla
        self.source.set_property("location", self.uri)

        # appsink ayarları
        self.appsink.set_property("emit-signals", True)
        self.appsink.set_property("sync", False)
        self.appsink.connect("new-sample", self.on_new_sample)

        # filesink ayarları
        self.filesink.set_property("location", "output.mp4")  # Kaydedilecek dosya adı
        self.filesink.set_property("sync", False)

        # Pipeline'a elemanları ekle
        self.pipeline.add(self.source)
        self.pipeline.add(self.decodebin)
        self.pipeline.add(self.tee)
        self.pipeline.add(self.appsink)
        self.pipeline.add(self.filesink)
        self.pipeline.add(self.queueCloud)
        self.pipeline.add(self.queueFile)

        # Bağlantıları kur
        self.source.link(self.decodebin)
        self.decodebin.connect("pad-added", self.on_pad_added)

    def on_pad_added(self, decodebin, pad):
        # Yeni pad eklenince çağrılır
        print("Pad added")

        # Tee'den pad iste
        tee_pad = self.tee.request_pad_simple("src_%u")  # Dinamik bir pad al
        if tee_pad:
            pad.link(tee_pad)

            # Queue'ları tee'ye bağlayalım
            tee_pad.link(self.queueCloud.get_static_pad("sink"))  # Queue için
            tee_pad.link(self.queueFile.get_static_pad("sink"))   # Queue için

            # Queue'dan appsink'e bağlama
            self.queueCloud.link(self.appsink)

            # Queue'dan filesink'e bağlama
            self.queueFile.link(self.filesink)

    def on_new_sample(self, sink):
        # Yeni frame geldiğinde çağrılır
        print("New sample")
        sample = sink.emit("pull-sample")
        buffer = sample.get_buffer()
        caps = sample.get_caps()
        width = caps.get_structure(0).get_value("width")
        height = caps.get_structure(0).get_value("height")

        # Frame'i numpy dizisine dönüştür
        frame_data = buffer.extract_dup(0, buffer.get_size())
        frame_array = np.frombuffer(frame_data, np.uint8).reshape((height, width, 3))

        # Frame üzerinde işlem yap (örneğin, gri tonlama)
        processed_frame = cv2.cvtColor(frame_array, cv2.COLOR_RGB2GRAY)

        # İşlenen frame'i göster
        cv2.imshow("Processed Frame", processed_frame)
        cv2.waitKey(1)

        return Gst.FlowReturn.OK

    def run(self):
        self.pipeline.set_state(Gst.State.PLAYING)

        # Ana döngü
        loop = GLib.MainLoop()
        try:
            loop.run()
        except KeyboardInterrupt:
            pass
        finally:
            self.pipeline.set_state(Gst.State.NULL)

if __name__ == '__main__':
    uri = "http://ip.localde.net:8080/sdk@test/Gd53ozwKPw/33837"  # Değiştirin
    video_processing = VideoProcessing(uri)
    video_processing.run()