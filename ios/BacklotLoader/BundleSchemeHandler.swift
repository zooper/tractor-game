import Foundation
import WebKit

/// Serves the game's files from the app bundle for `app://game/...` URLs, with proper content types,
/// so the page behaves as if it came from a web server (module scripts, fetch, HEAD requests, wasm).
final class BundleSchemeHandler: NSObject, WKURLSchemeHandler {
    private let root: URL

    init(root: URL) {
        self.root = root.standardizedFileURL
    }

    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        guard let url = task.request.url else {
            task.didFailWithError(URLError(.badURL))
            return
        }
        var path = url.path
        if path.isEmpty || path == "/" { path = "/index.html" }
        let file = root.appendingPathComponent(String(path.dropFirst())).standardizedFileURL

        // Only files inside the web folder, nothing else in the bundle.
        guard file.path.hasPrefix(root.path + "/"), let data = try? Data(contentsOf: file) else {
            respond(task, url: url, status: 404, type: "text/plain", data: Data("Not found".utf8))
            return
        }
        respond(task, url: url, status: 200, type: contentType(for: file.pathExtension), data: data)
    }

    func webView(_ webView: WKWebView, stop task: WKURLSchemeTask) {
        // Every response is sent in one go, so there is nothing to cancel.
    }

    private func respond(_ task: WKURLSchemeTask, url: URL, status: Int, type: String, data: Data) {
        let headers = [
            "Content-Type": type,
            "Content-Length": String(data.count),
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*",
        ]
        guard let response = HTTPURLResponse(url: url, statusCode: status, httpVersion: "HTTP/1.1", headerFields: headers) else {
            task.didFailWithError(URLError(.cannotParseResponse))
            return
        }
        task.didReceive(response)
        if task.request.httpMethod != "HEAD" { task.didReceive(data) }
        task.didFinish()
    }

    private func contentType(for ext: String) -> String {
        switch ext.lowercased() {
        case "html", "htm": return "text/html; charset=utf-8"
        case "js", "mjs": return "text/javascript; charset=utf-8"
        case "css": return "text/css; charset=utf-8"
        case "json": return "application/json"
        case "wasm": return "application/wasm"
        case "glb": return "model/gltf-binary"
        case "gltf": return "model/gltf+json"
        case "png": return "image/png"
        case "jpg", "jpeg": return "image/jpeg"
        case "webp": return "image/webp"
        case "svg": return "image/svg+xml"
        case "woff2": return "font/woff2"
        case "woff": return "font/woff"
        case "ttf": return "font/ttf"
        case "mp3": return "audio/mpeg"
        case "wav": return "audio/wav"
        default: return "application/octet-stream"
        }
    }
}
