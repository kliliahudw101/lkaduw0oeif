import httpx
import asyncio
import time
from utils.logger import log_error, log_info

class VelocityFuzz:
    """System 2: High-Speed Asynchronous Fuzzing (VelocityFuzz)"""
    def __init__(self, concurrency=20, timeout=10, headers=None):
        self.concurrency = concurrency
        self.timeout = timeout
        self.headers = headers if headers else {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.results = []

    async def _fuzz_task(self, client, url, method, param, payload):
        """Worker task for fuzzing a single payload."""
        try:
            # Build URL or Data based on method
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            query[param] = [payload]
            new_query = urlencode(query, doseq=True)
            target_url = urlunparse(parsed._replace(query=new_query))

            if method.lower() == "get":
                response = await client.get(target_url, timeout=self.timeout)
            else:
                response = await client.post(url, data={param: payload}, timeout=self.timeout)

            # Analyze response for reflection (ffuf-style matching)
            if payload in response.text:
                 self.results.append({
                     "url": url,
                     "method": method,
                     "param": param,
                     "payload": payload,
                     "status": response.status_code,
                     "length": len(response.text)
                 })
                 return True
            return False

        except Exception as e:
            log_error(f"VelocityFuzz Task Error: {e}")
            return False

    async def fuzz(self, vectors, payloads):
        """Main entry point for high-speed fuzzing."""
        self.results = []
        tasks = []

        print(f"[*] VelocityFuzz started: {len(vectors)} vectors x {len(payloads)} payloads.")
        start_time = time.time()

        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            # Create tasks for all combinations
            for vector in vectors:
                for payload in payloads:
                    tasks.append(self._fuzz_task(client, vector['url'], vector['method'], vector['param'], payload))

            # Execute with concurrency control
            sem = asyncio.Semaphore(self.concurrency)
            async def sem_task(task):
                async with sem:
                    return await task

            await asyncio.gather(*(sem_task(t) for t in tasks))

        elapsed = time.time() - start_time
        print(f"[+] VelocityFuzz complete: {len(self.results)} potential reflections found in {elapsed:.2f}s.")
        return self.results

if __name__ == "__main__":
    fuzzer = VelocityFuzz(concurrency=5)
    # vectors = [{"url": "http://example.com", "method": "GET", "param": "q"}]
    # payloads = ["<script>alert(1)</script>", "XSS"]
    # asyncio.run(fuzzer.fuzz(vectors, payloads))
