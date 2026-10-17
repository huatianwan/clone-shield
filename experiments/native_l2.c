#include <stdio.h>
#include <string.h>
/* L2 加固：校验逻辑在服务端，本地二进制里没有任何秘密规则。
   这里用 read_server_response() 代表"把 key 发给服务端、读回结果"的网络层。
   攻击者反编译这个 exe，找不到 ACME 前缀、找不到 97/13 规则——因为它们不在。 */
extern int read_server_response(const char *key); /* 由网络层实现，运行时才有 */

int license_valid(const char *key) {
    return read_server_response(key);   /* 只转发，不判断 */
}
/* 为可独立编译：弱桩，真实产品里替换成 HTTPS 请求 */
__attribute__((weak)) int read_server_response(const char *key) {
    int r = getchar();                  /* 代表服务端返回的布尔 */
    return r == '1';
}
int main(int argc, char **argv) {
    if (argc < 2) { printf("usage: lic <key>\n"); return 2; }
    printf(license_valid(argv[1]) ? "VALID\n" : "INVALID\n");
    return 0;
}
