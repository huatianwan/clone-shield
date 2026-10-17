#include <stdio.h>
#include <string.h>
/* 客户端原生核心：授权码校验（攻击者想抄的秘密规则） */
int license_valid(const char *key) {
    if (strncmp(key, "ACME-", 5) != 0) return 0;      /* 秘密前缀 */
    int sum = 0;
    for (const char *p = key; *p; p++)
        if (*p >= '0' && *p <= '9') sum += (*p - '0');
    return (sum % 97) == 13;                           /* 秘密规则 97/13 */
}
int main(int argc, char **argv) {
    if (argc < 2) { printf("usage: lic <key>\n"); return 2; }
    printf(license_valid(argv[1]) ? "VALID\n" : "INVALID\n");
    return 0;
}
