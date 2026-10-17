using System;
// .NET 客户端核心：授权校验（REA 静态读 CIL 就能看到）
class Lic {
    static bool LicenseValid(string key) {
        if (!key.StartsWith("ACME-")) return false;   // 秘密前缀
        int sum = 0;
        foreach (char c in key) if (c >= '0' && c <= '9') sum += (c - '0');
        return (sum % 97) == 13;                        // 秘密规则
    }
    static void Main(string[] a) {
        Console.WriteLine(a.Length > 0 && LicenseValid(a[0]) ? "VALID" : "INVALID");
    }
}
