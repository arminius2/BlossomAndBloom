import objc
from Cocoa import NSApplication, NSApp, NSWindow, NSWindowController, NSRect, NSScreen, NSStatusWindowLevel, NSBorderlessWindowMask, NSColor
from WebKit import WKWebView, NSURL, NSURLRequest
import WebKit

class BorderlessWindow(NSWindow):
    def initWithContentRect_styleMask_backing_defer_(self, contentRect, styleMask, backing, defer):
        # Initialize with no style masks for a borderless window
        super(BorderlessWindow, self).initWithContentRect_styleMask_backing_defer_(
            contentRect, NSBorderlessWindowMask, backing, defer
        )
        self.setOpaque_(False)
        self.setBackgroundColor_(NSColor.clearColor())
        self.setLevel_(NSStatusWindowLevel)  # Make it stay on top of all other windows
        return self

class StreamingWindowController(NSWindowController):
    def loadRequest_(self, url):
        request = NSURLRequest.requestWithURL_(NSURL.URLWithString_(url))
        webView = WKWebView.alloc().initWithFrame_(self.window().frame())
        self.window().setContentView_(webView)
        webView.loadRequest_(request)

class StreamingAppController:
    def __init__(self, url):
        self.url = url
        self.app = NSApplication.sharedApplication()
        self.window_controller = None

    def createWindow(self):
        # Create the window
        screen = NSScreen.mainScreen()
        screen_frame = screen.frame()
        window_frame = NSRect((0, 0), (screen_frame.size.width, screen_frame.size.height))
        window = BorderlessWindow.alloc().initWithContentRect_styleMask_backing_defer_(window_frame, 0, 2, False)
        
        # Create the window controller
        self.window_controller = StreamingWindowController.alloc().initWithWindow_(window)
        self.window_controller.loadRequest_(self.url)
        
        # Show the window and bring it to the front
        self.window_controller.showWindow_(self.window_controller)
        self.window_controller.window().makeKeyAndOrderFront_(None)

    def run(self):
        self.createWindow()
        self.app.run()

    def tearDownWindow(self):
        if self.window_controller:
            self.window_controller.close()
            self.window_controller = None

    def rebuildWindow(self):
        self.tearDownWindow()
        self.createWindow()
