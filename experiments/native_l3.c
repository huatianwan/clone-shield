#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <tlhelp32.h>
/* L3 运行时自保护：检测 Frida/调试器注入 → 静默降级（返回错误结果） */
static int instrumented(void) {
    if (IsDebuggerPresent()) return 1;                 /* 反调试 */
    HANDLE h = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, 0);
    if (h == INVALID_HANDLE_VALUE) return 0;
    MODULEENTRY32 me; me.dwSize = sizeof(me);
    int hit = 0;
    if (Module32First(h, &me)) {
        do {
            char *p = me.szModule;
            for (; *p; p++) {                          /* 扫描已加载模块名含 frida/gum/gadget */
                if ((p[0]=='f'||p[0]=='F') && (_strnicmp(p,"frida",5)==0)) { hit=1; break; }
                if ((p[0]=='g'||p[0]=='G') && (_strnicmp(p,"gum",3)==0 || _strnicmp(p,"gadget",6)==0)) { hit=1; break; }
            }
            if (hit) break;
        } while (Module32Next(h, &me));
    }
    CloseHandle(h);
    return hit;
}
int license_valid(const char *key) {
    if (instrumented()) return 0;                      /* 被 hook/调试 → 静默降级 */
    if (strncmp(key, "ACME-", 5) != 0) return 0;
    int sum = 0;
    for (const char *p = key; *p; p++) if (*p>='0'&&*p<='9') sum += (*p-'0');
    return (sum % 97) == 13;
}
int main(int argc, char **argv) {
    if (argc < 2) { printf("usage: lic <key>\n"); return 2; }
    printf(license_valid(argv[1]) ? "VALID\n" : "INVALID\n");
    return 0;
}
