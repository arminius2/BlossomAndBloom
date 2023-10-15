from Cocoa import NSScreen, NSApplication, NSApp, NSWindow, NSButton, NSMakeRect, NSBackingStoreBuffered, NSURLRequest, NSURL
from WebKit import WKWebView

def run_main_gui():
    app = NSApplication.sharedApplication()

    # Get screen size
    screen = NSScreen.mainScreen()
    screen_rect = screen.frame()

    # Create window
    window = NSWindow.alloc()
    window.initWithContentRect_styleMask_backing_defer_(screen_rect, 15, NSBackingStoreBuffered, False)
    window.setTitle_("BlossomAndBloom")

    # Create and configure WebView
    webView = WKWebView.alloc().initWithFrame_(screen_rect)
    webView.loadRequest_(NSURLRequest.requestWithURL_(NSURL.URLWithString_("https://www.canva.com/design/DAFsgM9Xi3A/Hsku1dC2x83Us3gMe25DWw/view?utm_content=DAFsgM9Xi3A&utm_campaign=designshare&utm_medium=link&utm_source=publishsharelink")))

    # Add WebView to window
    window.contentView().addSubview_(webView)

    # Make the window fullscreen
    window.toggleFullScreen_(None)

    # ... add button, blinking circle, status text-field, etc. here

    window.makeKeyAndOrderFront_(None)

    app.run()

# Uncomment the below line if you want to run the GUI standalone
# run_main_gui()
