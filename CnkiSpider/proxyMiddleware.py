from CnkiSpider.proxy import ApeProxyManager


class CnkispiderSpiderProxyMiddleware:
    def process_request(self, request, spider):
        # request.meta["proxy"] = ApeProxyManager.getProxyString()
        request.headers["Proxy-Authorization"] = ApeProxyManager.proxyAuth
        # print(ApeProxyManager.proxyAuth)
        # print('使用了代理中间件')
        return None