from PyObjCTools import AppHelper
from Foundation import *
from Cocoa import *
from WebKit import *
import youtube_stream
import objc

# Create a delegate protocol for the MainWindowController
MainWindowControllerDelegate = objc.informal_protocol(
    "MainWindowControllerDelegate",
    [
        objc.selector(None, selector="startStream", signature="v@:"),
        objc.selector(None, selector="stopStream", signature="v@:"),
    ]
)

class MyWKNavigationDelegate(NSObject):
    def webView_decidePolicyForNavigationAction_decisionHandler_(self, webview, navigationAction, decisionHandler):
        print("Navigation action:", navigationAction)
        decisionHandler(WKNavigationActionPolicyAllow)

class MainWindowController(NSWindowController):
    delegate = objc.ivar(type=objc_id)

    def loadWindow(self):
        screenFrame = NSScreen.mainScreen().frame()
        self._window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            screenFrame,
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable,
            NSBackingStoreBuffered,
            False
        )
        self.setWindow_(self._window)

    def windowDidLoad(self):
        screenFrame = self.window().frame()

        self.webView = WKWebView.alloc().initWithFrame_(screenFrame)
        self.webView.setNavigationDelegate_(MyWKNavigationDelegate.alloc().init())
        request = NSURLRequest.requestWithURL_(NSURL.URLWithString_("https://www.canva.com/"))
        self.webView.loadRequest_(request)
        self.window().contentView().addSubview_(self.webView)

        self.startStopButton = NSButton.alloc().initWithFrame_(NSMakeRect(20, 20, 100, 40))
        self.startStopButton.setTitle_("Start")
        self.startStopButton.setTarget_(self)
        self.startStopButton.setAction_("toggleStream:")
        self.window().contentView().addSubview_(self.startStopButton)

        self.statusTextField = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, screenFrame.size.width, 20))
        self.statusTextField.setAlignment_(NSCenterTextAlignment)
        self.statusTextField.setBackgroundColor_(NSColor.blackColor())
        self.statusTextField.setTextColor_(NSColor.whiteColor())
        self.window().contentView().addSubview_(self.statusTextField)

    def toggleStream_(self, sender):
        if self.startStopButton.title() == "Start":
            self.delegate.startStream()
        else:
            self.delegate.stopStream()

class AppDelegate(NSObject):
    mainWindowController = objc.ivar()

    def applicationDidFinishLaunching_(self, aNotification):
        if self.mainWindowController is None:
            self.mainWindowController = MainWindowController.alloc().init()
            self.mainWindowController.setDelegate_(self)
        self.mainWindowController.showWindow_(self)

    def startStream(self):
        youtube_stream.start_stream()
        self.mainWindowController.startStopButton().setTitle_("Stop")
        self.mainWindowController.statusTextField().setStringValue_("Stream started.")

    def stopStream(self):
        youtube_stream.stop_stream()
        self.mainWindowController.startStopButton().setTitle_("Start")
        self.mainWindowController.statusTextField().setStringValue_("Stream stopped.")

def run_main_gui():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()

if __name__ == "__main__":
    run_main_gui()
