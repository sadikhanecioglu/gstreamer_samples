from AppKit import NSApplication, NSWindow, NSApp

app = NSApplication.sharedApplication()
app.setActivationPolicy_(2)  # 2 = NSApplicationActivationPolicyRegular

# Pencere oluşturma
window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
    ((100, 100), (600, 400)),  # Pencere boyutları
    15,  # Stil maskesi
    2,   # NSBackingStoreBuffered
    False
)
window.setTitle_("AppKit GStreamer Window")
window.makeKeyAndOrderFront_(None)