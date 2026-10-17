// Android/Java 客户端核心：授权校验（REA/reverse-skill 用 JADX 反编译就能看到）
public class License {
    public static boolean licenseValid(String key) {
        if (!key.startsWith("ACME-")) return false;      // 秘密前缀
        int sum = 0;
        for (char c : key.toCharArray())
            if (c >= '0' && c <= '9') sum += (c - '0');
        return (sum % 97) == 13;                           // 秘密规则
    }
    public static void main(String[] a) {
        System.out.println(a.length > 0 && licenseValid(a[0]) ? "VALID" : "INVALID");
    }
}
