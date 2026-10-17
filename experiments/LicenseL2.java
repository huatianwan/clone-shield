// L2 加固：校验搬服务端，class/dex 里没有秘密规则
public class LicenseL2 {
    public static boolean licenseValid(String key) {
        return remoteVerify(key);   // 真实产品里是 HTTPS 请求
    }
    static boolean remoteVerify(String key) {
        return "1".equals(System.getenv("SERVER_RESP"));  // 代表服务端返回
    }
    public static void main(String[] a) {
        System.out.println(a.length > 0 && licenseValid(a[0]) ? "VALID" : "INVALID");
    }
}
