class JSHooker:
    """Layer 3: Instrumenting JS Sinks (eval, innerHTML, etc.) using Playwright."""
    def __init__(self):
        self.script = """
        (function() {
            const sinks = ['eval', 'setTimeout', 'setInterval', 'Function', 'innerHTML', 'outerHTML', 'insertAdjacentHTML', 'document.write', 'document.writeln', 'src', 'href'];
            const originalSinks = {};

            sinks.forEach(sink => {
                if (sink in window) {
                    originalSinks[sink] = window[sink];
                    window[sink] = function(...args) {
                        console.log(`[XStriker-Hook] Sink: ${sink}, Args: ${JSON.stringify(args)}`);
                        return originalSinks[sink].apply(this, args);
                    };
                }
            });

            // Special handling for Element.innerHTML setter
            const originalInnerHTML = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML').set;
            Object.defineProperty(Element.prototype, 'innerHTML', {
                set: function(val) {
                    console.log(`[XStriker-Hook] Sink: innerHTML, Value: ${val}`);
                    return originalInnerHTML.call(this, val);
                }
            });

            console.log("[XStriker-Hook] Sinks instrumentation complete.");
        })();
        """

    def get_hook_script(self):
        return self.script

if __name__ == "__main__":
    hooker = JSHooker()
    print(hooker.get_hook_script())
