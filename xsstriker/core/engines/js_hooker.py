class JSHooker:
    """Layer 3: Advanced Instrumentation of JS Sinks using Playwright."""
    def __init__(self):
        self.script = """
        (function() {
            const sinks = [
                'eval', 'setTimeout', 'setInterval', 'Function',
                'document.write', 'document.writeln', 'setImmediate',
                'execScript', 'crypto.generateCRMFRequest'
            ];
            const originalSinks = {};

            sinks.forEach(sink => {
                const parts = sink.split('.');
                let parent = window;
                const name = parts[parts.length - 1];

                for (let i = 0; i < parts.length - 1; i++) {
                    parent = parent[parts[i]];
                }

                if (parent && parent[name]) {
                    originalSinks[sink] = parent[name];
                    parent[name] = function(...args) {
                        console.log(`[XStriker-Hook] Sink: ${sink}, Args: ${JSON.stringify(args)}`);
                        try {
                            const stack = new Error().stack;
                            console.log(`[XStriker-Hook] Trace: ${stack}`);
                        } catch (e) {}
                        return originalSinks[sink].apply(this, args);
                    };
                }
            });

            // Monitoring Property Setters (innerHTML, outerHTML, src, href, etc.)
            const propertySinks = [
                { obj: Element.prototype, prop: 'innerHTML' },
                { obj: Element.prototype, prop: 'outerHTML' },
                { obj: Element.prototype, prop: 'src' },
                { obj: HTMLScriptElement.prototype, prop: 'src' },
                { obj: HTMLIFrameElement.prototype, prop: 'src' },
                { obj: Location.prototype, prop: 'href' },
                { obj: Element.prototype, prop: 'insertAdjacentHTML' }
            ];

            propertySinks.forEach(s => {
                try {
                    const descriptor = Object.getOwnPropertyDescriptor(s.obj, s.prop);
                    if (descriptor && descriptor.set) {
                        const originalSet = descriptor.set;
                        Object.defineProperty(s.obj, s.prop, {
                            set: function(val) {
                                console.log(`[XStriker-Hook] Sink Property: ${s.prop}, Value: ${val}`);
                                try {
                                    const stack = new Error().stack;
                                    console.log(`[XStriker-Hook] Trace: ${stack}`);
                                } catch (e) {}
                                return originalSet.call(this, val);
                            }
                        });
                    }
                } catch (e) {}
            });

            console.log("[XStriker-Hook] Sinks instrumentation complete (v2.1).");
        })();
        """

    def get_hook_script(self):
        return self.script

if __name__ == "__main__":
    hooker = JSHooker()
    # print(hooker.get_hook_script())
