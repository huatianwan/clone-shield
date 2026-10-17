using System;
// L2 加固：校验逻辑搬服务端，程序集里没有秘密规则
class Lic {
    static bool LicenseValid(string key) {
        // 真实产品里是 HttpClient POST 到服务端；这里用桩代表网络层
        return RemoteVerify(key);
    }
    static bool RemoteVerify(string key) {
        return Console.ReadLine() == "1";   // 代表服务端返回
    }
    static void Main(string[] a) {
        Console.WriteLine(a.Length > 0 && LicenseValid(a[0]) ? "VALID" : "INVALID");
    }
}
