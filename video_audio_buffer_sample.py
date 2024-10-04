import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GObject
import cv2
import numpy as np

# GStreamer başlatılır
Gst.init(None)

# Video ve ses verilerini almak için kullanılan callback fonksiyonları
def on_video_sample(sink, data):
    # Appsink'ten gelen video verisini (frame) buffer olarak al
    sample = sink.emit("pull-sample")
    buffer = sample.get_buffer()

    # Buffer'dan gelen veriyi bir numpy array olarak al
    success, map_info = buffer.map(Gst.MapFlags.READ)
    if success:
        # Video çerçevesini numpy dizisine dönüştürme (RGB formatında)
        frame = np.frombuffer(map_info.data, dtype=np.uint8)
        frame = frame.reshape((480, 640, 3))  # Video çözünürlüğüne göre ayarlayın
        buffer.unmap(map_info)

        # OpenCV ile frame üzerinde işlemler yapabilirsiniz
        cv2.imshow("Frame", frame)
        cv2.waitKey(1)
    return Gst.FlowReturn.OK

def on_audio_sample(sink, data):
    # Appsink'ten gelen ses verisini buffer olarak al
    sample = sink.emit("pull-sample")
    buffer = sample.get_buffer()

    # Buffer'dan gelen veriyi bir numpy array olarak al
    success, map_info = buffer.map(Gst.MapFlags.READ)
    if success:
        # Ses örneklerini numpy dizisine dönüştürme (float32 formatında)
        audio_sample = np.frombuffer(map_info.data, dtype=np.float32)
        buffer.unmap(map_info)

        # Ses verisi üzerinde işlem yapabilirsiniz (Örneğin: FFT, filtreleme)
        print(f"Audio sample: {audio_sample[:10]}")  # İlk 10 değeri yazdırma
    return Gst.FlowReturn.OK

# Pipeline tanımı
pipeline_description = """
    uridecodebin uri=file:///path/to/your/video.mp4 name=demuxer
    demuxer. ! videoconvert ! video/x-raw,format=RGB ! appsink name=video_sink sync=false
    demuxer. ! audioconvert ! audioresample ! audio/x-raw,format=F32LE,channels=1 ! appsink name=audio_sink sync=false
"""

# Pipeline'ı oluştur
pipeline = Gst.parse_launch(pipeline_description)

# Appsink elementlerine ulaşma
video_sink = pipeline.get_by_name("video_sink")
audio_sink = pipeline.get_by_name("audio_sink")

# Appsink'ten gelen veriyi (sample) almak için sinyalleri bağla
video_sink.connect("new-sample", on_video_sample, None)
audio_sink.connect("new-sample", on_audio_sample, None)

# Pipeline'ı çalıştır
pipeline.set_state(Gst.State.PLAYING)

# GStreamer event loop oluşturma
loop = GLib.MainLoop()
try:
    loop.run()
except KeyboardInterrupt:
    pass

# Pipeline durdurulur ve kaynaklar serbest bırakılır
pipeline.set_state(Gst.State.NULL)
cv2.destroyAllWindows()