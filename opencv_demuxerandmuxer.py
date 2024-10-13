import cv2
import gi
import sys
import numpy as np

gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
from gi.repository import Gst, GLib, GObject

# GStreamer başlat
Gst.init(None)

class VideoProcessor:
    def __init__(self, input_video, output_video):
        self.input_video = input_video
        self.output_video = output_video
        self.pipeline = None

        # GStreamer pipeline oluştur
        self.create_pipeline()

    def create_pipeline(self):
        # Pipeline elemanlarını oluştur
        self.pipeline = Gst.Pipeline.new("video-audio-processor")

        # Elemanları tanımla
        source = Gst.ElementFactory.make("souphttpsrc", "source")
        decodebin = Gst.ElementFactory.make("decodebin", "decoder")
        videoconverter = Gst.ELEMENT_FACTORY_make("videoconvert", "converter")

        demuxer = Gst.ElementFactory.make("qtdemux", "demuxer")
        video_decoder = Gst.ElementFactory.make("h264parse", "video-decoder")
        audio_decoder = Gst.ElementFactory.make("aacparse", "audio-decoder")
        video_sink = Gst.ElementFactory.make("appsink", "video_sink")
        audio_sink = Gst.ElementFactory.make("appsink", "audio_sink")
        video_encoder = Gst.ElementFactory.make("x264enc", "video-encoder")
        audio_encoder = Gst.ElementFactory.make("avenc_aac", "audio-encoder")
        muxer = Gst.ElementFactory.make("mp4mux", "muxer")
        sink = Gst.ElementFactory.make("filesink", "output_sink")

        if not all([source, demuxer, video_decoder, audio_decoder, video_sink, audio_sink, video_encoder, audio_encoder, muxer, sink]):
            print("Gerekli GStreamer elemanları oluşturulamadı.")
            sys.exit(1)

        # Elemanları ayarla
        source.set_property("location", self.input_video)
        sink.set_property("location", self.output_video)
        sink.set_property("sync", False)

        # Pipeline'a elemanları ekle
        self.pipeline.add(source)
        self.pipeline.add(decodebin)
        self.pipeline.add(videoconverter)
        self.pipeline.add(audio_decoder)
        self.pipeline.add(video_sink)
        self.pipeline.add(audio_sink)
        self.pipeline.add(video_encoder)
        self.pipeline.add(audio_encoder)
        self.pipeline.add(muxer)
        self.pipeline.add(sink)

        # Elemanları bağla
        source.link(demuxer)
        demuxer.connect("pad-added", self.on_pad_added, video_decoder, audio_decoder)
        video_encoder.link(muxer)
        audio_encoder.link(muxer)
        muxer.link(sink)

        # Appsink ayarları
        video_sink.set_property("emit-signals", True)
        video_sink.set_property("sync", False)
        video_sink.connect("new-sample", self.process_frame)

    def on_pad_added(self, src, pad, video_decoder, audio_decoder):
        if pad.get_name().startswith("video"):
            pad.link(video_decoder.get_static_pad("sink"))
        elif pad.get_name().startswith("audio"):
            pad.link(audio_decoder.get_static_pad("sink"))

    def process_frame(self, sink):
        print("process_frame")
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        width = caps.get_structure(0).get_value("width")
        height = caps.get_structure(0).get_value("height")

        # G/Ç çerçevesini numpy dizisine dönüştür
        frame_data = buf.extract_dup(0, buf.get_size())
        frame_array = np.frombuffer(frame_data, np.uint8).reshape((height, width, 3))

        # Burada çerçeve işleme yapılır (örneğin, gri tonlamaya çevirme)
        frame_array = cv2.cvtColor(frame_array, cv2.COLOR_RGB2GRAY)

        # İşlenen çerçeveyi geri gönder
        # İşlenmiş çerçeveyi yeniden belirli bir formatta encode etmeniz gerekir
        # Bu örnekte doğrudan geri gönderilmemiştir.
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

if __name__ == "__main__":

    input_video_path = "https://gstreamer.freedesktop.org/data/media/sintel_trailer-480p.webm"
    output_video_path = "/Users/sadikhanecioglu/Documents/Works/ImageProcess_Sl/output/test1/a1.mp4"

    processor = VideoProcessor(input_video_path, output_video_path)
    processor.run()