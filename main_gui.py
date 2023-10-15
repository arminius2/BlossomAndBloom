from PyObjCTools import AppHelper
from Cocoa import (NSApplication, NSApp, NSWindow, NSButton,
                   NSURLRequest, NSNotificationCenter, NSMakeRect, NSBackingStoreBuffered,
                   NSWindowStyleMaskTitled, NSWindowStyleMaskClosable, NSWindowStyleMaskResizable,
                   NSColor, NSTextField, NSCenterTextAlignment, NSScreen)
from Quartz import kCGColorRed
from AppKit import NSMainMenuWindowLevel
from Foundation import NSObject, NSLog
from WebKit import WKWebView, WKWebViewConfiguration
import youtube_stream
import objc

class AppDelegate(NSObject):

    def applicationDidFinishLaunching_(self, aNotification):
        screenFrame = NSScreen.mainScreen().frame()

        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            screenFrame,
            NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable,
            NSBackingStoreBuffered,
            False
        )
        self.window.setTitle_("BlossomAndBloom")
        self.window.setBackgroundColor_(NSColor.blackColor())
        self.window.setOpaque_(True)
        self.window.setHidesOnDeactivate_(True)
        self.window.setLevel_(NSMainMenuWindowLevel + 2)

        # Set up the WKWebView with custom user agent
        web_config = WKWebViewConfiguration.alloc().init()
        web_config.preferences.setValue_forKey_(True, "developerExtrasEnabled")
        self.webView = WKWebView.alloc().initWithFrame_configuration_(screenFrame, web_config)
        self.webView.setCustomUserAgent_("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15")

        request = NSURLRequest.requestWithURL_(NSURL.URLWithString_("https://www.canva.com/design/DAFsgM9Xi3A/Hsku1dC2x83Us3gMe25DWw/view?utm_content=DAFsgM9Xi3A&utm_campaign=designshare&utm_medium=link&utm_source=publishsharelink"))
        self.webView.loadRequest_(request)

        # Add the webView to the window
        self.window.contentView().addSubview_(self.webView)

        # Create the Start/Stop button
        self.startStopButton = NSButton.alloc().initWithFrame_(NSMakeRect(20, 20, 100, 40))
        self.startStopButton.setTitle_("Start")
        self.startStopButton.setTarget_(self)
        self.startStopButton.setAction_(self.toggleStream_)
        
        # Add the button to the window
        self.window.contentView().addSubview_(self.startStopButton)

        # Create the status text field
        self.statusTextField = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, screenFrame.size.width, 20))
        self.statusTextField.setAlignment_(NSCenterTextAlignment)
        self.statusTextField.setBackgroundColor_(NSColor.blackColor())
        self.statusTextField.setTextColor_(NSColor.whiteColor())
        
        # Add the status text field to the window
        self.window.contentView().addSubview_(self.statusTextField)
        
        # Show the window
        self.window.makeKeyAndOrderFront_(self.window)

    @objc.python_method
    def toggleStream_(self):
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
        
        # Add blinking red circle and other elements when the stream starts
        # (You can add code here or listen for the "StartStream" notification in another part of the code)

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()
