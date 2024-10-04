import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import cv2
import numpy as np

# GStreamer başlatılır
Gst.init(None)
video_source_path = "/Users/sadikhanecioglu/Documents/Works/ImageProcess_Sl/prototip/models/video/input/fligran.mp4"  # Giriş videosunun yolu
def on_video_sample(sink, data):
    # Appsink'ten gelen video verisini (frame) buffer olarak al
    print("on_video_sample")
    sample = sink.emit("pull-sample")
    buffer = sample.get_buffer()
    
    # Buffer'dan gelen veriyi bir numpy array olarak al
    success, map_info = buffer.map(Gst.MapFlags.READ)
    if success:
        # Video çerçevesini numpy dizisine dönüştürme (BGR formatında)
        frame = np.frombuffer(map_info.data, dtype=np.uint8)
        frame = frame.reshape((480, 640, 3))  # Video çözünürlüğünü pipeline'daki `caps` ile aynı yapın
        buffer.unmap(map_info)
        
        # OpenCV kullanarak frame üzerinde işlemler yapabilirsiniz (örneğin, görüntüyü siyah beyaz yapma)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Processed Frame", gray_frame)
        cv2.waitKey(1)

    return Gst.FlowReturn.OK

# Pipeline tanımı: Video ve ses akışlarını ayrı ayrı işler
pipeline_description = f"""
    uridecodebin uri=file://{video_source_path} name=demuxer
    demuxer. ! videoconvert ! video/x-raw,format=BGR ! appsink name=video_sink sync=false
    demuxer. ! queue ! audioconvert ! audioresample ! autoaudiosink sync=false
"""

# Pipeline oluşturulur
pipeline = Gst.parse_launch(pipeline_description)

# Appsink elementine ulaşma
video_sink = pipeline.get_by_name("video_sink")

# Appsink'ten gelen veriyi (sample) almak için sinyali bağla
video_sink.connect("new-sample", on_video_sample, None)

# Pipeline çalıştırılır
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