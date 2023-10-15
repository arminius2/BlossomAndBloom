from PyObjCTools import AppHelper
from Foundation import *
from Cocoa import *
from WebKit import *
import youtube_stream
import objc

class MyWKNavigationDelegate(NSObject):
    def webView_decidePolicyForNavigationAction_decisionHandler_(self, webview, navigationAction, decisionHandler):
        decisionHandler(WKNavigationActionPolicyAllow)

class MainWindowController(NSWindowController):
    delegate = objc.ivar()

    def loadWindow(self):
        screenFrame = NSScreen.mainScreen().frame()
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            screenFrame,
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable,
            NSBackingStoreBuffered,
            False
        )
        self.setWindow_(self.window)

    def windowDidLoad(self):
        screenFrame = self.window.frame()

        self.webView = WKWebView.alloc().initWithFrame_(screenFrame)
        self.webView.setNavigationDelegate_(MyWKNavigationDelegate.alloc().init())
        self.webView.setCustomUserAgent_("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15")
        request = NSURLRequest.requestWithURL_(NSURL.URLWithString_("https://www.canva.com/design/DAFsgM9Xi3A/Hsku1dC2x83Us3gMe25DWw/view?utm_content=DAFsgM9Xi3A&utm_campaign=designshare&utm_medium=link&utm_source=publishsharelink"))
        self.webView.loadRequest_(request)
        self.window.contentView().addSubview_(self.webView)

        self.startStopButton = NSButton.alloc().initWithFrame_(NSMakeRect(20, 20, 100, 40))
        self.startStopButton.setTitle_("Start")
        self.startStopButton.setTarget_(self)
        self.startStopButton.setAction_("toggleStream:")
        self.window.contentView().addSubview_(self.startStopButton)

        self.statusTextField = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, screenFrame.size.width, 20))
        self.statusTextField.setAlignment_(NSCenterTextAlignment)
        self.statusTextField.setBackgroundColor_(NSColor.blackColor())
        self.statusTextField.setTextColor_(NSColor.whiteColor())
        self.window.contentView().addSubview_(self.statusTextField)

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
    