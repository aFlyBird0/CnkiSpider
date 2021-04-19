from CnkiSpider.proxy import ApeProxyManager


class CnkispiderSpiderProxyMiddleware:
    def process_request(self, request, spider):
        request.meta["proxy"] = ApeProxyManager.getProxyString()
        request.headers["Proxy-Authorization"] = ApeProxyManager.proxyAuth
        return None