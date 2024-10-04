import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

video_source_path = "/Users/sadikhanecioglu/Documents/Works/ImageProcess_Sl/prototip/models/video/input/fligran.mp4"  # Giriş videosunun yolu
output_stream_path = "/Users/sadikhanecioglu/Documents/Works/ImageProcess_Sl/prototip/models/video/output/filigran_removed.mp4"  # Çıkış videosunun yolu


# GStreamer başlatılır
Gst.init(None)

# Pipeline oluşturulur
pipeline = Gst.parse_launch(
    f'filesrc location={video_source_path} ! decodebin name=demuxer demuxer. ! queue ! videoconvert ! autovideosink '
    f'filesrc location={video_source_path} ! decodebin ! audioconvert ! autoaudiosink'
)

# Pipeline çalıştırılır
pipeline.set_state(Gst.State.PLAYING)

# Hata yakalamak için bir bus oluşturulur
bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)

# Pipeline durdurulur ve kaynaklar serbest bırakılır
pipeline.set_state(Gst.State.NULL)