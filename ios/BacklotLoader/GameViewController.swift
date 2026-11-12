import UIKit
import WebKit

/// Runs the web game full screen. The game's files are served from the app bundle over a private
/// `app://` scheme (see BundleSchemeHandler), so ES modules, fetch and WebAssembly work as on a web server.
final class GameViewController: UIViewController, WKNavigationDelegate, UIScrollViewDelegate {
    private var webView: WKWebView!
    private let startURL = URL(string: "app://game/index.html")!

    override func loadView() {
        let config = WKWebViewConfiguration()
        let webRoot = Bundle.main.resourceURL!.appendingPathComponent("web", isDirectory: true)
        config.setURLSchemeHandler(BundleSchemeHandler(root: webRoot), forURLScheme: "app")
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []
        // Tell the page it runs in the app (it switches to its full-screen app layout).
        let flag = WKUserScript(source: "window.__nativeApp = { platform: 'ios' };", injectionTime: .atDocumentStart, forMainFrameOnly: true)
        config.userContentController.addUserScript(flag)

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.isOpaque = false
        webView.backgroundColor = .black
        webView.scrollView.backgroundColor = .black
        // No scrolling, bouncing or zooming of the page: the game handles every touch itself.
        webView.scrollView.isScrollEnabled = false
        webView.scrollView.bounces = false
        webView.scrollView.minimumZoomScale = 1
        webView.scrollView.maximumZoomScale = 1
        webView.scrollView.pinchGestureRecognizer?.isEnabled = false
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.scrollView.delegate = self
        webView.allowsBackForwardNavigationGestures = false
        webView.allowsLinkPreview = false
        webView.navigationDelegate = self
        #if DEBUG
        // Safari > Develop > (your device) to inspect the game while it runs in the app.
        if #available(iOS 16.4, *) { webView.isInspectable = true }
        #endif
        self.webView = webView
        view = webView
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        webView.load(URLRequest(url: startURL))
    }

    // Full screen: no status bar, the home indicator fades, and edge swipes reach the game first.
    override var prefersStatusBarHidden: Bool { true }
    override var prefersHomeIndicatorAutoHidden: Bool { true }
    override var preferredScreenEdgesDeferringSystemGestures: UIRectEdge { .all }

    func viewForZooming(in scrollView: UIScrollView) -> UIView? { nil }

    // If iOS kills the web content process (memory pressure), start the game again.
    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        webView.load(URLRequest(url: startURL))
    }

    // Links out of the game (none today) open in Safari instead of replacing it.
    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if let url = navigationAction.request.url, url.scheme != "app", url.scheme != "about", navigationAction.navigationType == .linkActivated {
            UIApplication.shared.open(url)
            decisionHandler(.cancel)
            return
        }
        decisionHandler(.allow)
    }
}
