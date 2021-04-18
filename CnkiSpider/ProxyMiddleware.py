from CnkiSpider.proxy import ProxyManager


class CnkispiderSpiderProxyMiddleware:
    def process_request(self, request, spider):
        request.meta["proxy"] = ProxyManager.getProxyString()
        request.headers["Proxy-Authorization"] = ProxyManager.proxyAuth
        return None