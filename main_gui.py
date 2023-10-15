from PyObjCTools import AppHelper
from Foundation import *
from Cocoa import *
from WebKit import *
import youtube_stream
import objc
from objc import super

class MainWindowController(NSWindowController):
    webView = objc.ivar()
    startStopButton = objc.ivar()
    
    def awakeFromNib(self):
        window = self.window()
        screenFrame = window.contentView().bounds()
        self.webView = WKWebView.alloc().initWithFrame_(screenFrame)
        self.webView.setCustomUserAgent_("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15")
        request = NSURLRequest.requestWithURL_(NSURL.URLWithString_("https://www.canva.com/design/DAFsgM9Xi3A/Hsku1dC2x83Us3gMe25DWw/view?utm_content=DAFsgM9Xi3A&utm_campaign=designshare&utm_medium=link&utm_source=publishsharelink"))
        window.contentView().addSubview_(self.webView)
        self.webView.loadRequest_(request)

        self.startStopButton = NSButton.alloc().initWithFrame_(NSMakeRect(20, 20, 100, 40))
        self.startStopButton.setTitle_("Start")
        self.startStopButton.setTarget_(self)
        self.startStopButton.setAction_("toggleStream:")
        window.contentView().addSubview_(self.startStopButton)

        self.statusTextField = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, screenFrame.size.width, 20))
        self.statusTextField.setAlignment_(NSCenterTextAlignment)
        self.statusTextField.setBackgroundColor_(NSColor.clearColor())
        self.statusTextField.setTextColor_(NSColor.whiteColor())
        window.contentView().addSubview_(self.statusTextField)
    
    @objc.IBAction
    def toggleStream_(self, sender):
        if self.startStopButton.title() == "Start":
            youtube_stream.start_stream()
            self.startStopButton().setTitle_("Start")
            self.statusTextField().setStringValue_("Stream stopped.")
        else:
            youtube_stream.stop_stream()
            self.startStopButton().setTitle_("Stop")
            self.statusTextField().setStringValue_("Stream started.")

class AppDelegate(NSObject):
    mainWindowController = objc.ivar()
    window = objc.ivar()

    def applicationDidFinishLaunching_(self, aNotification):
        if self.window is None:
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                        NSScreen.mainScreen().frame(),
                        NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable,
                        NSBackingStoreBuffered,
                        False
                    )    
        if self.mainWindowController is None:
            self.mainWindowController = MainWindowController.alloc().initWithWindow_(self.window) 
            self.mainWindowController.awakeFromNib()
        self.mainWindowController.showWindow_(self)
        self.window.makeKeyAndOrderFront_(None)
        

def run_main_gui():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    
    AppHelper.runEventLoop()

if __name__ == "__main__":
    run_main_gui()
    