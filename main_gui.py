from PyObjCTools import AppHelper
from Foundation import *
from Cocoa import *
from WebKit import *
import youtube_stream
import objc

class MyWKNavigationDelegate(NSObject):
    def webView_decidePolicyForNavigationAction_decisionHandler_(self, webview, navigationAction, decisionHandler):
        decisionHandler(WKNavigationActionPolicyAllow)
        
class AppDelegate(NSObject):
    window = objc.ivar()

    def __init__(self):
        self.window = None

    def applicationDidFinishLaunching_(self, aNotification):
        if self.window is None:
            # Existing code for window and webView setup goes here
            screenFrame = NSScreen.mainScreen().frame()

            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                screenFrame,
                NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable,
                NSBackingStoreBuffered,
                False
            )
            self.window.setTitle_("BlossomAndBloom")
            self.window.setBackgroundColor_(NSColor.blackColor())

            web_config = WKWebViewConfiguration.alloc().init()
            self.webView = WKWebView.alloc().initWithFrame_configuration_(screenFrame, web_config)
            self.webView.setCustomUserAgent_("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15")

            navigationDelegate = MyWKNavigationDelegate.alloc().init()
            self.webView.setNavigationDelegate_(navigationDelegate)

            request = NSURLRequest.requestWithURL_(NSURL.URLWithString_("https://www.canva.com/"))
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

            self.window.makeKeyAndOrderFront_(None)
        else:
            return        

    def toggleStream_(self, sender):
        if youtube_stream.is_streaming:
            youtube_stream.stop_stream()
            NSNotificationCenter.defaultCenter().postNotificationName_object_("StopStream", None)
            self.startStopButton.setTitle_("Start")
            self.statusTextField.setStringValue_("Stream stopped.")
        else:
            youtube_stream.start_stream()
            NSNotificationCenter.defaultCenter().postNotificationName_object_("StartStream", None)
            self.startStopButton.setTitle_("Stop")
            self.statusTextField.setStringValue_("Stream started.")

def run_main_gui():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()

if __name__ == "__main__":
    run_main_gui()
